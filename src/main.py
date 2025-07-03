import json, shutil
from pathlib import Path

from src.tester.build_test import TestCompiler
from src.tester.manage_test import TestManager
from src.tester.validate_test import validate_tests
from src.tester.parse_dsl import preprocess_dsl, save_dsl_prep_res

from src.utils._llm import LLMWrapper
from src.utils.types import DslInfoDict, TestInfoDict
from src.tester.gen_test import gen_checker_tests, refine_checker_tests
from src.utils._logger import logger, set_log_file, unset_log_file
from src.utils._helper import create_dir_with_path, collect_failed_dsl_paths


COMPILATION_FAIL_THRESHOLD = 0.6  # Threshold for test compilation failure ratio
MISMATCH_THRESHOLD = 0.5  # Threshold for test mismatch ratio


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

    # create the dsl directory, must clean
    dsl_ws_dsl_dir = dsl_ws_dir / "dsl"
    create_dir_with_path(dsl_ws_dsl_dir, cleanup=True)

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
    save_dsl_prep_res(dsl_prep_res, dsl_ws_dsl_dir)
    dsl_opp_prep_res = preprocess_dsl(dsl_info["dsl"], init_transform=True, spec_na_strategy=True)
    save_dsl_prep_res(dsl_opp_prep_res, dsl_ws_dsl_dir, is_opposite=True)


def move_non_compilable_tests(failed_test_abspath_strlist: list[str], target_dir: Path):
    """
    Save non-compilable tests to a specified directory.
    :param failed_test_abspath_strlist: List of absolute paths to the failed test files.
    :param target_dir: Directory where the failed tests will be saved.
    """
    if not target_dir.is_dir():
        target_dir.mkdir(parents=True, exist_ok=True)
    # create a subdirectory kirin_ws/{dsl_id}/test-failed/{i} to store failed tests
    target_dir.mkdir(parents=True, exist_ok=True)
    exists_sub_dir_count = len(list(target_dir.glob("*/")))
    failed_tests_sub_dir = target_dir / f"{exists_sub_dir_count + 1}"
    failed_tests_sub_dir.mkdir(parents=True, exist_ok=True)
    logger.info(f"Removing {len(failed_test_abspath_strlist)} non-compiled tests into {target_dir}...")
    for failed_test_str in failed_test_abspath_strlist:
        # move the failed test to the failed tests subdirectory
        failed_test_abspath = Path(failed_test_str)
        test_name = failed_test_abspath.name
        if failed_test_abspath.exists():
            failed_test_abspath.rename(failed_tests_sub_dir / test_name)
        else:
            raise FileNotFoundError(f"Failed test {failed_test_abspath} not found")


