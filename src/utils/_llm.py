import time
from openai import OpenAI
from typing import Optional

from .config import OPENAI_BASE_URL, OPENAI_MODEL_NAME, OPENAI_API_KEY
from ._logger import logger


def query_llm_v1(messages: list, model_name: str = OPENAI_MODEL_NAME) -> str:
    """
    Query LLM with openai API
    """
    assert model_name, f"Model name {model_name} not provided"

    client = OpenAI(base_url=OPENAI_BASE_URL, api_key=OPENAI_API_KEY)
    chat_completion = client.chat.completions.create(model=model_name, messages=messages, temperature=0.7, stream=False)
    # prompt_tokens = chat_completion.usage.prompt_tokens
    # completion_tokens = chat_completion.usage.completion_tokens
    response = chat_completion.choices[0].message.content

    if "QWQ" in model_name or "Qwen" in model_name:
        # skip thinking
        response = response.split("</think>")[-1].strip()

    return response


class LLMWrapper:
    """
    A wrapper class for LLM API calls.
    """

    # record the number of API calls and timestamps
    single_call_chain: list[tuple[str, int]] = []
    all_call_chains: list[list[tuple[str, int]]] = []

    @classmethod
    def reset_all_record(cls) -> None:
        """
        Reset the number of API calls made.
        """
        cls.single_call_chain.clear()
        cls.all_call_chains.clear()

    @classmethod
    def reset_single_record(cls) -> None:
        """
        Reset the number of API calls made for a single data item.
        """
        cls.single_call_chain.clear()

    @classmethod
    def query_llm_with_msg(cls, messages: list[dict], query_type: str = "default") -> str:
        """
        [Entrance] Query LLM with user prompt and system prompt
        """
        start_time = time.time()
        res = query_llm_v1(messages)
        end_time = time.time()
        time_cost = int(end_time - start_time)
        logger.info(f"LLM Timestamp Record: {time_cost} seconds")

        # update LLM record
        if not cls.single_call_chain:
            cls.all_call_chains.append([])
        call_record = (query_type, time_cost)
        cls.single_call_chain.append(call_record)
        cls.all_call_chains[-1].append(call_record)

        return res

    @classmethod
    def query_llm(cls, user_prompt: str, system_prompt: Optional[str] = None, query_type: str = "default") -> str:
        """
        [Entrance] Query LLM with user prompt and system prompt
        """
        assert len(cls.single_call_chain) <= 3, f"--> [LLM] API call limit reached: {len(cls.single_call_chain)}."
        if system_prompt is None:
            messages = [{"role": "user", "content": user_prompt}]
        else:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ]
        return cls.query_llm_with_msg(messages, query_type=query_type)

    @classmethod
    def log_single_record(cls) -> None:
        """
        Log the single record of API calls.
        """
        wrapper = "*****" * 8
        full_record_str = f"\n{wrapper}\n"
        full_record_str += f"==> Single LLM API Call Record (#{len(cls.single_call_chain)}):\n"
        full_record_str += ", ".join(str(record) for record in cls.single_call_chain)
        full_record_str += f"\n{wrapper}"
        logger.info(full_record_str)

    @classmethod
    def log_all_record(cls) -> None:
        """
        Log all records of API calls.
        """
        wrapper = "*****" * 8
        call_count_list = list(map(len, cls.all_call_chains))
        full_record_str = f"\n{wrapper}\n"
        full_record_str += f"==> All LLM API Call Record (#{sum(call_count_list)}):\n"
        full_record_str += ", ".join([str(count) for count in call_count_list])
        full_record_str += f"\n{wrapper}"
        logger.info(full_record_str)


if __name__ == "__main__":
    # Test the query_llm function
    user_prompt = "Who are you?"
    response = LLMWrapper.query_llm(user_prompt)
    print(response)
    LLMWrapper.log_single_record()
    LLMWrapper.log_all_record()
