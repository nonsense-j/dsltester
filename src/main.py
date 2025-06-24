import json
from pathlib import Path

from src.utils._llm import LLMWrapper
from src.utils.types import DslInfoDict
from src.tester.build_test import TestCompiler
from src.tester.gen_test import gen_checker_tests
from src.tester.validate_test import validate_tests
from src.utils._logger import logger, set_log_file, unset_log_file
from src.tester.parse_dsl import preprocess_dsl, save_dsl_prep_res
from src.utils._helper import (
    create_dir_with_path,
    create_test_info,
    collect_local_start_ids,
    save_test_info,
    rearrage_test_info,
    collect_failed_dsl_paths,
)


def initialize_dsl_ws(dsl_info: DslInfoDict, do_clean_up: bool = False):
    """
    initialize dsl workspace at kirin_ws for folders: dsl, test
    :param dsl_info: dsl info
    :param do_clean_up: whether to clean up the dsl workspace if it already exists
    :return: dsl workspace path
    """
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

    # create the dsl directory and save dsl and sub-dsl files
    dsl_ws_dsl_dir = dsl_ws_dir / "dsl"
    dsl_ws_dsl_dir.mkdir(parents=True, exist_ok=True)

    # create the test directory for generated tests
    dsl_ws_test_dir = dsl_ws_dir / "test"
    dsl_ws_test_dir.mkdir(parents=True, exist_ok=True)


def prep_dsl_dir(dsl_info: DslInfoDict):
    """
    Prepare the DSL directory in the Kirin workspace, including original dsl and parsing sub-dsls.
    """
    dsl_ws_dir = Path("kirin_ws") / dsl_info["id"]
    dsl_ws_dsl_dir = dsl_ws_dir / "dsl"
    assert dsl_ws_dsl_dir.is_dir(), f"DSL directory {dsl_ws_dsl_dir} does not exist!"
    # save the original dsl in the dsl workspace (optional)
    ori_dsl_path = dsl_ws_dsl_dir / f"DSL_ORI.kirin"
    ori_dsl_path.write_text(dsl_info["dsl"], encoding="utf-8")
    # preprocess the dsl (both normal and opposite setting) and save the result
    dsl_prep_res = preprocess_dsl(dsl_info["dsl"])
    save_dsl_prep_res(dsl_prep_res, dsl_ws_dsl_dir / "norm")
    dsl_opp_prep_res = preprocess_dsl(dsl_info["dsl"], init_transform=True)
    save_dsl_prep_res(dsl_opp_prep_res, dsl_ws_dsl_dir / "opp", is_opposite=True)


def gen_flow_once(
    dsl_id: str, checker_dsl: str, gen_type: str = "all", do_test_aug: bool = False, use_exist_tests: bool = False
) -> dict:
    """
    Generate tests and validate for a single DSL as a complete flow.
    :param dsl_info: The DSL information dictionary containing 'id' and 'dsl'.
    :param gen_type: The type of tests to generate, can be "all", "alerting", or "non-alerting".
    :param do_test_aug: Whether to augment tests while keeping existing tests.
    :param use_exist_tests: Whether to use existing tests if available.
    """
    assert gen_type in [
        "all",
        "alerting",
        "non-alerting",
    ], f"Invalid gen_type: {gen_type}, should be one of ['all', 'alerting', 'non-alerting']"

    dsl_ws = Path("kirin_ws") / dsl_id
    dsl_ws_test_dir = dsl_ws / "test"
    test_case_count = len(list(dsl_ws_test_dir.rglob("*.java")))
    if test_case_count > 0 and use_exist_tests:
        logger.info(f"Found {test_case_count} test cases in {dsl_ws_test_dir}, skip...")
    else:
        # if gen_type == "all":
        #     alerting_test_list, _ = gen_checker_tests(checker_dsl, gen_type="alerting")
        #     _, non_alerting_tests = gen_checker_tests(checker_dsl, gen_type="non-alerting")
        # else:
        #     alerting_test_list, non_alerting_tests = gen_checker_tests(checker_dsl, gen_type)
        alerting_test_list, non_alerting_tests = gen_checker_tests(checker_dsl, gen_type)
        if do_test_aug:
            start_ids, mismatch_start_ids = collect_local_start_ids(dsl_ws_test_dir)
            test_info = create_test_info(alerting_test_list, non_alerting_tests, start_ids, mismatch_start_ids)
        else:
            test_info = create_test_info(alerting_test_list, non_alerting_tests)
        assert test_info, f"Failed to generate test cases for DSL {dsl_id}"
        save_test_info(test_info, dsl_ws_test_dir, do_test_aug=do_test_aug)

    # try to compile the test cases (mock lib + compile lib + compile test)
    test_compiler = TestCompiler(dsl_id, checker_dsl=checker_dsl)
    test_compile_status = test_compiler.build_tests(fix_max_attempts=2)
    if not test_compile_status:
        # TODO)) if status is False
        logger.error(f"Compilation failed for DSL {dsl_id}, skip...")
        # continue
        # assert False, f"Compilation failed for DSL {dsl_id}, exit..."
    gen_res = {"BUILD_FAIL_TESTS": test_compiler.failed_tests}

    # validate tests
    dsl_val_res = validate_tests(dsl_id)
    gen_res.update(dsl_val_res)
    # rearrage and save the test info based on validation results
    rearraged_test_info, gen_res = rearrage_test_info(dsl_ws_test_dir, gen_res)
    save_test_info(rearraged_test_info, dsl_ws_test_dir, do_test_aug=do_test_aug)

    return gen_res


