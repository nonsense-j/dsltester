import re
from pathlib import Path

from .parse_dsl import preprocess_dsl
from .prompts import PROMPTS, SYS_PROMPTS

from src.utils.types import TestInfoDict
from src.utils._logger import logger
from src.utils._llm import LLMWrapper
from src.utils._helper import validate_syntax, create_dir_with_path, create_test_info


def fix_syntax_error(test_list: list[str], max_attempts=3) -> list[str]:
    """
    Fix the syntax error in the test cases.
    Args:
        test_list: The test codes to be fixed [may contain syntax errors].
        max_attempts: The maximum number of attempts to fix the syntax error.
    Returns:
        The fixed test code list. Invalid test cases that cannot be fixed are excluded.
    """
    final_test_list = [""] * len(test_list)

    # loop variables
    attempts = 0
    input_test_list = []
    input_base_id_list = []

    # initial checking
    syntax_status_list = validate_syntax(test_list)
    for i in range(len(test_list)):
        if syntax_status_list[i]:
            final_test_list[i] = test_list[i]
        else:
            input_test_list.append(test_list[i])
            input_base_id_list.append(i)

    if len(input_test_list) == 0:
        # [Good] all test cases are valid
        logger.info(f"All test cases are valid, skip syntax errors fixing.")
        return final_test_list
    elif len(input_base_id_list) == 1 and input_base_id_list[0] == len(test_list) - 1:
        # [Trunctuate] if only the last test case is invalid, remove the last one
        logger.info(f"[Detected trunctuation] Only the last test case is invalid, remove it.")
        return final_test_list[:-1]

    while attempts < max_attempts and len(input_test_list) > 0:
        # construct the user prompt
        wrapped_java_code = "\n\n".join([f"```java\n{test_code}\n```" for test_code in input_test_list])
        user_prompt = PROMPTS["fix_syntax_error"].format(
            wrapped_java_code=wrapped_java_code,
        )
        # query the LLM
        llm_response = LLMWrapper.query_llm(user_prompt, query_type="fix_syntax_error")

        # parse the response
        pattern = r"```java\s*(.*?)\s*```"
        output_test_list = re.findall(pattern, llm_response, re.DOTALL)
        output_test_list = [test_case for test_case in output_test_list if test_case.strip() != ""]
        # no output or mismatch, currently assert. TODO)) add retry
        if len(output_test_list) != len(input_test_list):
            attempts += 1
            assert (
                False
            ), f"--> [LLM Output Mismatch] Test count: {len(output_test_list)} != {len(input_test_list)}.LLM output:\n{llm_response}."

        # check the syntax status
        tmp_test_list = []
        tmp_base_id_list = []
        syntax_status_list = validate_syntax(output_test_list)
        for i in range(len(output_test_list)):
            base_i = input_base_id_list[i]
            if syntax_status_list[i]:
                final_test_list[base_i] = output_test_list[i]
            else:
                # if the syntax is still invalid, retry to fix the input test code again
                tmp_test_list.append(input_test_list[i])
                tmp_base_id_list.append(base_i)

        # update
        input_test_list = tmp_test_list
        input_base_id_list = tmp_base_id_list
        attempts += 1
        logger.info(
            f"[SyntaxFix Attempt {attempts}/{max_attempts}] {len(input_test_list)} test cases still have syntax errors."
        )

    # if still has syntax error, just keep the passing test cases
    res = [test for test in final_test_list if test != ""]
    if len(res) < len(test_list):
        logger.warning(f"--> {len(test_list) - len(res)} test cases are skipped for unsolved syntax errors.")
    logger.info(f"Generated {len(res)} valid test cases after syntax fixing.")
    return res


def gen_pos_tests(dsl_text: str, add_info: bool = False) -> TestInfoDict:
    """
    Generate positive test cases for the given DSL.
    Args:
        dsl_text: The input dsl text.
        add_info: Whether to add additional information (node_properties) to the prompt.
    """
    logger.info(f"==> Generating positive test cases")

    # construct the user prompt
    additional_info = ""
    if add_info:
        additional_info_md = Path("src/md/additional_info.md")
        additional_info = additional_info_md.read_text(encoding="utf-8")

    sys_prompt = SYS_PROMPTS["gen_tests"]
    user_prompt = PROMPTS["gen_pos_tests"].format(
        additional_info=additional_info,
        dsl_input=dsl_text,
    )
    # query the LLM
    llm_response = LLMWrapper.query_llm(user_prompt, system_prompt=sys_prompt, query_type="gen_pos_tests")
    logger.debug(f"LLM TestGenerator result: \n{llm_response}")
    # parse the response
    pattern = r"```java\s*(.*?)\s*```"
    test_case_list = re.findall(pattern, llm_response, re.DOTALL)
    test_case_list = [test_case for test_case in test_case_list if test_case.strip() != ""]

    # validate and fix the syntax of the test cases
    test_case_list = fix_syntax_error(test_case_list)

    return create_test_info(test_case_list)


def save_test_info(test_info: TestInfoDict, test_dir: Path) -> None:
    """
    Save the test information to the test directory.
    Args:
        test_info (TestInfoDict): The test information dictionary.
        test_dir (Path): The test directory path.
    """
    if not test_dir.is_dir():
        raise ValueError(f"--> Test directory {test_dir} not found!")
    create_dir_with_path(test_dir, clean=True)

    for label, sub_test_info in test_info.items():
        logger.info(f"Saving {len(sub_test_info)} {label} test cases...")
        for file_stem, test_case_code in sub_test_info:
            test_case_path = test_dir / f"{file_stem}.java"
            test_case_path.write_text(test_case_code, encoding="utf-8")

    logger.info(f"All test cases saved to {test_dir}")
