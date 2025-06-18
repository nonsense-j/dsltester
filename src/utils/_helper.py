"""
helper functions
"""

import shutil, re, json
from pathlib import Path
from .types import DslInfoDict, DslPrepResDict, TestInfoDict
from ._logger import logger

import tree_sitter_java as tsjava
from tree_sitter import Language, Parser

# list of builtin package prefixes
JAVA_BUILTIN_PKG_PREFIXES = []


def create_dir_with_path(dir_path: Path, cleanup=True):
    """
    only allow create folders and files in kirin_ws
    :param dir_path: path to create
    :param cleanup: if True, remove the folder if it exists
    """
    dir_abspath = dir_path.absolute()
    kirin_ws_abspath = Path("kirin_ws").absolute()
    if not str(dir_abspath).startswith(str(kirin_ws_abspath)):
        raise ValueError(f"[Exception] not allowed to create folder {dir_path} beyond kirin_ws")
    # cleanup
    if cleanup and dir_path.exists():
        shutil.rmtree(dir_path)

    dir_path.mkdir(parents=True, exist_ok=True)


def del_kirin_logs(dir_path: Path):
    """
    delete kirin logs
    :param dir_path: path to delete
    """
    if dir_path.exists():
        # only delete .log files in the subfolder without recursing
        for file in dir_path.glob("*.log"):
            file.unlink()


def read_file(file_path: Path) -> str:
    """
    read file
    :param file_path: path to read
    :return: content of the file
    """
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    return content


def load_builtin_pkg_prefixes():
    """
    load builtin package prefixes from json file
    :return: list of builtin package prefixes
    """
    global JAVA_BUILTIN_PKG_PREFIXES
    if not JAVA_BUILTIN_PKG_PREFIXES:
        with open("src/resources/java17_builtin_pkg.json", "r") as f:
            JAVA_BUILTIN_PKG_PREFIXES = json.load(f)


def is_third_class(class_fqn: str) -> bool:
    """
    check if the class name is a third class
    :param class_fqn: class name
    :return: True if the class name is a third class
    """
    # look for: https://docs.oracle.com/en/java/javase/17/docs/api/allpackages-index.html
    # saved in src/resources/java17_builtin_pkg.json -> preload in JAVA_BUILTIN_PKG_PREFIXES
    if not JAVA_BUILTIN_PKG_PREFIXES:
        load_builtin_pkg_prefixes()
    return not any([class_fqn.startswith(prefix) for prefix in JAVA_BUILTIN_PKG_PREFIXES])


def is_standard_class(class_fqn: str) -> bool:
    """
    Check whether the class fqn follows best practice.
    package id len >= 2; package ids must lowercase; class id must start with upper case
    """
    pkg_name, cls_name = class_fqn.rsplit(".", 1)
    # pkg len > 2
    if "." not in pkg_name:
        return False
    # pkg name must be lowercase, cls name must start with upper case
    return pkg_name.lower() and cls_name[0].isupper()


def extract_missing_pkgs(compile_error_msg: str) -> list[str]:
    """
    Extract the missing packages from the compile error message.
    :param compile_error_msg: The compile error message.
    :return: A list of missing packages.
    """
    unrecog_pkg_pattern = re.compile(r"error: package ([\w\.]+) does not exist")
    missing_pkgs = unrecog_pkg_pattern.findall(compile_error_msg)

    return list(set(missing_pkgs))


def get_pkgs_from_fqns(class_fqns: list[str]) -> list[str]:
    """
    Extract the package names from the fully qualified class names.
    :param class_fqns: A list of fully qualified class names.
    :return: A list of package names.
    """
    pkgs = set()
    for class_fqn in class_fqns:
        pkg_name = class_fqn.rsplit(".", 1)[0]
        pkgs.add(pkg_name)
    return pkgs


def save_dsl_prep_result(dsl_prep_result: DslPrepResDict, save_dir: Path):
    """
    save dsl prep result to file
    :param dsl_prep_result: dsl prep result
    :param save_dir: path to save the result
    """
    if not save_dir.exists():
        save_dir.mkdir(parents=True, exist_ok=True)
    for key, value in dsl_prep_result.items():
        with open(save_dir / f"{key}.json", "w", encoding="utf-8") as f:
            f.write(value)


def parse_lib_code(llm_result: str) -> dict[str, str]:
    """
    Parse the LLM result to get the mock lib code.
    :param llm_result: The LLM result string.
    :return: {"{class_fqn}": "{mock_code}"}
    """
    wrapper = r"<lib-(.*?)>\s*(.*?)\s*</lib-\1>"
    llm_parse_res = re.findall(wrapper, llm_result, re.DOTALL)
    lib_res = dict()
    for lib_code in llm_parse_res:
        class_fqn = lib_code[0].strip()
        lib_code = lib_code[1]
        if is_third_class(class_fqn) and lib_code.strip():
            # check for duplicate class names
            assert class_fqn not in lib_res, f"Duplicate class name {class_fqn} found in the mock code!"
            lib_res[class_fqn] = lib_code

    return lib_res


