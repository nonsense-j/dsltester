import re
from pathlib import Path

from src.prompts import PROMPTS, SYS_PROMPTS
from src.utils._logger import logger
from src.utils._llm import LLMWrapper
from src.utils._helper import validate_syntax


def fix_syntax_error(test_list: list[str], max_attempts=1) -> list[str]:
    """
    Fix the syntax error in the test cases.
    Args:
        test_list: The test codes to be fixed [may contain syntax errors].
        max_attempts: The maximum number of attempts to fix the syntax error (retry and iterative fix).
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
        attempts += 1
        logger.warning(f"--> [Detected SyntaxError] Try LLM SyntaxFix (attempt {attempts}/{max_attempts})...")
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
        # no output or mismatch, currently assert, continue to retry
        if len(output_test_list) != len(input_test_list):
            logger.warning(
                f"--> LLM SyntaxFix Output test count mismatches: {len(output_test_list)} != {len(input_test_list)}."
            )
            continue

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

    # if still has syntax error, just keep the passing test cases
    res = [test for test in final_test_list if test != ""]
    if len(res) < len(test_list):
        logger.warning(f"--> {len(test_list) - len(res)} test cases are skipped for unsolved syntax errors.")
    logger.info(f"Keep {len(res)} valid test cases after syntax fixing.")
    return res


def extract_checker_tests(llm_output: str) -> tuple[list[str], list[str]]:
    """
    extract alerting and non-alerting test cases from the LLM output.
    """
    alert_pattern = r"<alerting_test>\s*(.*?)\s*</alerting_test>"
    alerting_test_list = re.findall(alert_pattern, llm_output, re.DOTALL)
    alerting_test_list = [test_case for test_case in alerting_test_list if test_case.strip() != ""]
    if alerting_test_list:
        alerting_test_list = fix_syntax_error(alerting_test_list)

    non_alert_pattern = r"<non_alerting_test>\s*(.*?)\s*</non_alerting_test>"
    non_alerting_test_list = re.findall(non_alert_pattern, llm_output, re.DOTALL)
    non_alerting_test_list = [test_case for test_case in non_alerting_test_list if test_case.strip() != ""]
    if non_alerting_test_list:
        non_alerting_test_list = fix_syntax_error(non_alerting_test_list)

    return alerting_test_list, non_alerting_test_list


def gen_checker_tests(
    checker_dsl: str,
    gen_type: str = "all",
    add_info: bool = True,
    retry_max_attempts: int = 1,
) -> tuple[list[str], list[str]]:
    """
    Generate test cases for the given Checker DSL.
    Args:
        checker_dsl: The Checker DSL to generate tests for.
        gen_type: The type of tests to generate, can be "all", "alerting", or "non-alerting".
        add_info: Whether to add additional information (node_properties) to the prompt.
        do_test_aug: Whether to augment tests while keeping existing tests.
        retry_max_attempts: The maximum number of attempts to retry if parsed nothing.
    Returns:
        alerting_test_list: A list of alerting test cases.
        non_alerting_test_list: A list of non-alerting test cases.
    """
    assert gen_type in [
        "all",
        "alerting",
        "non-alerting",
    ], f"Invalid gen_test type: {gen_type}, should be one of ['all', 'alerting', 'non-alerting']"
    logger.info(f"==> Generating {gen_type} test cases")

    # construct the user prompt
    additional_info = ""
    if add_info:
        additional_info_md = Path("src/resources/additional_info.md")
        additional_info = additional_info_md.read_text(encoding="utf-8")

    sys_prompt = SYS_PROMPTS["gen_tests"]
    prompt_map = {
        "all": "gen_all_tests",
        "alerting": "gen_alerting_tests",
        "non-alerting": "gen_non_alerting_tests",
    }
    query_type = prompt_map[gen_type]
    user_prompt = PROMPTS[query_type].format(
        additional_info=additional_info,
        checker_dsl=checker_dsl,
    )

    for attempt in range(retry_max_attempts + 1):
        if attempt > 0:
            # 0 is the first attempt, others are retries
            logger.warning(f"--> [Detected LLM GenTest Failure] Retrying (attempt {attempt}/{retry_max_attempts})...")
        # query the LLM
        llm_response = LLMWrapper.query_llm(user_prompt, system_prompt=sys_prompt, query_type=query_type)
        logger.debug(f"LLM TestGenerator result: \n{llm_response}")
        # parse the response
        alerting_test_list, non_alerting_test_list = extract_checker_tests(llm_response)
        if gen_type in ["alerting", "all"] and len(alerting_test_list) == 0:
            logger.error(
                f"--> [Detected LLM GenTest Failure] No Alerting test cases generated! Please check the LLM output."
            )
        elif gen_type in ["non-alerting", "all"] and len(non_alerting_test_list) == 0:
            logger.error(
                f"--> [Detected LLM GenTest Failure] No Non-Alerting test cases generated! Please check the LLM output."
            )
        else:
            return alerting_test_list, non_alerting_test_list

    logger.error(
        f"--> [Detected LLM GenTest Failure] failed after {retry_max_attempts} attempts! Please check the LLM output."
    )
    return [], []


def refine_checker_tests(
    mismatch_test_list: list[str],
    checker_dsl: str,
    refine_type: str,
    add_info: bool = True,
    retry_max_attempts: int = 1,
) -> list[str]:
    """
    Refine the generated test cases by checking the syntax and removing invalid ones.
    """
    assert refine_type in [
        "alerting",
        "non-alerting",
    ], f"Invalid refine type: {refine_type}, should be one of ['alerting', 'non-alerting']"
    logger.info(f"==> Refining {len(mismatch_test_list)} test cases to be {refine_type} test cases")
    prompt_map = {
        "alerting": "refine_alerting_tests",
        "non-alerting": "refine_non_alerting_tests",
    }
    # construct the user prompt
    additional_info = ""
    if add_info:
        additional_info_md = Path("src/resources/additional_info.md")
        additional_info = additional_info_md.read_text(encoding="utf-8")

    test_wrapper = "alerting_test" if refine_type == "alerting" else "non_alerting_test"
    user_prompt = PROMPTS[prompt_map[refine_type]].format(
        checker_dsl=checker_dsl,
        additional_info=additional_info,
        wrapped_tests="\n\n".join(
            [f"<{test_wrapper}>\n{test_code}\n</{test_wrapper}>" for test_code in mismatch_test_list]
        ),
    )

    for attempt in range(retry_max_attempts + 1):
        if attempt > 0:
            # 0 is the first attempt, others are retries
            logger.warning(
                f"--> [Detected LLM RefineTest Failure] Retrying (attempt {attempt}/{retry_max_attempts})..."
            )
        # query the LLM
        llm_response = LLMWrapper.query_llm(user_prompt, query_type=prompt_map[refine_type])
        logger.debug(f"LLM RefineTests result: \n{llm_response}")

        # parse the response with test_wrapper
        pattern = rf"<{test_wrapper}>\s*(.*?)\s*</{test_wrapper}>"
        refined_test_list = re.findall(pattern, llm_response, re.DOTALL)
        refined_test_list = [test_case for test_case in refined_test_list if test_case.strip() != ""]

        if refined_test_list:
            return refined_test_list

    return []