def gen_compilable_tests(dsl_id: str, checker_dsl: str, gen_type: str = "all", use_exist_tests: bool = False) -> bool:
    """
    Generate tests and filter non-compiled ones for a single DSL in the tmp/test dir.
    :param dsl_info: The DSL information dictionary containing 'id' and 'dsl'.
    :param gen_type: The type of tests to generate, can be "all", "alerting", or "non-alerting".
    :param use_exist_tests: Whether to use existing tests if available in tmp test dir.
    :return: False if too many non-compilable tests are found, True otherwise.
    """
    assert gen_type in [
        "all",
        "alerting",
        "non-alerting",
    ], f"Invalid gen_type: {gen_type}, should be one of ['all', 'alerting', 'non-alerting']"

    dsl_ws = Path("kirin_ws") / dsl_id

    # create a tmp test dir for this gen_flow
    tmp_ws_test_dir = dsl_ws / "tmp/test"
    tmp_ws_test_dir.mkdir(parents=True, exist_ok=True)
    tmp_test_manager = TestManager(tmp_ws_test_dir)

    test_count = 0  # Record the generated or existed tests
    skip_gen_flag = False  # Flag to indicate if generation should be skipped
    if use_exist_tests:
        tmp_start_id_map = tmp_test_manager.collect_local_start_ids(tmp_ws_test_dir)
        test_count = sum(tmp_start_id_map.values()) - len(tmp_start_id_map)
        if test_count > 0:
            skip_gen_flag = True
            logger.info(f"Found {test_count} existed test cases in {tmp_ws_test_dir}, skip...")
        else:
            logger.info(f"No existed test cases found in {tmp_ws_test_dir}, will generate new tests...")

    # Invoke LLM to generate tests
    if not skip_gen_flag:
        if gen_type == "all":
            alerting_test_list, _ = gen_checker_tests(checker_dsl, gen_type="alerting")
            _, non_alerting_tests = gen_checker_tests(checker_dsl, gen_type="non-alerting")
        else:
            alerting_test_list, non_alerting_tests = gen_checker_tests(checker_dsl, gen_type)
        # alerting_test_list, non_alerting_tests = gen_checker_tests(checker_dsl, gen_type)

        test_info = tmp_test_manager.create_test_info(alerting_test_list, non_alerting_tests)
        if not test_info.get("alerting", []) and not test_info.get("non_alerting", []):
            raise ValueError(f"No test cases generated for DSL {dsl_id} with gen_type {gen_type}. ")

        # update the test case count and save the tests
        test_count = len(test_info["alerting"]) + len(test_info["non_alerting"])
        tmp_test_manager.save_test_info(test_info)

    # try to compile the test cases (mock lib + compile lib + compile test)
    test_compiler = TestCompiler(dsl_id, test_dir=tmp_ws_test_dir, checker_dsl=checker_dsl)
    test_compile_status = test_compiler.build_tests(fix_max_attempts=2)
    # [Verify] Non-compilable tests -> return False (need retry)
    if not test_compile_status:
        compile_fail_ratio = len(test_compiler.failed_tests) / test_count if test_count > 0 else 1
        move_non_compilable_tests(test_compiler.failed_tests, dsl_ws / "test-fail")
        if compile_fail_ratio >= COMPILATION_FAIL_THRESHOLD:
            logger.warning(
                f"Compile fail ratio {compile_fail_ratio:.2f} is too high, consider regenerating test cases."
            )
            return False

    return True


def gen_flow_once(dsl_id: str, checker_dsl: str, gen_type: str = "all", use_exist_tests: bool = False) -> bool:
    """
    Generate tests and validate for a single DSL, including compilation and validation.
    return: status of the validation flow, True if successful, False if failed.
    """
    dsl_ws = Path("kirin_ws") / dsl_id
    tmp_ws_dir = dsl_ws / "tmp"
    tmp_ws_dsl_dir = tmp_ws_dir / "dsl"
    tmp_ws_test_dir = tmp_ws_dir / "test"

    # save current dsl in the tmp dsl dir
    create_dir_with_path(tmp_ws_dsl_dir, cleanup=True)
    (tmp_ws_dsl_dir / f"DSL_ORI.kirin").write_text(checker_dsl, encoding="utf-8")

    # clean up the tmp test dir if use_exist_tests is False
    create_dir_with_path(tmp_ws_test_dir, cleanup=(not use_exist_tests))

    mismatch_max_retries = 1
    gen_flow_status = False
    while not gen_flow_status:
        # generate compilable tests in the tmp test dir
        gen_compile_status = gen_compilable_tests(dsl_id, checker_dsl, gen_type, use_exist_tests)
        if not gen_compile_status:
            return dict()
        tmp_test_manager = TestManager(tmp_ws_test_dir)

        # validate tests in the tmp test dir
        tmp_val_res = validate_tests(dsl_id, val_type="tmp")
        rearraged_test_info, tmp_val_res = tmp_test_manager.rearrange_test_info(tmp_val_res)
        tmp_test_manager.save_test_info(rearraged_test_info)

        # [Verify] Mismatch tests -> Refine test cases
        test_count = sum(list(map(len, rearraged_test_info.values())))
        mismatch_test_count = len(rearraged_test_info.get("mis_alerting", [])) + len(
            rearraged_test_info.get("mis_non_alerting", [])
        )
        mismatch_ratio = mismatch_test_count / test_count if test_count > 0 else 1

        mismatch_type_flag = False  # no alerts or no non-alerts but needed in gen_type
        if gen_type == "all" or gen_type == "alerting":
            mismatch_type_flag = mismatch_type_flag or len(rearraged_test_info.get("alerting", [])) == 0
        if gen_type == "all" or gen_type == "non-alerting":
            mismatch_type_flag = mismatch_type_flag or len(rearraged_test_info.get("non_alerting", [])) == 0

        if mismatch_ratio >= MISMATCH_THRESHOLD or mismatch_type_flag:
            mismatch_max_retries -= 1
            if mismatch_max_retries < 0:
                logger.warning(f"Mismatch ratio {mismatch_ratio:.2f} is too high, but max retries reached, stopping...")
                return False

            logger.warning(f"Mismatch ratio {mismatch_ratio:.2f} is too high, try refining test cases...")
            # clean up the tmp test dir
            create_dir_with_path(tmp_ws_test_dir, cleanup=True)
            # refine the tests
            refined_alerting_test_list = [t[1] for t in rearraged_test_info.get("alerting", [])]
            refined_non_alerting_test_list = [t[1] for t in rearraged_test_info.get("non_alerting", [])]

            if rearraged_test_info.get("mis_non_alerting", []):
                mis_non_alerting_test_list = [t[1] for t in rearraged_test_info["mis_non_alerting"]]
                refined_alerting_tests = refine_checker_tests(
                    mis_non_alerting_test_list, checker_dsl, refine_type="alerting"
                )
                refined_alerting_test_list.extend(refined_alerting_tests)
            if rearraged_test_info.get("mis_alerting", []):
                mis_alerting_test_list = [t[1] for t in rearraged_test_info["mis_alerting"]]
                refined_non_alerting_tests = refine_checker_tests(
                    mis_alerting_test_list, checker_dsl, refine_type="non-alerting"
                )
                refined_non_alerting_test_list.extend(refined_non_alerting_tests)

            refined_test_info = tmp_test_manager.create_test_info(
                alerting_test_list=refined_alerting_test_list,
                non_alerting_test_list=refined_non_alerting_test_list,
            )
            tmp_test_manager.save_test_info(refined_test_info)
            # in the next round, we will use the saved refined tests
            use_exist_tests = True
        else:
            # saving tests to the final test directory and clear tmp test dir
            dsl_ws_test_dir = dsl_ws / "test"
            tmp_test_manager.append_test_info(rearraged_test_info, target_test_dir=dsl_ws_test_dir)
            # shutil.rmtree(tmp_ws_dir)
            gen_flow_status = True
    return gen_flow_status