def validate_syntax(java_code_list: list[str]) -> list[bool]:
    """
    check if the java code has syntax error with tree-sitter
    :param java_code_list: list of java code
    :return: True if there is no syntax error
    """
    # Load the Java language
    java_parser = Parser(Language(tsjava.language()))
    result = []
    for java_code in java_code_list:
        try:
            tree = java_parser.parse(bytes(java_code, "utf-8"))
            if tree.root_node.has_error:
                result.append(False)
            else:
                result.append(True)
        except Exception as e:
            result.append(False)
    return result


def extract_main_class(test_case: str) -> str:
    """
    extract the main class name.
    :param test_case: test case
    :return: main class name
    """
    # extract the main public class name from the test case
    pattern = r"public\s+class\s+(\w+)"
    match = re.search(pattern, test_case)
    class_name = ""
    if match:
        class_name = match.group(1)
    if not class_name:
        logger.warning(f"--> No public main class found in the test case: {test_case}")
    return class_name


def update_main_class(test_case: str, class_name: str) -> str:
    """
    update the main class name in the test case
    :param test_case: test case
    :param class_name: new class name
    :return: updated test case
    """
    # update the main public class name in the test case
    pattern = r"public\s+(class)\s+\w+"
    # replace the class name with the new class name
    ori_class_name = re.search(pattern, test_case)
    if not ori_class_name:
        logger.error(f"--> No public main class found in the test case: {test_case}")
        return test_case
    else:
        ori_class_name = ori_class_name.group(0)
        new_test_case = test_case.replace(ori_class_name, class_name)
    return new_test_case


def collect_local_test_info(test_dir: Path) -> TestInfoDict:
    """
    Collect test information from the test directory.
    """
    assert test_dir.is_dir(), f"--> Test directory {test_dir} not found!"
    test_info = TestInfoDict(alerting=[], non_alerting=[], mismatch=[])

    alert_dir = test_dir / "alert"
    for test_file in sorted(alert_dir.glob("*.java")):
        test_code = read_file(test_file)
        class_name = test_file.stem
        test_info["alerting"].append((class_name, test_code))

    non_alert_dir = test_dir / "no-alert"
    for test_file in sorted(non_alert_dir.glob("*.java")):
        test_code = read_file(test_file)
        class_name = test_file.stem
        test_info["non_alerting"].append((class_name, test_code))

    mismatch_dir = test_dir / "mismatch"
    if mismatch_dir.is_dir():
        for test_file in sorted(mismatch_dir.glob("*.java")):
            test_code = read_file(test_file)
            class_name = test_file.stem
            test_info["mismatch"].append((class_name, test_code))

    return test_info


def collect_local_start_ids(test_dir: Path) -> tuple[tuple[int, int], tuple[int, int]]:
    """
    Collect the start ids for appending alerting, non-alerting, and mismatch tests from the test directory.
    :param test_dir: The test directory path.
    :return: (alert_test_count, non_alert_test_count), (mismatch_alert_test_count, mismatch_non_alert_test_count), mismatch_count
    """
    assert test_dir.is_dir(), f"--> Test directory {test_dir} not found!"

    alert_count = len(list((test_dir / "alert").glob("*.java")))
    non_alert_count = len(list((test_dir / "no-alert").glob("*.java")))

    mismatch_alert_count = 0
    mismatch_non_alert_count = 0
    for mismatch_file in (test_dir / "mismatch").glob("*.java"):
        class_name = mismatch_file.stem
        if class_name.startswith("MismatchAlertingTest"):
            mismatch_alert_count += 1
        elif class_name.startswith("MismatchNonAlertingTest"):
            mismatch_non_alert_count += 1

    return (alert_count + 1, non_alert_count + 1), (mismatch_alert_count + 1, mismatch_non_alert_count + 1)