def gen_flow_regression(dsl_info: DslInfoDict):
    """
    Generate tests and validate for a single DSL as a regression flow.
    :param dsl_info: The DSL information dictionary containing 'id' and 'dsl'.
    """
    dsl_id = dsl_info["id"]
    dsl_ws = Path("kirin_ws") / dsl_id
    dsl_ws_test_dir = dsl_ws / "test"

    # initial test generation flow
    gen_res = gen_flow_once(dsl_info["id"], dsl_info["dsl"], gen_type="all", use_exist_tests=False)

    # check if non-alerting tests are generated
    # if not gen_res["DSL_ORI"]["pass"]:
    #     gen_res = gen_flow_once(dsl_info["id"], dsl_info["dsl"], gen_type="non-alerting", do_test_aug=True)

    # scenario-coverage test augmentation
    failed_dsl_paths = collect_failed_dsl_paths(dsl_ws_test_dir, gen_res)
    for failed_dsl_path in failed_dsl_paths:
        failed_dsl = failed_dsl_path.read_text(encoding="utf-8")
        logger.info(f"Augmenting tests for failed DSL: {failed_dsl_path}")
        gen_res = gen_flow_once(dsl_id, failed_dsl, gen_type="alerting", do_test_aug=True)

    return gen_res


def main():
    """
    Main function to run the Kirin DSL analysis.
    """
    # Load the dataset
    dataset_path = Path("data/test/test_one.json")
    with open(dataset_path, "r", encoding="utf-8") as f:
        dsl_info_list: list[DslInfoDict] = json.load(f)

    res_path = dataset_path.parent / f"{dataset_path.stem}_result.json"
    final_result = []
    # create the general kirin workspace if not exists
    kirin_ws_dir = Path("kirin_ws")
    if not kirin_ws_dir.is_dir():
        logger.info(f"Creating general kirin workspace at {kirin_ws_dir}")
        kirin_ws_dir.mkdir(parents=True, exist_ok=True)

    for i, dsl_info in enumerate(dsl_info_list):
        logger.info(f"====== Processing DSL #{i + 1}/{len(dsl_info_list)} ======")
        # initialize the DSL workspace and set log file for each dsl
        dsl_id = dsl_info["id"]
        initialize_dsl_ws(dsl_info)
        set_log_file(kirin_ws_dir / dsl_id / f"run.log")

        # prepare kirin_ws/{dsl_id}/dsl
        prep_dsl_dir(dsl_info)

        # [Main] generate tests
        LLMWrapper.reset_single_record()
        gen_res = gen_flow_regression(dsl_info)

        # collect results
        final_result.append({dsl_info["id"]: gen_res})
        with open(res_path, "w", encoding="utf-8") as f:
            json.dump(final_result, f, indent=4, ensure_ascii=False, sort_keys=True)
        logger.info(f"DSL #{i+1} validation result saved to {res_path}")
        LLMWrapper.log_single_record()
        single_record_path = Path("kirin_ws") / dsl_info["id"] / f"llm-record.json"
        with open(single_record_path, "w", encoding="utf-8") as f:
            json.dump(LLMWrapper.single_call_chain, f, indent=4, ensure_ascii=False)
        unset_log_file()

    # save LLM API call record
    LLMWrapper.log_all_record()
    all_llm_record_path = Path("logs") / f"main-{dataset_path.stem}-llm-record.json"
    with open(all_llm_record_path, "w", encoding="utf-8") as f:
        json.dump(LLMWrapper.all_call_chains, f, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    main()