def gen_flow_regression(dsl_info: DslInfoDict, gen_flow_max_retries: int = 1):
    """
    Generate tests and validate for a single DSL as a regression flow.
    :param dsl_info: The DSL information dictionary containing 'id' and 'dsl'.
    """
    dsl_id = dsl_info["id"]
    dsl_ws = Path("kirin_ws") / dsl_id
    dsl_ws_test_dir = dsl_ws / "test"

    test_count = len(list(dsl_ws_test_dir.rglob("*.java"))) if dsl_ws_test_dir.is_dir() else 0
    if test_count > 0:
        logger.info(f"Found {test_count} existing test directory {dsl_ws_test_dir}, start augmenting...")
    else:
        gen_flow_status = gen_flow_once(dsl_info["id"], dsl_info["dsl"], gen_type="all", use_exist_tests=True)
        while not gen_flow_status and gen_flow_max_retries > 0:
            logger.info(f"==> Retrying test generation for DSL {dsl_id}...")
            gen_flow_status = gen_flow_once(dsl_info["id"], dsl_info["dsl"], gen_type="all", use_exist_tests=False)
            gen_flow_max_retries -= 1

    # validate with the all checker dsls and aggregated tests
    full_val_res = validate_tests(dsl_id, val_type="tmp")

    # scenario-coverage test augmentation
    # failed_dsl_paths = collect_failed_dsl_paths(dsl_id, full_val_res)
    # logger.info(f"Identified {len(failed_dsl_paths)} failed checker DSLs to augment tests.")
    # for i, failed_dsl_path in enumerate(failed_dsl_paths):
    #     failed_dsl = failed_dsl_path.read_text(encoding="utf-8")
    #     logger.info(f"Augmenting tests for [{i+1}/{len(failed_dsl_paths)}] failed DSL: {failed_dsl_path}")
    #     gen_flow_once(dsl_id, failed_dsl, gen_type="alerting", use_exist_tests=False)
    # full_val_res = validate_tests(dsl_id, val_type="all")
    return full_val_res


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
        # if (kirin_ws_dir / dsl_id).is_dir():
        #     logger.info(f"Found existing DSL workspace for {dsl_id}, skip...")
        #     continue

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