def create_test_info(
    alerting_test_list: list[str],
    non_alerting_test_list: list[str],
    mismatch_test_list: list[str] = [],
    start_ids: tuple[int] = (1, 1),
    mismatch_start_ids: tuple[int] = (1, 1),
) -> TestInfoDict:
    """
    create test info dict based on the two types of test case list (checking the class name and reordering)
    :param alerting_test_list: list of alerting test cases
    :param non_alerting_test_list: list of non-alerting test cases
    :param mismatch_test_list: list of mismatch test cases (optional)
    :param start_ids: (alert_start, no_alert_start), the starting ids for alerting and non-alerting test cases
    :param mismatch_start_ids: (mismatch_alert_start, mismatch_no_alert_start), the starting ids for alerting and non-alerting mismatch test cases
    :return: test info dict
    """
    test_info = TestInfoDict(alerting=[], non_alerting=[])
    for i, test_case in enumerate(alerting_test_list):
        class_name = extract_main_class(test_case)
        expected_class_name = f"AlertingTest{start_ids[0] + i}"
        if class_name != expected_class_name:
            test_case = update_main_class(test_case, expected_class_name)
        test_info["alerting"].append((expected_class_name, test_case))

    for i, test_case in enumerate(non_alerting_test_list):
        class_name = extract_main_class(test_case)
        expected_class_name = f"NonAlertingTest{start_ids[1] + i}"
        if class_name != expected_class_name:
            test_case = update_main_class(test_case, expected_class_name)
        test_info["non_alerting"].append((expected_class_name, test_case))

    # for mismatch test cases, we update the class name as follows:
    # AlertingTest{i} -> MismatchAlertingTest{j}; NonAlertingTest{i} -> MismatchNonAlertingTest{j}
    if mismatch_test_list:
        test_info["mismatch"] = []
        mismatch_alert_i, mismatch_no_alert_i = mismatch_start_ids
        for test_case in mismatch_test_list:
            ori_class_name = extract_main_class(test_case)
            assert ori_class_name.startswith("Alerting") or ori_class_name.startswith(
                "NonAlerting"
            ), f"--> Mismatch test case {test_case} does not start with Alerting or NonAlerting!"
            if ori_class_name.startswith("Alerting"):
                new_class_name = f"MismatchAlertingTest{mismatch_alert_i}"
                mismatch_alert_i += 1
            else:
                new_class_name = f"MismatchNonAlertingTest{mismatch_no_alert_i}"
                mismatch_no_alert_i += 1
            test_case = update_main_class(test_case, new_class_name)
            test_info["mismatch"].append((new_class_name, test_case))

    return test_info


def save_test_info(test_info: TestInfoDict, test_dir: Path, do_test_aug: bool = False) -> None:
    """
    Save the test information to the test directory.
    Args:
        test_info (TestInfoDict): The test information dictionary.
        test_dir (Path): The test directory path.
    """
    assert test_dir.is_dir(), f"--> Test directory {test_dir} not found!"
    if not do_test_aug:
        create_dir_with_path(test_dir, cleanup=True)

    sub_test_dir_map = {
        "alerting": test_dir / "alert",
        "non_alerting": test_dir / "no-alert",
        "mismatch": test_dir / "mismatch",
    }

    for label, sub_test_info in test_info.items():
        logger.info(f"Saving {len(sub_test_info)} {label} test cases...")
        sub_test_dir = sub_test_dir_map[label]
        sub_test_dir.mkdir(parents=True, exist_ok=True)
        for single_test_info in sub_test_info:
            file_stem, test_case_code = single_test_info
            test_case_path = sub_test_dir / f"{file_stem}.java"
            test_case_path.write_text(test_case_code, encoding="utf-8")

    logger.info(f"All test cases saved to {test_dir}")


