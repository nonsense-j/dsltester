"""
helper functions
"""

import shutil, re, json
from pathlib import Path
from .types import DslPrepResDict, TestInfoDict, TestIdxDict
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


def collect_failed_dsl_paths(dsl_id, val_res: dict) -> list[Path]:
    """
    Identify the sub DSLs that failed to generate tests and collect their paths.
    :param dsl_id: The DSL ID.
    :param val_res: The generation result dictionary.
    :return: A list of sub DSLs that failed to generate tests.
    """
    failed_sub_dsl_paths = []
    dsl_dir = Path("kirin_ws") / dsl_id / "dsl"

    for checker_name in sorted(val_res.keys()):
        if not checker_name.startswith("DSL"):
            continue
        if not val_res["DSL_ORI"]["report"]:
            return [dsl_dir / "DSL_ORI"]

        if not val_res[checker_name]["report"]:
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
    # test rearrange_test_info using kirin_ws\ONLINE_Use_Unsafe_Algorithm_IDEA\test
    test_dir = Path("kirin_ws/ONLINE_Use_Unsafe_Algorithm_IDEA/test-tmp")
    val_res = {
        "DSL_ORI": {
            "report": {
                "AlertingTest1.java": [1],
                "AlertingTest2.java": [1],
                "AlertingTest4.java": [2],
                "NonAlertingTest1.java": [3],
            },
            "pass": ["NonAlertingTest2.java", "NonAlertingTest3.java", "AlertingTest3.java"],
        }
    }
    re_test_info, new_val_res = rearrage_test_info(test_dir, val_res)
    logger.info("Rearranged Test Information:")
    for label in re_test_info:
        file_list = list(map(lambda x: x[0], re_test_info[label]))
        logger.info(f"{label}: {', '.join(file_list)}")
    save_test_info(re_test_info, test_dir, do_test_aug=True)

    # move all the folders in kirin_ws/test-tmp to kirin_ws/test-cur
    test_cur_dir = Path("kirin_ws/test-cur")
    test_cur_dir.mkdir(parents=True, exist_ok=True)
    # using Pathlib rename to move the folder
    for item in test_dir.iterdir():
        shutil.move(str(item), str(test_cur_dir / item.name))

    logger.info(f"New Validation Result: {new_val_res}")
