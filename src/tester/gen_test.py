import re
from pathlib import Path

from .parse_dsl import preprocess_dsl
from .prompts import PROMPTS, SYS_PROMPTS

from src.utils.types import TestInfoDict
from src.utils._logger import logger
from src.utils._llm import query_llm


def gen_pos_tests(dsl_text: str) -> TestInfoDict:
    """
    Generate positive test cases for the given DSL.
    Args:
        dsl_text: The input dsl text.
    """
    logger.info(f"==> Generating positive test cases")

    # construct the user prompt
    node_properties_md = Path("src/md/node_properties.md")
    node_properties = node_properties_md.read_text(encoding="utf-8")

    sys_prompt = SYS_PROMPTS["gen_tests"]
    user_prompt = PROMPTS["gen_pos_tests"].format(
        node_properties=node_properties,
        dsl_input=dsl_text,
    )
    # query the LLM
    llm_response = query_llm(user_prompt, system_prompt=sys_prompt)
    # parse the response
    pattern = r"```java(.*?)```"
    test_case_list = re.findall(pattern, llm_response, re.DOTALL)
    test_case_list = [test_case.strip() for test_case in test_case_list if test_case.strip() != ""]

    return TestInfoDict(
        positive=test_case_list,
        negative=[],
        unknown=[],
    )


def save_test_info(test_info: TestInfoDict, test_dir: Path) -> None:
    """
    Save the test information to the test directory.
    Args:
        test_info (TestInfoDict): The test information dictionary.
        test_dir (Path): The test directory path.
    """
    if not test_dir.is_dir():
        raise ValueError(f"--> Test directory {test_dir} not found!")

    for label, test_cases in test_info.items():
        if not test_cases:
            continue
        logger.info(f"Saving {len(test_cases)} {label} test cases...")
        for i, test_case in enumerate(test_cases):
            i += 1
            test_case_path = test_dir / f"{label}_{i}.java"
            test_case_path.write_text(test_case, encoding="utf-8")

    logger.info(f"All test cases saved to {test_dir}")
