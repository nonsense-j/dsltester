import json
from pathlib import Path

from src.utils._llm import LLMWrapper
from src.utils.types import DslInfoDict
from src.utils._helper import create_dir_with_path
from src.utils._logger import logger, set_log_file
from src.tester.parse_dsl import preprocess_dsl, save_dsl_prep_res
from src.tester.gen_test import gen_pos_tests, save_test_info
from src.tester.compile_test import TestCompiler
from src.tester.validate_test import validate_tests


def initialize_dsl_ws(dsl_info: DslInfoDict, do_clean_up: bool = False):
    """
    initialize dsl workspace at kirin_ws for folders: dsl, test, report
    :param dsl_info: dsl info
    :param do_clean_up: whether to clean up the dsl workspace if it already exists
    :return: dsl workspace path
    """
    # create the kirin_ws folder if not exists
    kirin_ws_dir = Path("kirin_ws")
    if not kirin_ws_dir.is_dir():
        logger.info(f"Creating kirin workspace at {kirin_ws_dir}")
        kirin_ws_dir.mkdir(parents=True, exist_ok=True)

    # initialize the dsl workspace
    dsl_id = dsl_info["id"]
    dsl_ws_dir = Path("kirin_ws") / dsl_id
    if not dsl_ws_dir.is_dir():
        logger.info(f"Creating dsl workspace at {dsl_ws_dir}")
        dsl_ws_dir.mkdir(parents=True, exist_ok=True)
    else:
        if do_clean_up:
            logger.info(f"Found dsl workspace at {dsl_ws_dir}, do clean up...")
            create_dir_with_path(dsl_ws_dir, cleanup=True)
        else:
            logger.info(f"Found dsl workspace at {dsl_ws_dir}, skip clean up...")

    # save the original dsl in the dsl workspace (optional)
    ori_dsl_path = dsl_ws_dir / f"{dsl_id}.kirin"
    ori_dsl_path.write_text(dsl_info["dsl"], encoding="utf-8")

    # create the dsl directory for dsl preprocess result
    dsl_ws = dsl_ws_dir / "dsl"
    dsl_ws.mkdir(parents=True, exist_ok=True)

    # create the test directory for generated tests
    test_ws = dsl_ws_dir / "test"
    test_ws.mkdir(parents=True, exist_ok=True)

    # create the report directory for kirin reports (must clean)
    report_ws = dsl_ws_dir / "report"
    create_dir_with_path(report_ws, cleanup=True)


def main():
    """
    Main function to run the Kirin DSL analysis.
    """
    # Load the dataset
    dataset_path = Path("data/test/test_one.json")
    with open(dataset_path, "r", encoding="utf-8") as f:
        dsl_info_list: list[DslInfoDict] = json.load(f)

    # set the log path
    main_log_path = Path("logs") / f"main-{dataset_path.stem}.log"
    set_log_file(main_log_path)

    res_path = dataset_path.parent / f"{dataset_path.stem}_result.json"
    final_result = []
    for i, dsl_info in enumerate(dsl_info_list):
        logger.info(f"====== Processing DSL #{i + 1}/{len(dsl_info_list)} ======")
        # reset the LLM API call record for single data item
        LLMWrapper.reset_single_record()
        dsl_id = dsl_info["id"]

        # initialize DSL workspace
        initialize_dsl_ws(dsl_info)

        # preprocess the DSL and save the result
        dsl_ws = Path("kirin_ws") / dsl_id
        dsl_prep_res = preprocess_dsl(dsl_info["dsl"])
        save_dsl_prep_res(dsl_prep_res, dsl_ws / "dsl")

        # generate dsl test
        # Currently, we only generate tests for the first node
        test_dir = dsl_ws / "test"
        test_case_count = len(list(test_dir.rglob("*.java")))
        if test_case_count > 0:
            logger.info(f"Found {test_case_count} test cases in {test_dir}, skip...")
        else:
            input_dsl_text = dsl_prep_res["node_dsl_list"][0]
            test_info = gen_pos_tests(input_dsl_text)
            assert test_info, f"Failed to generate test cases for DSL {dsl_id}"
            save_test_info(test_info, dsl_ws / "test")

        # try to compile the test cases (mock lib + compile lib + compile test)
        test_compiler = TestCompiler(dsl_id)
        test_compile_status = test_compiler.compile_tests(fix_max_attempts=2)
        if not test_compile_status:
            # TODO)) if status is False
            logger.error(f"Compilation failed for DSL {dsl_id}, skip...")
            # continue
            # assert False, f"Compilation failed for DSL {dsl_id}, exit..."

        # validate tests
        res = validate_tests(dsl_id)
        final_result.append({dsl_info["id"]: res})

        with open(res_path, "w", encoding="utf-8") as f:
            json.dump(final_result, f, indent=4, ensure_ascii=False, sort_keys=True)
        logger.info(f"DSL #{i+1} validation result saved to {res_path}")

        LLMWrapper.log_single_record()
        single_record_path = dsl_ws / f"llm-record.json"
        with open(single_record_path, "w", encoding="utf-8") as f:
            json.dump(LLMWrapper.single_call_chain, f, indent=4, ensure_ascii=False)

    # save LLM API call record
    LLMWrapper.log_all_record()
    all_llm_record_path = Path("logs") / f"main-{dataset_path.stem}-llm-record.json"
    with open(all_llm_record_path, "w", encoding="utf-8") as f:
        json.dump(LLMWrapper.all_call_chains, f, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    main()
