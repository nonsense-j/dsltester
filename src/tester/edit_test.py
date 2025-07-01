import re
import tree_sitter_java as tsjava
from pathlib import Path
from tree_sitter import Language, Parser

from src.utils._logger import logger


class TestEditor:
    """
    TestEditor is a class that provides methods to edit test files, mainly for fixing gneral compilation errors.
    """

    JAVA_LANGUAGE = Language(tsjava.language())
    parser = Parser(JAVA_LANGUAGE)
    # "filename:line_number"
    skip_file_lines: set[str] = set()

    @classmethod
    def init(cls):
        """
        Initialize the TestEditor class by loading the Java language parser.
        """
        cls.skip_file_lines.clear()

    @classmethod
    def fix_general_error(cls, error_map: dict[str, str]) -> bool:
        """
        Try fixing general compilation errors in test files using tree-sitter.
        :param error_map: A dictionary mapping file names to error messages.
        :return: True if any unsupported exceptions were fixed, False otherwise.
        """
        for file_name, error_msg in error_map.items():
            # # get the error count since each error_msg endswith "x errors\s+" or "x error\s+"
            # error_count_match = re.search(r"(\d+)\s+error[s]?\s*$", error_msg)
            # error_count = int(error_count_match.group(1)) if error_count else 0
            # if error_count == 0:
            #     logger.info(f"No compilation errors in {file_name}, skip...")
            #     continue
            # check unsupported exception

            if f"{file_name}:{error_msg}" in cls.skip_file_lines:
                logger.info(f"Skipping {file_name} due to previously fixed errors.")
                continue

            do_fix_flag = False
            unsupported_exception_match = re.search(
                r"\w+\.java:(\d+): error: unreported (exception|error) (\w+); must be caught or declared to be thrown",
                error_msg,
            )
            if unsupported_exception_match:
                line_number = int(unsupported_exception_match.group(1))
                exception_name = unsupported_exception_match.group(3)
                test_file = Path(file_name)
                do_fix_flag = True
                if test_file.exists():
                    try:
                        default_e = "Exception" if exception_name.endswith("Exception") else "Error"
                        cls.fix_unsupported_exception(
                            test_file, line_number, default_exception=default_e, do_replace=True
                        )
                    except Exception as e:
                        cls.skip_file_lines.add(f"{file_name}:{line_number}")
                        logger.error(f"Failed to fix unsupported exception in {test_file} at line {line_number}: {e}")
                else:
                    logger.error(f"Test file {file_name} does not exist.")

            never_throw_exception_match = re.search(
                r"\w+\.java:(\d+): error: (exception|error) (\w+) is never thrown in body of corresponding try statement",
                error_msg,
            )
            if never_throw_exception_match:
                line_number = int(never_throw_exception_match.group(1))
                wrong_exception = never_throw_exception_match.group(3)
                test_file = Path(file_name)
                do_fix_flag = True
                if test_file.exists():
                    try:
                        correct_exception = "Exception" if wrong_exception.endswith("Exception") else "Error"
                        cls.fix_never_throw_exception(
                            test_file, line_number, wrong_exception, correct_exception, do_replace=True
                        )
                    except Exception as e:
                        cls.skip_file_lines.add(f"{file_name}:{line_number}")
                        logger.error(f"Failed to fix never throw exception in {test_file} at line {line_number}: {e}")
                else:
                    logger.error(f"Test file {file_name} does not exist.")
        if do_fix_flag:
            logger.info("Finish fixing general errors in test files, try re-compiling...")
        else:
            logger.info("No general errors found in test files, skipping...")
        return do_fix_flag

    @classmethod
    def fix_never_throw_exception(
        cls, test_file: Path, error_line: int, wrong_exception: str, correct_exception: str, do_replace=False
    ) -> str:
        with open(test_file, "r", encoding="utf-8") as f:
            code = f.readlines()
        # replace the error line with the correct exception
        error_line_index = error_line - 1
        if error_line_index < 0 or error_line_index >= len(code):
            raise ValueError(f"Error line {error_line} is out of range for file {test_file}")
        new_error_line = code[error_line_index].replace(wrong_exception, correct_exception)
        code[error_line_index] = new_error_line

        if do_replace:
            with open(test_file, "w", encoding="utf-8") as f:
                f.writelines(code)
            logger.info(
                f"Fixed never throw exception in {test_file} at line {error_line} from {wrong_exception} to {correct_exception}."
            )

    @classmethod
    def fix_unsupported_exception(
        cls, test_file: Path, error_line: int, default_exception="Exception", do_replace=False
    ) -> str:
        """
        Fix unsupported exception in the test file by adding "throws Exception" or "throws Error" to the method containing the error line,
        also add the default exception to enclosing method that invoking the target method.
        :param test_file: Path to the test file.
        :param error_line: The line containing the compilation error. (starting from 1)
        :return: The transformed code with the exception fixed.
        """
        # Parse the test file
        with open(test_file, "r", encoding="utf-8") as f:
            code = f.read()
        fixed_code = ""

        # all methods need to be declared with throws Exception or throws Error
        edit_method_nodes = []

        # Find the method node containing the specified line number
        tree = cls.parser.parse(bytes(code, "utf8"))
        root_node = tree.root_node
        method_decl_query = cls.JAVA_LANGUAGE.query(
            """
            (method_declaration) @method_decl
            """
        )
        method_decl_captures = method_decl_query.captures(root_node)
        method_decl_nodes = method_decl_captures.get("method_decl", [])
        target_method_node = None
        for node in method_decl_nodes:
            start_line = node.start_point[0]  # start from 0
            end_line = node.end_point[0]  # end at 0
            if start_line <= error_line - 1 <= end_line:
                if target_method_node is None or target_method_node.startpoint[0] >= start_line:
                    target_method_node = node
        assert target_method_node is not None, f"Cannot find target method containing line {error_line} in {test_file}"
        target_method_name = target_method_node.child_by_field_name("name").text.decode("utf-8")
        edit_method_nodes.append(target_method_node)

        # find enclosing methods that may implicitly invoke the target method
        target_method_names = {target_method_name}
        while target_method_names:
            match_pattern = "|".join(target_method_names)
            target_method_names.clear()
            method_call_query = cls.JAVA_LANGUAGE.query(
                f"""
                (method_invocation
                    name: (identifier) @method_name
                    (#match? @method_name "^({match_pattern})$")
                ) @method_call
                """
            )
            method_call_captures = method_call_query.captures(root_node)
            if not method_call_captures:
                break
            for method_call_node in method_call_captures.get("method_call", []):
                # get the enclosing method node
                parent_node = method_call_node.parent
                while parent_node is not None and parent_node.type != "method_declaration":
                    parent_node = parent_node.parent
                enclosing_method_node = parent_node
                if enclosing_method_node:
                    edit_method_nodes.append(enclosing_method_node)
                    target_method_names.add(enclosing_method_node.child_by_field_name("name").text.decode("utf-8"))

        # edit all methods
        method_sigs_to_fix = set()
        for method_node in edit_method_nodes:
            # only edit the method signature before {
            method_body_node = method_node.child_by_field_name("body")
            body_start = method_body_node.start_byte - method_node.start_byte
            method_sig = method_node.text[:body_start].decode("utf-8").strip()
            method_sigs_to_fix.add(method_sig)
        fixed_code = code
        for method_sig in method_sigs_to_fix:
            fixed_method_sig = method_sig
            if "throws" in method_sig:
                # replace existing throws clause
                fixed_method_sig = re.sub(r"throws.*$", f"throws {default_exception}", method_sig)
            else:
                # add throws clause befor the first {
                fixed_method_sig += f" throws {default_exception}"
            # replace the method code in the original code
            fixed_code = fixed_code.replace(method_sig, fixed_method_sig)

        if do_replace:
            test_file.write_text(fixed_code, encoding="utf-8")
            logger.info(
                f"Fixed unsupported exception in {test_file} at line {error_line} for {len(edit_method_nodes)} methods."
            )

        return fixed_code


if __name__ == "__main__":
    # Example usage
    error_map = {
        "kirin_ws/test_tmp/test/TmpTest.java": """kirin_ws\\test_tmp\\test\\TmpTest.java:6: error: unreported exception ParserConfigurationException; must be caught or declared to be thrown
        factory.setFeature("some.other.feature", true);
                          ^
1 error"""
    }
    TestEditor.fix_general_error(error_map)