def rearrage_test_info(test_dir: Path, gen_res: dict, allow_failed_build: bool = True) -> tuple[TestInfoDict, dict]:
    """
    Rearrange the test directory based on the generation result.
    gen_res is a dictionary with the following structure:
    {
        "BUILD_FAIL_TESTS": [list of failed test cases],
        "DSL_ORI": {"report": {file_name: [line_numbers]}, "pass": [list of passed files]},
        "DSL_N1": {"report": {file_name: [line_numbers]}, "pass": [list of passed files]},
        "DSL_N1_S1": {"report": {file_name: [line_numbers]}, "pass": [list of passed files]},
        "DSL_OPP_N1": {"report": {file_name: [line_numbers]}, "pass": [list of passed files]},
        "DSL_OPP_N1_S1": {"report": {file_name: [line_numbers]}, "pass": [list of passed files]},
        ...
    }
    :return: A tuple containing the rearranged test information and the updated generation result.
    """
    assert test_dir.is_dir(), f"--> Test directory {test_dir} not found!"
    assert "DSL_ORI" in gen_res, f"--> DSL_ORI not found in the generation result {gen_res}"
    # identify mismatches
    mismatched_tests = []
    true_alerting_tests = []
    true_non_alerting_tests = []
    test_change_map = dict()

    # read and append existing mismatch files
    mismatch_test_subdir = test_dir / "mismatch"
    for mismatch_file in mismatch_test_subdir.glob("*.java"):
        mismatched_tests.append(read_file(mismatch_file))

    for alerting_file in sorted(gen_res["DSL_ORI"]["report"].keys()):
        alerting_test_code = read_file(test_dir / "alert" / alerting_file)
        if alerting_file.startswith("NonAlerting"):
            # alerting test but not reported
            mismatched_tests.append(alerting_test_code)
            test_change_map[alerting_file] = f"MismatchAlerting{len(mismatched_tests)}"
        elif alerting_file.startswith("Alerting"):
            true_alerting_tests.append(alerting_test_code)
            new_alerting_file = f"AlertingTest{len(true_alerting_tests)}"
            if alerting_file != new_alerting_file:
                test_change_map[alerting_file] = new_alerting_file
        else:
            # starting with "Mismatch"
            continue

    for non_alerting_file in sorted(gen_res["DSL_ORI"]["pass"]):
        non_alerting_test_code = read_file(test_dir / "no-alert" / non_alerting_file)
        if non_alerting_file.startswith("Alerting"):
            # non-alerting test but reported
            mismatched_tests.append(non_alerting_test_code)
            test_change_map[non_alerting_file] = f"MismatchNonAlerting{len(mismatched_tests)}"
        elif non_alerting_file.startswith("NonAlerting"):
            true_non_alerting_tests.append(non_alerting_test_code)
            new_non_alerting_file = f"NonAlertingTest{len(true_non_alerting_tests)}"
            if non_alerting_file != new_non_alerting_file:
                test_change_map[non_alerting_file] = new_non_alerting_file
        else:
            continue

    test_info = create_test_info(
        alerting_test_list=true_alerting_tests,
        non_alerting_test_list=true_non_alerting_tests,
        mismatch_test_list=list(mismatched_tests),
    )

    # substitute the test cases in the gen_res based on the test_change_map, by converting gen_res to json string then replace
    gen_res_str = json.dumps(gen_res)
    for old_name, new_name in test_change_map.items():
        gen_res_str = gen_res_str.replace(old_name, new_name)
    new_gen_res = json.loads(gen_res_str)

    return test_info, new_gen_res


def collect_failed_dsl_paths(dsl_id, gen_res: dict) -> list[Path]:
    """
    Identify the sub DSLs that failed to generate tests and collect their paths.
    :param dsl_id: The DSL ID.
    :param gen_res: The generation result dictionary.
    :return: A list of sub DSLs that failed to generate tests.
    """
    failed_sub_dsl_paths = []
    dsl_dir = Path("kirin_ws") / dsl_id / "dsl"

    for checker_name in sorted(gen_res.keys()):
        if checker_name == "BUILD_FAIL_TESTS":
            continue
        if not gen_res["DSL_ORI"]["report"]:
            return [dsl_dir / "DSL_ORI"]

        if not gen_res[checker_name]["report"]:
            # DSL_N1, DSL_N1_S1, DSL_OPP_N1, DSL_OPP_N1_S1, etc.
            if checker_name.startswith("DSL_N"):
                if "S" in checker_name:
                    parent_node_name = re.match(r"^(.*)_S\d+$", checker_name).group(1)
                    if parent_node_name in failed_sub_dsl_paths:
                        continue
                failed_sub_dsl_paths.append(dsl_dir / "norm" / f"{checker_name}.kirin")
            elif checker_name.startswith("DSL_OPP_N"):
                if "S" in checker_name:
                    parent_node_name = re.match(r"^(.*)_S\d+$", checker_name).group(1)
                    if parent_node_name in failed_sub_dsl_paths:
                        continue
                failed_sub_dsl_paths.append(dsl_dir / "opp" / f"{checker_name}.kirin")

    return failed_sub_dsl_paths


if __name__ == "__main__":
    code_list = [
        """
        public class PositiveTest {
            public static void main(String[] args) {
                System.out.println("Hello, World!");
            }
        }
        """,
        """
        // Positivetest: test case for positive test
        public class Positivetest {
            public static void main(String[] args) {
                System.out.println("Hello, World);
            }
        }
        """,
    ]
    test_info = create_test_info(code_list)
    for k, v in test_info.items():
        print(f"{k}: {len(v)}")
        for i in v:
            print(f"  {i[0]}: {i[1]}")
#     llm_output = """
# <lib-javax.validation.constraints.Pattern>
# package javax.validation.constraints;

# import java.lang.annotation.Documented;
# import java.lang.annotation.ElementType;
# import java.lang.annotation.Retention;
# import java.lang.annotation.RetentionPolicy;
# import java.lang.annotation.Target;

# @Documented
# @Target({ElementType.FIELD, ElementType.METHOD, ElementType.PARAMETER, ElementType.ANNOTATION_TYPE})
# @Retention(RetentionPolicy.RUNTIME)
# public @interface Pattern {
#     String regexp() default "";
#     String message() default "";
#     Class<?>[] groups() default {};
#     Class<?>[] payload() default {};
# }
# </lib-javax.validation.constraints.Pattern>
# """
#     print(parse_lib_code(llm_output))
