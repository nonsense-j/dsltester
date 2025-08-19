import re
from src.utils._llm import LLMWrapper
from src.prompts import PROMPTS


def transform_test(input_code: str) -> list[str]:
    test_wrapper_prefix = "```java"
    test_wrapper_suffix = "```"
    wrapped_test_code = f"{test_wrapper_prefix}\n{input_code}\n{test_wrapper_suffix}"
    user_prompt = PROMPTS["transform_checker_test"].format(seed_program=wrapped_test_code)
    llm_result = LLMWrapper.query_llm(user_prompt, query_type="transform_checker_test")
    # parse the LLM result
    test_mutants = re.findall(rf"{test_wrapper_prefix}(.*?){test_wrapper_suffix}", llm_result, re.DOTALL)
    test_mutants = [mutant.strip() for mutant in test_mutants]
    return test_mutants


if __name__ == "__main__":
    input_code = """\
public class CustomException extends RuntimeException{
    //TARGET_START
    final String customValue;
    //TARGET_END
}
"""
    transformed_tests = transform_test(input_code)
    for i, test in enumerate(transformed_tests):
        print(f"Transformed Test {i + 1}:\n{test}\n{'=' * 40}")
