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
                    default_e = "Exception" if exception_name.endswith("Exception") else "Error"
                    cls.fix_unsupported_exception(test_file, line_number, default_exception=default_e, do_replace=True)
                else:
                    logger.error(f"Test file {file_name} does not exist.")
        if do_fix_flag:
            logger.info("Finish Fixing general errors in test files.")
        else:
            logger.info("No general errors found in test files, skipping.")
        return do_fix_flag

    @classmethod
    def fix_unsupported_exception(
        cls, test_file: Path, error_line: int, default_exception="Exception", do_replace=False
    ) -> str:
        """
        Fix unsupported exception in the test file by adding "throws Exception" or "throws Error" to the method containing the error.
        :param test_file: Path to the test file.
        :param error_line: The line containing the compilation error. (starting from 1)
        :return: The transformed code with the exception fixed.
        """
        # Parse the test file
        with open(test_file, "r", encoding="utf-8") as f:
            code = f.read()
        fixed_code = ""

        # Find the method node containing the specified line number
        tree = cls.parser.parse(bytes(code, "utf8"))
        root_node = tree.root_node
        method_decl_query = cls.JAVA_LANGUAGE.query(
            """
            (method_declaration) @method_decl
            """
        )
        captures = method_decl_query.captures(root_node)
        for node in captures.get("method_decl", []):
            start_line = node.start_point[0]  # start from 0
            end_line = node.end_point[0]  # end at 0
            if start_line <= error_line - 1 <= end_line:
                # substitute existing throws clause as default and add the default exception
                method_code = node.text.decode("utf-8")
                if "throws" in method_code:
                    # replace existing throws clause
                    fixed_method_code = re.sub(r"throws\s+\w+", f"throws {default_exception}", method_code)
                else:
                    # add throws clause befor the first {
                    fixed_method_code = re.sub(
                        r"^([^{]*)\{",
                        lambda m: f"{m.group(1).rstrip()} throws {default_exception} {{",
                        method_code,
                        count=1,
                    )
                # replace the method code in the original code
                fixed_code = code.replace(method_code, fixed_method_code)

                if do_replace:
                    test_file.write_text(fixed_code, encoding="utf-8")
                    logger.info(f"Fixed unsupported exception in {test_file} at line {error_line}.")

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
