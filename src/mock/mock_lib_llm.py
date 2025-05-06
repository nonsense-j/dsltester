"""
[Slower]
This module is used to generate mock libraries for third-party packages using LLM.
"""

import re
from pathlib import Path

from src.tester.prompts import PROMPTS
from src.utils._logger import logger
from src.utils._llm import query_llm


def extract_pkg_and_class_name(java_code: str):
    pkg_name = None
    class_name = None

    pkg_match = re.search(r"^\s*package\s+([a-zA-Z0-9_.]+);", java_code, re.MULTILINE)
    if pkg_match:
        pkg_name = pkg_match.group(1)

    class_match = re.search(r"^\s*public\s+class\s+([a-zA-Z_$][a-zA-Z0-9_$]*)", java_code, re.MULTILINE)
    if class_match:
        class_name = class_match.group(1)

    return pkg_name, class_name


def gen_mock_lib_code_llm(test_dir: Path) -> dict[str, str]:
    """
    Use LLM to get all the mock lib codes for each thir-party package.
    :param test_dir: The directory containing the test cases.
    :return: {"{class_fqn}": "{mock_code}"}
    """
    assert test_dir.is_dir(), f"Test directory {test_dir} does not exist!"
    # read all the test cases
    all_test_files = list(test_dir.glob("*.java"))
    if len(all_test_files) == 0:
        logger.warning(f"--> No test cases are found in {test_dir}!")
        return dict()

    logger.info(f"Generating mock lib for {len(all_test_files)} test cases in {test_dir}...")
    code_snippets = ""
    for test_file in all_test_files:
        with open(test_file, "r", encoding="utf-8") as f:
            code_snippets += f.read() + "\n\n"

    # construct the user prompt
    prompt = PROMPTS["gen_mock_lib_code"].format(code_snippets=code_snippets)
    llm_result = query_llm(prompt)
    logger.debug(f"LLM LibGenerator result: \n{llm_result}")

    # parse result
    pattern = r"```java(.*?)```"
    lib_code_list = re.findall(pattern, llm_result, re.DOTALL)

    res = {}
    for lib_code in lib_code_list:
        lib_code = lib_code.strip()
        pkg_name, class_name = extract_pkg_and_class_name(lib_code)

        # pkg_name and class_name should not be None
        assert pkg_name is not None, f"Package name not found in the mock code: {lib_code}"
        assert class_name is not None, f"Class name not found in the mock code: {lib_code}"

        if pkg_name and class_name:
            class_fqn = f"{pkg_name}.{class_name}"
            # check for duplicate class names
            assert class_fqn not in res, f"Duplicate class name {class_fqn} found in the mock code!"
            res[class_fqn] = lib_code

    logger.info(f"Generated {len(res)} mock lib codes: \n{', '.join(list(res.keys()))}")

    return res
