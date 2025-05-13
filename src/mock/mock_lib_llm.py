"""
[Slower but sounder]
This module is used to generate mock libraries for third-party packages using LLM.
"""

import re
from pathlib import Path

from src.tester.prompts import PROMPTS
from src.utils._logger import logger
from src.utils._llm import LLMWrapper
from src.utils._helper import is_third_class, parse_lib_code


class MockLibGenLLM:
    """
    A wrapper class for LLM to generate mock libraries for third-party packages.
    """

    def __init__(self, test_dir: Path):
        self.test_dir = test_dir
        assert test_dir.is_dir(), f"Test directory {test_dir} does not exist!"

        self.test_filepaths = list(test_dir.rglob("*.java"))
        assert len(self.test_filepaths) > 0, f"Test directory {test_dir} does not contain any Java files!"

        # code snippets for all test files
        self.all_test_code = ""
        for test_file in self.test_filepaths:
            self.all_test_code += test_file.read_text(encoding="utf-8") + "\n\n"

    def gen_mock_lib_code_llm_once(self) -> tuple[bool, dict[str, str]]:
        """
        Use LLM to get all the mock lib codes for each thir-party package.
        :return: {"{class_fqn}": "{mock_code}"}
        """
        logger.info(f"Generating mock lib for {len(self.test_filepaths)} tests in {self.test_dir} using LLM...")

        # construct the user prompt
        prompt = PROMPTS["gen_mock_lib_code"].format(code_snippets=self.all_test_code)
        llm_result = LLMWrapper.query_llm(prompt, query_type="gen_mock_lib_code")
        logger.debug(f"LLM LibGenerator result: \n{llm_result}")

        # parse result
        if "Pass: no third-party libraries are used" in llm_result:
            return True, dict()
        res_status, lib_res = parse_lib_code(llm_result)

        fqn_list = list(lib_res.keys())
        logger.info(f"Generated {len(lib_res)} mock lib codes: \n{', '.join(fqn_list)}")

        return res_status, lib_res

    def gen_mock_lib_code_llm(self, retry_max_attempts: int = 0) -> tuple[bool, dict[str, str]]:
        """
        Retry the LLM generation for mock lib code.
        :param test_dir: The directory containing the test cases.
        :param retry_max_attempts: The maximum number of times to retry.
        :return: {"{class_fqn}": "{mock_code}"}
        """
        res_status, lib_res = self.gen_mock_lib_code_llm_once()
        if res_status:
            return res_status, lib_res
        else:
            # retry if the result is empty
            for attempt in range(1, retry_max_attempts + 1):
                logger.warning(
                    f"--> [Detected LLM GenMock Failure]Retrying... (attempt {attempt}/{retry_max_attempts})"
                )
                res_status, lib_res = self.gen_mock_lib_code_llm_once()
                if res_status:
                    return res_status, lib_res
        # TODO)) return False instead of raising an error
        # return False, lib_res
        raise AssertionError(f"LLM GenMock failed after {retry_max_attempts} attempts! Please check the LLM output.")

    def fix_mock_lib_code(self, lib_res_dict: dict[str, str], error_msg: str) -> dict[str, str]:
        """
        Fix the mock lib code to make it pass compilation for package.
        :param lib_res_dict: The dictionary containing the mock lib code.
        :param error_msg: The error message from the compilation.
        :return: {"{class_fqn}": "{mock_code}"}
        """
        # construct the messages
        gen_mock_in = PROMPTS["gen_mock_lib_code"].format(code_snippets=self.all_test_code)
        gen_mock_out = ""
        for class_fqn, lib_code in lib_res_dict.items():
            gen_mock_out += f"<lib-{class_fqn}>\n{lib_code}\n</lib-{class_fqn}>\n"
        fix_in = PROMPTS["fix_mock_lib_code"].format(error_msg=error_msg)

        messages = [
            {"role": "user", "content": gen_mock_in},
            {"role": "assistant", "content": gen_mock_out},
            {"role": "user", "content": fix_in},
        ]
        llm_result = LLMWrapper.query_llm_with_msg(messages=messages, query_type="fix_mock_lib_code")
        logger.debug(f"LLM LibFixer result: \n{llm_result}")

        # parse result
        res_status, lib_res = parse_lib_code(llm_result)
        # return False instead of raising an error
        assert res_status, f"LLM FixMock failed! Please check the LLM output: \n{llm_result}"

        return res_status, lib_res
