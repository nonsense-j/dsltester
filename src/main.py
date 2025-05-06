import json
from pathlib import Path

from src.utils._logger import logger
from src.utils.types import DslInfoDict
from src.utils._helper import create_dir_with_path
from src.tester.parse_dsl import preprocess_dsl, save_dsl_prep_res
from src.tester.gen_test import gen_pos_tests, save_test_info
from src.tester.mock_jar import gen_mock_jar
from src.tester.validate_test import validate_tests


def initialize_dsl_ws(dsl_info: DslInfoDict):
    """
    initialize dsl workspace at kirin_ws for folders: dsl, test, report
    :param dsl_info: dsl info
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
    else:
        logger.info(f"Found dsl workspace at {dsl_ws_dir}, do clean up...")
    create_dir_with_path(dsl_ws_dir, cleanup=True)

    # save the original dsl in the dsl workspace (optional)
    ori_dsl_path = dsl_ws_dir / f"{dsl_id}.kirin"
    ori_dsl_path.write_text(dsl_info["dsl"], encoding="utf-8")

    # create the dsl directory for dsl preprocess result
    dsl_ws = dsl_ws_dir / "dsl"
    create_dir_with_path(dsl_ws)

    # create the test directory for generated tests
    test_ws = dsl_ws_dir / "test"
    create_dir_with_path(test_ws)

    # create the report directory for kirin reports
    report_ws = dsl_ws_dir / "report"
    create_dir_with_path(report_ws)


def main():
    """
    Main function to run the Kirin DSL analysis.
    """
    # Load the dataset
    dataset_path = Path("data/test.json")
    with open(dataset_path, "r") as f:
        dsl_info_list: list[DslInfoDict] = json.load(f)

    final_result = []
    for i, dsl_info in enumerate(dsl_info_list):
        logger.info(f"====== Processing DSL #{i + 1}/{len(dsl_info_list)} ======")
        dsl_id = dsl_info["id"]

        # # initialize DSL workspace
        # initialize_dsl_ws(dsl_info)

        # # preprocess the DSL and save the result
        # dsl_ws = Path("kirin_ws") / dsl_id
        # dsl_prep_res = preprocess_dsl(dsl_info["dsl"])
        # save_dsl_prep_res(dsl_prep_res, dsl_ws / "dsl")

        # # generate dsl test
        # # Currently, we only generate tests for the first node
        # input_dsl_text = dsl_prep_res["node_dsl_list"][0]
        # test_info = gen_pos_tests(input_dsl_text)

        # # save the test info and generate mock jar
        # save_test_info(test_info, dsl_ws / "test")
        # gen_mock_jar(dsl_id)

        # validate tests
        validate_tests(dsl_id)


if __name__ == "__main__":
    main()
