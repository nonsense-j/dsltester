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

    def __init__(self, test_dir: Path, potential_third_pkgs: list[str] = []):
        self.test_dir = test_dir
        assert test_dir.is_dir(), f"Test directory {test_dir} does not exist!"

        self.test_filepaths = list(test_dir.rglob("*.java"))
        assert len(self.test_filepaths) > 0, f"Test directory {test_dir} does not contain any Java files!"

        # code snippets for all test files
        self.all_test_code = ["\n\n".join([test_file.read_text(encoding="utf-8") for test_file in self.test_filepaths])]

        # potential third-party packages -- additional info to help LLM generate mock lib code
        self.potential_third_pkgs = potential_third_pkgs

    def set_potential_third_pkgs(self, potential_third_pkgs: list[str]):
        self.potential_third_pkgs = potential_third_pkgs

    def gen_mock_lib_code_llm(self, retry_max_attempts: int = 1) -> dict[str, str]:
        """
        Use LLM to get all the mock lib codes for each thir-party package (must mock).
        Before using this function, please make sure that the test code needs mocked lib.
        :param retry_max_attempts: The maximum number of times to retry if parsed nothing.
        :return: {"{class_fqn}": "{mock_code}"}
        """
        logger.info(f"Generating mock lib for {len(self.test_filepaths)} tests in {self.test_dir} using LLM...")

        # construct the user prompt
        additional_info = ""
        if self.potential_third_pkgs:
            additional_info = f"""## Potential Third-party Packages\n{", ".join(self.potential_third_pkgs)}\n\n"""
        prompt = PROMPTS["gen_mock_lib_code"].format(code_snippets=self.all_test_code, additional_info=additional_info)

        for attempts in range(retry_max_attempts + 1):
            if attempts > 0:
                # 0 is the first attempt, others are retries
                logger.warning(
                    f"--> [Detected LLM GenMock Failure] Retrying (attempt {attempts}/{retry_max_attempts})..."
                )
            llm_result = LLMWrapper.query_llm(prompt, query_type="gen_mock_lib_code")
            # parse result
            lib_res = parse_lib_code(llm_result)
            if not lib_res:
                logger.warning(f"--> No third-party dependencies output by LLM.")
            else:
                logger.info(f"Generated {len(lib_res)} third-party classes: \n{', '.join(lib_res.keys())}.")
                return lib_res

        logger.error(
            f"--> [Detected LLM GenMock Failure] failed after {retry_max_attempts} attempts! Please check the LLM output."
        )
        return dict()

    def fix_mock_lib_code(self, lib_res_dict: dict[str, str], error_msg: str) -> dict[str, str]:
        """
        [Once] Fix the mock lib code to make it pass compilation for package.
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

        # parse result
        lib_res = parse_lib_code(llm_result)
        if not lib_res:
            logger.warning(f"No fixed third-party dependencies output by LLM.")
            # logger.warning(f"LLM LibFixer result: \n{llm_result}")
        else:
            logger.info(f"Fixed {len(lib_res)} third-party classes: \n{', '.join(lib_res.keys())}.")

        return lib_res
