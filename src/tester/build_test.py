"""
If a DSL uses third-party libraries, we will generate a mock jar package for it.
Notably, properties like function and field should also be mocked.
"""

import subprocess, os, shutil, re
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from src.prompts import PROMPTS
from src.utils._logger import logger
from src.utils.config import KIRIN_JAVA_HOME
from src.mocker.mock_lib_llm import MockLibGenLLM
from src.mocker.mock_lib_ts import MockLibGenTS
from src.utils._llm import LLMWrapper
from src.tester.gen_test import fix_syntax_error
from src.tester.edit_test import TestEditor
from src.tester.manage_test import extract_main_class
from src.utils._helper import create_dir_with_path, parse_lib_code


class TestCompiler:
    """
    This class is used to compile the test cases for the given DSL ID.
    For third-party dependency, it will generate a mock jar package and compile the test cases.
    """

    def __init__(self, dsl_id: str, test_dir: Path = None, checker_dsl: str = ""):
        self.dsl_id = dsl_id
        self.dsl_ws_dir = Path(f"kirin_ws/{dsl_id}")

        self.test_dir = test_dir if test_dir else self.dsl_ws_dir / "test"
        assert self.test_dir.is_dir(), f"--> Test dirpath {self.test_dir} does not exists!"

        self.checker_dsl = checker_dsl
        if not checker_dsl:
            default_dsl_path = self.dsl_ws_dir / "dsl/DSL_ORI.kirin"
            logger.info(f"No checker provided, using default {default_dsl_path} for tests in {self.test_dir}.")
            self.checker_dsl = default_dsl_path.read_text(encoding="utf-8")

        self.test_abspath_list: list[str] = [str(test_file.absolute()) for test_file in self.test_dir.rglob("*.java")]
        if len(self.test_abspath_list) == 0:
            logger.error(f"--> No test cases are found in {self.test_dir}!")
            raise AssertionError(f"--> No test cases are found in {self.test_dir}!")

        # preload paths(not created)
        self.lib_dir = self.dsl_ws_dir / "lib"
        self.mock_tmp_dir = self.dsl_ws_dir / "_mock_tmp"
        self.mock_jar_file = self.lib_dir / "mock.jar"
        self.target_dir = self.dsl_ws_dir / "target"

        # cmd executable
        self.javac_executable = os.path.join(KIRIN_JAVA_HOME, "bin", "javac")
        self.jar_executable = os.path.join(KIRIN_JAVA_HOME, "bin", "jar")
        if os.name == "nt":
            self.javac_executable += ".exe"
            self.jar_executable += ".exe"

        # third-party lib related (all identified by tree-sitter)
        self.need_third_party_lib: bool = self.lib_dir.is_dir()

        self.failed_tests: list[str] = []  # to store the failed test absolute paths

    def compile_lib_code(self) -> tuple[bool, str]:
        """
        Compile the mock lib code and generate a jar package.
        Read mock lib code from self.mock_tmp_dir and write the jar package to self.mock_jar_file.
        :return: (status, error_msg)
        """
        assert self.mock_tmp_dir.is_dir(), f"--> Mock tmp dirpath for lib code {self.lib_dir} does not exists!"
        # create the lib dir if not exists
        self.lib_dir.mkdir(parents=True, exist_ok=True)
        try:
            # compile
            lib_filepaths = list(self.mock_tmp_dir.rglob("*.java"))
            lib_filepaths_str = [str(lib_file) for lib_file in lib_filepaths]
            javac_res = subprocess.run(
                [self.javac_executable, "-encoding", "utf-8", "-nowarn", "-d", str(self.mock_tmp_dir)]
                + lib_filepaths_str,
                capture_output=True,
                text=True,
                check=True,
                env={"LANG": "C"},
            )
            logger.debug(f"Javac result: \n{javac_res.stdout}")

            # package
            jar_res = subprocess.run(
                [self.jar_executable, "cvf", str(self.mock_jar_file), "-C", str(self.mock_tmp_dir), "."],
                capture_output=True,
                text=True,
                check=True,
                env={"LANG": "C"},
            )
            logger.debug(f"Jar result: \n{jar_res.stdout}")

            logger.info(f"Successfully build mock JAR at {self.mock_jar_file}")
            return True, ""
        except subprocess.CalledProcessError as e:
            logger.warning(f"--> Failed to build mock JAR for {self.dsl_id}: \n{e}")
            logger.warning(f"Std error: \n{e.stderr}")
            return False, str(e.stderr)

    def _compile_single_file(self, java_file: str) -> tuple[str, bool, str]:
        """
        Compile a single Java file.
        :param java_file: Path to the Java file to compile
        :return: (file_path, success, error_message)
        """
        cmd_list = [
            self.javac_executable,
            "-Xmaxerrs",
            "1000",
            "-encoding",
            "utf-8",
            "-nowarn",
            "-d",
            str(self.target_dir),
        ]
        if self.mock_jar_file.is_file():
            cmd_list += ["-cp", str(self.mock_jar_file)]
        cmd_list.append(java_file)
        env = {"LANG": "C"}

        try:
            result = subprocess.run(cmd_list, capture_output=True, text=True, check=False, env=env)
            if result.returncode == 0:
                return java_file, True, ""
            else:
                return java_file, False, result.stderr
        except Exception as e:
            return java_file, False, str(e)

    def compile_test_code(self, clear_targets: bool = True) -> tuple[bool, dict[str, str]]:
        """
        Compile the test cases. Before compilation, the mock jar lib will also be genrated and installed.
        Read test cases from test_dir (lib from lib_dir) and write the compiled class files to target_dir.
        :param clear_targets: Whether to clear the target directory after compilation.
        :return: (status, error_map)
        """
        # Compile the test cases
        logger.info(
            f"Compiling tests {'with' if self.mock_jar_file.is_file() else 'without '} mock lib for {self.test_dir}..."
        )
        create_dir_with_path(self.target_dir, cleanup=True)
        compile_ws_dir = Path("kirin_ws/tmp/test")
        create_dir_with_path(compile_ws_dir, cleanup=True)

        # move all test files to kirin_ws/tmp/test, get the file mapping
        compile_test_abspath_list = []
        compile_ori_test_map = dict()
        for test_abspath in self.test_abspath_list:
            test_file = Path(test_abspath)
            assert test_file.is_file(), f"--> Test file {test_file} does not exist!"
            # create the target directory structure
            compile_file_dir = compile_ws_dir / test_file.stem
            compile_file_dir.mkdir(parents=True, exist_ok=True)
            # write the test file to the target directory
            test_code = test_file.read_text(encoding="utf-8")
            test_main_class = extract_main_class(test_code)
            compile_file_path = compile_file_dir / f"{test_main_class}.java"
            compile_file_path.write_text(test_code, encoding="utf-8")
            # update the compile test list and mapping
            compile_file_path_str = str(compile_file_path.absolute().as_posix())
            compile_test_abspath_list.append(compile_file_path_str)
            compile_ori_test_map[compile_file_path_str] = test_abspath

        error_map = dict()
        # Use ThreadPoolExecutor for parallel compilation
        max_workers = min(len(compile_test_abspath_list), 8)  # Limit to 8 concurrent processes
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all compilation tasks
            future_to_file = {
                executor.submit(self._compile_single_file, compile_test_abspath): compile_test_abspath
                for compile_test_abspath in compile_test_abspath_list
            }

            # Collect results
            for future in concurrent.futures.as_completed(future_to_file):
                compile_test_abspath, success, error_msg = future.result()
                if not success:
                    test_abspath = compile_ori_test_map[compile_test_abspath]
                    error_map[test_abspath] = error_msg

        if not error_map:
            logger.info(f"Successfully compiled all {len(self.test_abspath_list)} test cases in {self.test_dir}.")
        else:
            self.failed_tests = sorted(error_map.keys())
            sorted_errors = [error_map[key] for key in self.failed_tests]
            error_msg = "\n".join(sorted_errors)
            logger.warning(
                f"--> Failed to compile {len(self.failed_tests)} out of {len(self.test_abspath_list)} files:\n{error_msg}"
            )

        # clean target directory if needed
        if clear_targets:
            shutil.rmtree(self.target_dir)

        # clear the compile_ws_dir directory
        shutil.rmtree(compile_ws_dir)

        status = len(error_map) == 0
        return status, error_map

    def install_lib_code(self, mock_lib_code_res: dict[str, str]) -> bool:
        """
        Install the mock lib code to the kirin workspace self.mock_tmp_dir dsl_id._mock_tmp.
        :param mock_lib_code_res: The result of the mock lib code generation. ["{class_fqn}": "{mock_code}"}]
        :return: True if the installation is successful, False otherwise.
        """
        # check the mock lib code result
        if not mock_lib_code_res:
            logger.warning(f"--> Skip install since no mock lib code is generated.")
            return False
        # create the mock tmp dir if not exists
        create_dir_with_path(self.mock_tmp_dir, cleanup=True)

        # install the mock lib code to the install_dir
        for class_fqn, lib_code in mock_lib_code_res.items():
            class_rel_path = f"{class_fqn.replace('.', '/')}.java"
            lib_file_path = self.mock_tmp_dir / class_rel_path
            # create directory structure
            lib_file_path.parent.mkdir(parents=True, exist_ok=True)
            # write the java file
            lib_file_path.write_text(lib_code, encoding="utf-8")
            logger.info(f"Installed mock lib code for {class_fqn} in {lib_file_path}.")
        return True

    def gen_mock_jar_llm(self, potential_third_fqns: list[str] = [], fix_max_attempts: int = 1) -> bool:
        """
        Generate a mock jar package for the dsl_id using LLM [with fixing].
        :param potential_third_fqns: The potential third-party fully qualified names used in the test cases.
        :param fix_max_attempts: The maximum number of attempts to fix the mock jar generation using LLM.
        :return: True if the mock jar is generated successfully, False otherwise.
        """
        logger.info(f"Generating mock lib jar for {self.dsl_id} using LLM...")
        llm_mocker = MockLibGenLLM(self.test_dir, potential_third_fqns=potential_third_fqns)
        lib_code_res = llm_mocker.gen_mock_lib_code_llm()
        # if no mock lib code is generated by llm but nonnull for ts, return False
        if self.need_third_party_lib and not lib_code_res:
            return False

        # install the mock lib code
        self.install_lib_code(lib_code_res)
        # compile the mock lib code
        lib_compile_status, error_msg = self.compile_lib_code()

        # fix the mock lib code if compilation fails using LLM
        fix_attempts = 0
        while not lib_compile_status and fix_attempts < fix_max_attempts:
            fix_attempts += 1
            logger.warning(
                f"--> [Detected LLM BuildMock Failure] Fixing with LLM[attemp-{fix_attempts}/{fix_max_attempts}]..."
            )
            lib_code_res = llm_mocker.fix_mock_lib_code(lib_code_res, error_msg)
            if not lib_code_res:
                # continue to retry
                continue
            # install & compile
            self.install_lib_code(lib_code_res)
            lib_compile_status, error_msg = self.compile_lib_code()

        return lib_compile_status

    def fix_test_compile(
        self, error_map: dict[str, str], retry_max_attempts: int = 1
    ) -> tuple[dict[str, str], dict[str, str]]:
        """
        Fix the failed test cases and mock lib code (if needed) to make them pass compilation for package.
        :param error_map: The error message map from the compilation.
        :param retry_max_attempts: The maximum number of times to retry if parsed nothing.
        :return: {test_file_path: fixed_test_file}, {class_fqn: mock_code"}
        """
        fixed_test_map = dict()
        # construct the messages
        wrapped_java_code = ""
        full_error_msg = ""
        failed_test_file_list = sorted(error_map.keys())
        for test_file in failed_test_file_list:
            test_wrapper = "alerting_file" if "PosTest" in test_file else "non_alerting_file"
            test_code = Path(test_file).read_text(encoding="utf-8")
            wrapped_java_code += f"<{test_wrapper}>\n{test_code}\n</{test_wrapper}>\n"
            full_error_msg += error_map[test_file] + "\n"
        wrapped_java_code = wrapped_java_code.rstrip()
        full_error_msg = full_error_msg.rstrip()
        lib_res_ori = dict()

        # check if dependency lib is needed
        if self.need_third_party_lib:
            wrapped_lib_code = ""
            lib_res_ori = self.get_local_lib_code()
            for fqn in lib_res_ori:
                wrapped_lib_code += f"<lib-{fqn}>\n{lib_res_ori[fqn]}\n</lib-{fqn}>\n"
            query_type = "fix_test_compile_with_lib"
            user_prompt = PROMPTS[query_type].format(
                checker_dsl=self.checker_dsl,
                wrapped_java_code=wrapped_java_code,
                wrapped_lib_code=wrapped_lib_code,
                error_msg=full_error_msg,
            )
        else:
            query_type = "fix_test_compile_wo_lib"
            user_prompt = PROMPTS[query_type].format(
                checker_dsl=self.checker_dsl,
                wrapped_java_code=wrapped_java_code,
                error_msg=full_error_msg,
            )

        # query the LLM with retry if needed
        for attempt in range(retry_max_attempts + 1):
            if attempt > 0:
                # 0 is the first attempt, others are retries
                logger.warning(
                    f"--> [Detected LLM FixTest Failure] Retrying (attempt {attempt}/{retry_max_attempts})..."
                )
            # query the LLM
            llm_result = LLMWrapper.query_llm(user_prompt, query_type=query_type)

            # extract lib res
            lib_res = parse_lib_code(llm_result)
            for fqn_ori in lib_res_ori:
                if fqn_ori not in lib_res:
                    logger.info(f"LLM did not return lib code for {fqn_ori}, using existed {fqn_ori}.")
                    lib_res[fqn_ori] = lib_res_ori[fqn_ori]

            pattern = r"<java_file>\s*(.*?)\s*</java_file>"
            test_case_list = re.findall(pattern, llm_result, re.DOTALL)
            test_case_list = [test_case for test_case in test_case_list if test_case.strip() != ""]
            test_case_list = fix_syntax_error(test_case_list)

            if len(test_case_list) != len(error_map.keys()):
                logger.warning(
                    f"--> Output test count mismatches: {len(test_case_list)} != {len(self.test_abspath_list)}."
                )
            else:
                # replace the test cases with the fixed ones in full_test_case_list
                for i, test_file in enumerate(failed_test_file_list):
                    fixed_test_map[test_file] = test_case_list[i]
                return fixed_test_map, lib_res

        logger.error(f"--> LLM FixTest failed after {retry_max_attempts} attempts! Please check the LLM output.")
        return dict(), dict()

    def clear_mock_lib(self) -> bool:
        """
        Clear the mock lib directory.
        :return: True if the clear is successful, False otherwise.
        """
        # clear mock lib dir
        if self.lib_dir.is_dir():
            shutil.rmtree(self.lib_dir)
        if self.mock_tmp_dir.is_dir():
            shutil.rmtree(self.mock_tmp_dir)

    def get_local_lib_code(self) -> dict[str, str]:
        """
        Get the local mock lib code from the mock_tmp_dir.
        :return: {"{class_fqn}": "{mock_code}"}
        """
        if not self.mock_tmp_dir.is_dir():
            logger.info(f"No local mock tmp dir {self.mock_tmp_dir} exists, skip.")
            return dict()

        lib_code_res = dict()
        for lib_file in self.mock_tmp_dir.rglob("*.java"):
            lib_file_path = Path(lib_file)
            fqn = lib_file_path.relative_to(self.mock_tmp_dir).as_posix().replace("/", ".").replace(".java", "")
            lib_code_res[fqn] = lib_file_path.read_text(encoding="utf-8")

        return lib_code_res

    def build_tests(self, fix_max_attempts: int = 1) -> bool:
        """
        [Build Main]Build(compile) the test cases for the given DSL ID with multiple attempts.
        :param fix_max_attempts: The maximum number of attempts to fix compilation using LLM.
        :return: True if the compilation is successful, False otherwise.
        """
        logger.info(f"==> Building test cases for {self.dsl_id}...")

        assert self.test_dir.is_dir(), f"--> Test dirpath {self.test_dir} does not exists!"
        if len(self.test_abspath_list) == 0:
            logger.error(f"--> No test cases are found in {self.test_dir}!")
            return True

        # parse tests' dependency using tree-sitter
        ts_mocker = MockLibGenTS(self.test_dir)
        lib_code_res = ts_mocker.gen_mock_lib_code_ts()
        self.need_third_party_lib = True if lib_code_res else False
        third_class_fqns_ts = set(lib_code_res.keys())

        # generate mock lib code, install and compile with tree-sitter & LLM
        if self.need_third_party_lib:
            # loading existing lib code if exists
            if self.mock_tmp_dir.is_dir():
                local_lib_code_res = self.get_local_lib_code()
                # check whether existing lib classes is complete and add classes if not
                missed_fqns = third_class_fqns_ts - set(local_lib_code_res.keys())
                if missed_fqns:
                    logger.info(f"Local lib misses following third-party classes: {','.join(missed_fqns)}")
                    logger.info(f"Adding missing classes with tree-sitter...")
                    for missed_class_fqn in missed_fqns:
                        local_lib_code_res[missed_class_fqn] = lib_code_res[missed_class_fqn]
                    # update local lib code and install
                    lib_code_res = local_lib_code_res
                    self.install_lib_code(lib_code_res)
            else:
                self.install_lib_code(lib_code_res)
            mock_jar_status, _ = self.compile_lib_code()

            # if not compiled successfully, retry to mock with LLM
            if not mock_jar_status:
                logger.warning(f"--> [Detected Tree-sitter GenMock Failure] Retrying with LLM...")
                if not self.gen_mock_jar_llm(potential_third_fqns=list(third_class_fqns_ts)):
                    # LLM also failed to generate mock jar
                    logger.error(f"--> Failed to gen mock jar for {self.dsl_id}, try directly compiling...")
                    test_compile_status, error_map = self.compile_test_code()
                    return test_compile_status
        else:
            shutil.rmtree(self.mock_tmp_dir, ignore_errors=True)
            shutil.rmtree(self.lib_dir, ignore_errors=True)

        fix_attempts = 0
        test_compile_status = False
        TestEditor.init()
        while not test_compile_status:
            # Test compilation
            test_compile_status, error_map = self.compile_test_code()
            if test_compile_status:
                return True
            # Fix general errors
            logger.warning(f"--> Tests fail to pass compilation. Try general fix...")
            if TestEditor.fix_general_error(error_map):
                # recompile the test cases
                continue

            # Fix test compilation errors with LLM
            fix_attempts += 1  # only increase after using LLM to fix
            if fix_attempts > fix_max_attempts:
                logger.warning(
                    f"--> Failed to compile test cases for {self.dsl_id} after {fix_max_attempts} fixing attempts!"
                )
                break

            logger.warning(
                f"--> [Detected LLM CompileTest Failure] Fixing with LLM[attemp-{fix_attempts}/{fix_max_attempts}]..."
            )
            fixed_test_map, fixed_lib_res = self.fix_test_compile(error_map)
            if not fixed_test_map:
                logger.error(f"--> Exit test build for {self.dsl_id} since fixing tests failed!")
                break
            # replace tests and lib code
            logger.info(f"Installing fixed test cases...")
            for test_file in fixed_test_map:
                Path(test_file).write_text(fixed_test_map[test_file], encoding="utf-8")
            if fixed_lib_res:
                self.need_third_party_lib = True
                logger.info(f"Installing fixed lib code...")
                self.install_lib_code(fixed_lib_res)
                mock_jar_status, _ = self.compile_lib_code()
                if not mock_jar_status:
                    logger.warning(f"--> [Detected LLM FixTest GenMock Failure] Retrying with LLM...")
                    if not self.gen_mock_jar_llm(potential_third_fqns=list(fixed_lib_res.keys())):
                        logger.error(f"--> Failed to gen mock jar for {self.dsl_id}, try directly compiling...")
                        test_compile_status, _ = self.compile_test_code()
                        return test_compile_status
            else:
                logger.info(f"No lib code generated, skip installing lib code...")
                self.clear_mock_lib()

        if not test_compile_status:
            logger.warning(
                f"--> Failed to compile test cases for {self.dsl_id} after {fix_max_attempts} fixing attempts!"
            )
            if self.failed_tests:
                failed_test_file = ", ".join(self.failed_tests)
                logger.error(f"{len(error_map.keys())} test cases still failed to compile.")

        return test_compile_status


if __name__ == "__main__":
    # Test the gen_mock_jar function
    dsl_id = "test_tmp"
    test_compiler = TestCompiler(dsl_id)
    # test_compiler.gen_mock_jar()
    _, msg = test_compiler.compile_test_code()
    # print(f"Compile lib code error msg: {msg}")
