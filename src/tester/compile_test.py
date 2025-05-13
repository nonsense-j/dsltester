"""
If a DSL uses third-party libraries, we will generate a mock jar package for it.
Notably, properties like function and field should also be mocked.
"""

import subprocess, os, shutil, re
from pathlib import Path

from src.utils._logger import logger
from src.tester.prompts import PROMPTS
from src.utils.config import KIRIN_JAVA_HOME
from src.mock.mock_lib_llm import MockLibGenLLM
from src.mock.mock_lib_ts import MockLibGenTS
from src.utils._llm import LLMWrapper
from src.utils._helper import create_dir_with_path, parse_lib_code
from src.tester.gen_test import fix_syntax_error, save_test_info


class TestCompiler:
    """
    This class is used to compile the test cases for the given DSL ID.
    For third-party dependency, it will generate a mock jar package and compile the test cases.
    """

    def __init__(self, dsl_id: str):
        self.dsl_id = dsl_id
        self.dsl_ws_dir = Path(f"kirin_ws/{dsl_id}")

        self.test_dir = self.dsl_ws_dir / "test"
        assert self.test_dir.is_dir(), f"--> Test dirpath {self.test_dir} does not exists!"

        self.test_filepaths_str: list[str] = [test_file for test_file in self.test_dir.rglob("*.java")]
        if len(self.test_filepaths_str) == 0:
            logger.error(f"--> No test cases are found in {self.test_dir}!")
            raise AssertionError(f"--> No test cases are found in {self.test_dir}!")

        # preload paths(not created)
        self.lib_dir = self.dsl_ws_dir / "lib"
        self.mock_tmp_dir = self.dsl_ws_dir / "_mock_tmp"
        self.mock_jar_file = self.lib_dir / "mock.jar"
        self.target_dir = self.test_dir.parent / "target"

        # cmd executable
        self.javac_executable = os.path.join(KIRIN_JAVA_HOME, "bin", "javac")
        self.jar_executable = os.path.join(KIRIN_JAVA_HOME, "bin", "jar")
        if os.name == "nt":
            self.javac_executable += ".exe"
            self.jar_executable += ".exe"

        # indicate the mock lib code is generated only by tree-sitter
        self.ts_gen_flag = False

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
            javac_res = subprocess.run(
                [self.javac_executable, "-encoding", "utf-8" "-d", str(self.mock_tmp_dir)] + self.test_filepaths_str,
                capture_output=True,
                text=True,
                check=True,
            )
            logger.debug(f"Javac result: \n{javac_res.stdout}")

            # package
            jar_res = subprocess.run(
                [self.jar_executable, "cvf", str(self.mock_jar_file), "-C", str(self.mock_tmp_dir), "."],
                capture_output=True,
                text=True,
                check=True,
            )
            logger.debug(f"Jar result: \n{jar_res.stdout}")

            logger.info(f"Successfully build mock JAR at {self.mock_jar_file}")
            return True, ""
        except subprocess.CalledProcessError as e:
            logger.warning(f"--> Failed to build mock JAR for {self.dsl_id}: {e}")
            logger.warning(f"Std error: \n{e.stderr}")
            return False, str(e.stderr)

    def compile_test_code(self, clear_targets: bool = True) -> tuple[bool, str]:
        """
        Compile the test cases. Before compilation, the mock jar lib will also be genrated and installed.
        Read test cases from test_dir (lib from lib_dir) and write the compiled class files to target_dir.
        :param clear_targets: Whether to clear the target directory after compilation.
        :return: (status, error_msg)
        """
        # Compile the test cases
        create_dir_with_path(self.target_dir, cleanup=True)
        try:
            cmd_list = [self.javac_executable, "-encoding", "utf-8", "-d", str(self.target_dir)]
            # if self.lib_dir.is_dir():
            #     cmd_list += ["-cp", str(self.mock_jar_file)]
            cmd_list += self.test_filepaths_str
            subprocess.run(cmd_list, capture_output=True, text=True, check=True)
            logger.info(f"Successfully compile all test cases for {self.dsl_id}.")
            return True, ""
        except subprocess.CalledProcessError as e:
            logger.warning(f"--> Failed to compile test cases for {self.dsl_id}: {e}")
            logger.warning(f"Std error: \n{e.stderr}")
            return False, str(e.stderr)
        finally:
            # clear the target directory if needed
            if clear_targets:
                shutil.rmtree(self.target_dir)

    def install_lib_code(self, mock_lib_code_res: dict[str, str]) -> bool:
        """
        Install the mock lib code to the kirin workspace self.mock_tmp_dir dsl_id._mock_tmp.
        :param mock_lib_code_res: The result of the mock lib code generation. ["{class_fqn}": "{mock_code}"}]
        :return: True if the installation is successful, False otherwise.
        """
        # check the mock lib code result
        if len(mock_lib_code_res) == 0:
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

    def gen_mock_jar(self, only_use_llm: bool = False, skip_lib_gen: bool = False, fix_max_attempts: int = 1) -> bool:
        """
        generate a mock jar package for the dsl_id (empty implementation with only signatures)
        :param only_use_llm: Whether to only use LLM to generate the mock lib code.
        :param skip_lib_gen: Whether to skip the mock lib generation and only package.
        :param fix_max_attempts: The maximum number of attempts to fix the mock jar generation using LLM.
        Return:
            True: successully generated the mock jar, no mock jar needed
            False: failed to generate the mock jar
        """
        strategy = "LLM" if only_use_llm else "tree-sitter & LLM"
        logger.info(f"==> Generating mock lib jar for {dsl_id} using {strategy}")
        ts_mocker = MockLibGenTS(self.test_dir)
        llm_mocker = MockLibGenLLM(self.test_dir)

        if skip_lib_gen:
            logger.info(f"Using existing lib code to build Jar package.")
        else:
            if only_use_llm:
                # generate mock lib code only with LLM
                mock_status, lib_code_res = llm_mocker.gen_mock_lib_code_llm()
            else:
                # generate mock lib code (default: tree-sitter -> LLM)
                mock_status, lib_code_res = ts_mocker.gen_mock_lib_code_ts()
                if not mock_status:
                    logger.warning(f"--> [Detected Tree-sitter GenMock Failure] Retrying with LLM...")
                    mock_status, lib_code_res = llm_mocker.gen_mock_lib_code_llm()
                else:
                    self.ts_gen_flag = True

            # [Case 1] no need to generate mock lib code
            if mock_status and not lib_code_res:
                logger.info(f"No mock lib code is needed for {dsl_id}")
                return True

            # [Case 2] LLM generation failed (no mock lib code responses but expected to have)
            if not mock_status:
                logger.warning(f"--> Failed to generate mock lib code for {dsl_id} using {strategy}!")
                return False

            # [Case 3] Handle when we successfully extract mock lib code, which also means tests need third-party lib
            self.install_lib_code(lib_code_res)

        lib_compile_status, error_msg = self.compile_lib_code()

        # if the mock lib code is generated successfully by ts, but the compilation fails, retry with LLM
        if self.ts_gen_flag and not lib_compile_status:
            logger.warning(f"--> [Detected Tree-sitter BuildMock Failure] Retrying with LLM...")
            self.ts_gen_flag = False
            mock_status, lib_code_res = llm_mocker.gen_mock_lib_code_llm()
            if not mock_status:
                logger.warning(f"--> Failed to generate mock lib code for {dsl_id} using {strategy}!")
                return False
            self.install_lib_code(lib_code_res)
            lib_compile_status, error_msg = self.compile_lib_code()

        # Here, all mock lib is generated by LLM but fail compilation. Try fixing the mock lib jar with error msg
        fix_attempts = 1
        while fix_attempts <= fix_max_attempts and not lib_compile_status:
            logger.warning(
                f"--> [Detected LLM BuildMock Failure] Fixing with LLM[attemp-{fix_attempts}/{fix_max_attempts}]..."
            )
            mock_status, lib_code_res = llm_mocker.fix_mock_lib_code(lib_code_res, error_msg)
            if not mock_status:
                # retry
                continue
            # install & compile
            self.install_lib_code(lib_code_res)
            lib_compile_status, error_msg = self.compile_lib_code()
            fix_attempts += 1

        if not lib_compile_status:
            # TODO)) remove raise AssertionError
            raise AssertionError(
                f"--> Failed to generate mock jar for {dsl_id} after {fix_max_attempts} fixing attempts!"
            )
            logger.warning(f"--> Failed to generate mock jar for {dsl_id} after {fix_max_attempts} fixing attempts!")
            shutil.rmtree(self.mock_tmp_dir)
            shutil.rmtree(self.lib_dir)
            return False

        return lib_compile_status

    def fix_test_compile(self, error_msg: str) -> dict[str, str]:
        """
        Fix the mock lib code to make it pass compilation for package.
        :param error_msg: The error message from the compilation.
        :return: {"{class_fqn}": "{mock_code}"}
        """
        # construct the messages
        wrapped_java_code = ""
        for test_file in self.test_filepaths_str:
            test_file_path = Path(test_file)
            wrapped_java_code += f"<java_file>\n{test_file_path.read_text(encoding='utf-8')}\n</java_file>\n"

        wrapped_lib_code = ""
        if self.lib_dir.is_dir():
            for lib_file in self.mock_tmp_dir.rglob("*.java"):
                lib_file_path = Path(lib_file)
                fqn = lib_file_path.relative_to(self.mock_tmp_dir).as_posix().replace("/", ".").replace(".java", "")
                wrapped_lib_code += f"<lib-{fqn}>\n{lib_file_path.read_text(encoding='utf-8')}\n</lib-{fqn}>\n"
            user_prompt = PROMPTS["fix_test_compile_with_lib"].format(
                wrapped_java_code=wrapped_java_code,
                wrapped_lib_code=wrapped_lib_code,
                error_msg=error_msg,
            )
        else:
            user_prompt = PROMPTS["fix_test_compile_wo_lib"].format(
                wrapped_java_code=wrapped_java_code,
                error_msg=error_msg,
            )
        llm_result = LLMWrapper.query_llm(user_prompt, query_type="fix_test_compile")
        logger.debug(f"LLM FixTestCompile result: \n{llm_result}")

        # parse result
        pattern = r"<java_file>\s*(.*?)\s*</java_file>"
        _, lib_res = parse_lib_code(llm_result)
        test_case_list = re.findall(pattern, llm_result, re.DOTALL)
        test_case_list = [test_case for test_case in test_case_list if test_case.strip() != ""]
        test_case_list = fix_syntax_error(test_case_list)

        return test_case_list, lib_res

    def compile_tests(self, fix_max_attempts: int = 1) -> bool:
        """
        [Compile Main]Compile the test cases for the given DSL ID with multiple attempts.
        :param fix_max_attempts: The maximum number of attempts to fix compilation using LLM.
        :return: True if the compilation is successful, False otherwise.
        """
        logger.info(f"==> Compiling test cases for {dsl_id}...")

        dsl_ws_dir = Path(f"kirin_ws/{dsl_id}")
        test_dir = dsl_ws_dir / "test"
        assert test_dir.is_dir(), f"--> Test dirpath {test_dir} does not exists!"
        all_test_filepaths = list(test_dir.rglob("*.java"))
        if len(all_test_filepaths) == 0:
            logger.error(f"--> No test cases are found in {test_dir}!")
            return False

        # generate, install and compile lib jar (initial: ts -> llm)
        mock_jar_status = self.gen_mock_jar(only_use_llm=False)
        if not mock_jar_status:
            logger.error(f"--> Failed to compile test cases for {dsl_id} since generating mock jar failed!")
            return False

        # compile the test cases
        test_compile_status, error_msg = self.compile_test_code()

        if "error: cannot find symbol" in error_msg and self.ts_gen_flag and not test_compile_status:
            logger.warning(f"--> [Detected Tree-sitter CompileTest Failure] Retrying mocking with LLM...")
            self.ts_gen_flag = False
            mock_jar_status = self.gen_mock_jar(only_use_llm=True)
            if not mock_jar_status:
                logger.warning(f"--> Failed to compile test cases for {dsl_id} since generating mock jar failed!")
                return False
            test_compile_status, error_msg = self.compile_test_code()

        # Try fixing the compilation error using LLM if fails [fix mock lib or fix test code]
        fix_attempts = 1
        while fix_attempts <= fix_max_attempts and not test_compile_status:
            logger.warning(
                f"--> [Detected LLM CompileTest Failure] Fixing with LLM[attemp-{fix_attempts}/{fix_max_attempts}]..."
            )
            fixed_test_list, fixed_lib_res = self.fix_test_compile(error_msg)
            test_info = {"positive": fixed_test_list}
            # save tests and lib code
            save_test_info(test_info, self.test_dir)
            self.install_lib_code(fixed_lib_res)
            lib_compile_status, error_msg = self.compile_lib_code()
            if not lib_compile_status:
                # retry
                continue

            test_compile_status, error_msg = self.compile_test_code()

        if not test_compile_status:
            # TODO)) remove raise AssertionError
            raise AssertionError(
                f"--> Failed to compile test cases for {dsl_id} after {fix_max_attempts} fixing attempts!"
            )
            logger.warning(f"--> Failed to compile test cases for {dsl_id} after {fix_max_attempts} fixing attempts!")
            shutil.rmtree(self.mock_tmp_dir)
            shutil.rmtree(self.lib_dir)
            return False

        return test_compile_status


if __name__ == "__main__":
    # Test the gen_mock_jar function
    dsl_id = "ONLINE_AG_CmdInjection"
    test_compiler = TestCompiler(dsl_id)
    _, msg = test_compiler.compile_test_code(clear_targets=False)
    print(f"Compile test code result: {'error: cannot find symbol' in msg}")
