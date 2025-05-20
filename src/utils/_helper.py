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


def extract_main_class(test_case: str) -> str:
    """
    classify test case into positive, negative or unknown
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
    pattern = r"public\s+class\s+\w+"
    new_test_case = re.sub(pattern, f"public class {class_name}", test_case)
    return new_test_case


def create_test_info(test_case_list: list[str]) -> TestInfoDict:
    """
    create test info dict based on the test case list (for each test, identify the type)
    :param test_case_list: list of test cases
    :return: test info dict
    """
    test_info = TestInfoDict(
        positive=[],
        negative=[],
        unknown=[],
    )
    for test_case in test_case_list:
        class_name = extract_main_class(test_case)
        if "positive" in class_name.lower():
            i = len(test_info["positive"]) + 1
            expected_class_name = f"PositiveTest{i}"
            if class_name != expected_class_name:
                test_case = update_main_class(test_case, expected_class_name)
            test_info["positive"].append((expected_class_name, test_case))
        elif "negative" in test_case.lower():
            i = len(test_info["negative"]) + 1
            expected_class_name = f"NegativeTest{i}"
            if class_name != expected_class_name:
                test_case = update_main_class(test_case, expected_class_name)
            test_info["negative"].append((expected_class_name, test_case))
        else:
            i = len(test_info["unknown"]) + 1
            expected_class_name = f"UnknownTest{i}"
            if class_name != expected_class_name:
                test_case = update_main_class(test_case, expected_class_name)
            test_info["unknown"].append((expected_class_name, test_case))
    return test_info


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


if __name__ == "__main__":
    # code_list = [
    #     """
    #     public class PositiveTest {
    #         public static void main(String[] args) {
    #             System.out.println("Hello, World!");
    #         }
    #     }
    #     """,
    #     """
    #     public class Positivetest {
    #         public static void main(String[] args) {
    #             System.out.println("Hello, World);
    #         }
    #     }
    #     """,
    # ]
    # print(create_test_info(code_list))
    llm_output = """
<lib-javax.validation.constraints.Pattern>
package javax.validation.constraints;

import java.lang.annotation.Documented;
import java.lang.annotation.ElementType;
import java.lang.annotation.Retention;
import java.lang.annotation.RetentionPolicy;
import java.lang.annotation.Target;

@Documented
@Target({ElementType.FIELD, ElementType.METHOD, ElementType.PARAMETER, ElementType.ANNOTATION_TYPE})
@Retention(RetentionPolicy.RUNTIME)
public @interface Pattern {
    String regexp() default "";
    String message() default "";
    Class<?>[] groups() default {};
    Class<?>[] payload() default {};
}
</lib-javax.validation.constraints.Pattern>
"""
    print(parse_lib_code(llm_output))
