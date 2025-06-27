"""
Manage test cases in the folder kirin_ws/{dsl_id}
"""

import re, json
from pathlib import Path

from utils._logger import logger
from utils._helper import create_dir_with_path
from utils.types import TestInfoDict, TestIdxDict


def extract_main_class(test_case: str) -> str:
    """
    extract the main class name.
    :param test_case: test case
    :return: main class name
    """
    # extract the main public class name from the test case
    pattern = r"public\s+class\s+(\w+)"
    match = re.search(pattern, test_case)
    class_name = ""
    if match:
        class_name = match.group(1)
    if not class_name:
        logger.warning(f"--> No public main class found in the test case: {test_case}")
    return class_name


def update_main_class(test_case: str, class_name: str) -> str:
    """
    update the main class name in the test case
    :param test_case: test case
    :param class_name: new class name
    :return: updated test case
    """
    # update the main public class name in the test case
    pattern = r"public\s+(class)\s+\w+"
    # replace the class name with the new class name
    ori_class_name = re.search(pattern, test_case)
    if not ori_class_name:
        logger.error(f"--> No public main class found in the test case: {test_case}")
        return test_case
    else:
        ori_class_name = ori_class_name.group(0)
        new_test_case = test_case.replace(ori_class_name, class_name)
    return new_test_case


class TestManager:
    def __init__(self, test_dir: Path):
        """
        Initialize the TestManager with the test directory.
        :param test_dir: Current test directory path.
        Test folder structure:
            kirin_ws/{dsl_id}/
                ├── alert/
                │   ├── AlertingTest1.java
                │   ├── AlertingTest2.java
                │   ├── MisAlertingTest1.java
                ├── no-alert/
                │   ├── NonAlertingTest1.java
                │   ├── MisNonAlertingTest1.java
        """
        assert test_dir.is_dir(), f"--> Test directory {test_dir} not found!"
        logger.info(f"Initialize TestManager with test directory: {test_dir}")
        self.test_dir = test_dir

    def collect_local_test_info(self) -> TestInfoDict:
        """
        Collect test information from the test directory.
        """
        test_info = TestInfoDict(alerting=[], non_alerting=[], mismatch=[])

        alert_dir = self.test_dir / "alert"
        for test_file in sorted(alert_dir.glob("AlertingTest*.java")):
            test_code = test_file.read_text(encoding="utf-8")
            class_name = test_file.stem
            test_info["alerting"].append((class_name, test_code))

        non_alert_dir = self.test_dir / "no-alert"
        for test_file in sorted(non_alert_dir.glob("NonAlertingTest*.java")):
            test_code = test_file.read_text(encoding="utf-8")
            class_name = test_file.stem
            test_info["non_alerting"].append((class_name, test_code))

        return test_info

    def collect_local_start_ids(self) -> TestIdxDict:
        """
        Collect the start ids for appending alerting, non-alerting, and mismatch tests from the test directory.
        :return: TestIdxDict containing the start ids for alerting, non-alerting, and mismatch tests.
        """
        alerting_count = len(list(self.test_dir.glob("alert/AlertingTest*.java")))
        mismatch_alert_count = len(list(self.test_dir.glob("alert/MisAlertingTest*.java")))
        non_alerting_count = len(list(self.test_dir.glob("no-alert/NonAlertingTest*.java")))
        mismatch_non_alerting_count = len(list(self.test_dir.glob("no-alert/MisNonAlertingTest*.java")))

        return TestIdxDict(
            alerting_id=alerting_count + 1,
            non_alerting_id=non_alerting_count + 1,
            mis_alerting_id=mismatch_alert_count + 1,
            mis_non_alerting_id=mismatch_non_alerting_count + 1,
        )

    def create_test_info(
        self,
        alerting_test_list: list[str],
        non_alerting_test_list: list[str],
        mismatch_alerting_test_list: list[str] = [],
        mismatch_non_alerting_test_list: list[str] = [],
        start_id_map: TestIdxDict = None,
    ) -> TestInfoDict:
        """
        create test info dict with alerting and non-alerting test cases.
        :param alerting_test_list: list of alerting test cases
        :param non_alerting_test_list: list of non-alerting test cases
        :param mismatch_alerting_test_list: list of mismatch alerting test cases
        :param mismatch_non_alerting_test_list: list of mismatch non-alerting test cases
        :param start_id_map: start ids for alerting, non-alerting, mismatch alerting, and mismatch non-alerting tests
        :return: test info dict
        """
        if not alerting_test_list and not non_alerting_test_list:
            logger.warning(f"--> No test cases found! Returning empty test info.")
            return dict()
        if start_id_map is None:
            start_id_map = TestIdxDict(
                alerting_id=1,
                non_alerting_id=1,
                mis_alerting_id=1,
                mis_non_alerting_id=1,
            )
        test_info = TestInfoDict(alerting=[], non_alerting=[])
        for i, test_case in enumerate(alerting_test_list):
            class_name = extract_main_class(test_case)
            expected_class_name = f"AlertingTest{start_id_map['alerting_id'] + i}"
            if class_name != expected_class_name:
                test_case = update_main_class(test_case, expected_class_name)
            test_info["alerting"].append((expected_class_name, test_case))

        for i, test_case in enumerate(non_alerting_test_list):
            class_name = extract_main_class(test_case)
            expected_class_name = f"NonAlertingTest{start_id_map['non_alerting_id'] + i}"
            if class_name != expected_class_name:
                test_case = update_main_class(test_case, expected_class_name)
            test_info["non_alerting"].append((expected_class_name, test_case))

        if mismatch_alerting_test_list:
            test_info["mis_alerting"] = []
            for i, test_case in enumerate(mismatch_alerting_test_list):
                class_name = extract_main_class(test_case)
                expected_class_name = f"MisAlertingTest{start_id_map['mis_alerting_id'] + i}"
                if class_name != expected_class_name:
                    test_case = update_main_class(test_case, expected_class_name)
                test_info["mis_alerting"].append((expected_class_name, test_case))

        if mismatch_non_alerting_test_list:
            test_info["mis_non_alerting"] = []
            for i, test_case in enumerate(mismatch_non_alerting_test_list):
                class_name = extract_main_class(test_case)
                expected_class_name = f"MisNonAlertingTest{start_id_map['mis_non_alerting_id'] + i}"
                if class_name != expected_class_name:
                    test_case = update_main_class(test_case, expected_class_name)
                test_info["mis_non_alerting"].append((expected_class_name, test_case))

        return test_info

    def save_test_info(self, test_info: TestInfoDict, do_test_aug: bool = False) -> None:
        """
        Save the test information to the test directory.
        Args:
            test_info (TestInfoDict): The test information dictionary.
        """
        assert self.test_dir.is_dir(), f"--> Test directory {self.test_dir} not found!"
        if not do_test_aug:
            create_dir_with_path(self.test_dir, cleanup=True)

        for label, sub_test_info in test_info.items():
            logger.info(f"Saving {len(sub_test_info)} {label} test cases...")
            # Alerting/MisAlerting -> alert; NonAlerting/MisNonAlerting -> no-alert
            sub_test_dir = self.test_dir / "no-alert" if "non_alerting" in label else self.test_dir / "alert"
            sub_test_dir.mkdir(parents=True, exist_ok=True)
            for single_test_info in sub_test_info:
                file_stem, test_case_code = single_test_info
                test_case_path = sub_test_dir / f"{file_stem}.java"
                if do_test_aug and test_case_path.exists():
                    logger.warning(f"Test case {test_case_path} already exists, do overwrite.")
                test_case_path.write_text(test_case_code, encoding="utf-8")

        logger.info(f"All test cases saved to {self.test_dir}")

    def rearrange_test_info(self, val_res: dict) -> tuple[TestInfoDict, dict]:
        """
        Rearrange the alert and non-alert sub-dir of the test directory based on the validation result.
        Based on the validation result, move mismatches from alert/no-alert sub-dir and rearrage alerting/non-alerting ones.
        val_res is a dictionary with the following structure:
        {
            "DSL_ORI": {"report": {file_name: [line_numbers]}, "pass": [list of passed files]},
            "DSL_N1": {"report": {file_name: [line_numbers]}, "pass": [list of passed files]},
            ...
        }
        :return: A tuple containing the rearranged test information and the updated generation result.
        """
        assert self.test_dir.is_dir(), f"--> Test directory {self.test_dir} not found!"
        assert "DSL_ORI" in val_res, f"--> DSL_ORI not found in the generation result {val_res}"
        logger.info("Rearranging test directory based on generation result...")

        true_alerting_tests = []
        true_non_alerting_tests = []
        mismatch_alerting_tests = [
            p.read_text(encoding="utf-8") for p in sorted(self.test_dir.glob("alert/MisAlerting*.java"))
        ]
        mismatch_non_alerting_tests = [
            p.read_text(encoding="utf-8") for p in sorted(self.test_dir.glob("no-alert/MisNonAlerting*.java"))
        ]
        test_change_map = dict()
        mis_alerting_count = 0
        mis_non_alerting_count = 0

        for alerting_file in val_res["DSL_ORI"]["report"].keys():
            if alerting_file.startswith("Alerting"):
                alerting_test_code = (self.test_dir / "alert" / alerting_file).read_text(encoding="utf-8")
                true_alerting_tests.append(alerting_test_code)
                new_alerting_file = f"AlertingTest{len(true_alerting_tests)}.java"
                if alerting_file != new_alerting_file:
                    test_change_map[alerting_file] = new_alerting_file
            elif alerting_file.startswith("NonAlerting"):
                alerting_test_code = (self.test_dir / "no-alert" / alerting_file).read_text(encoding="utf-8")
                mismatch_alerting_tests.append(alerting_test_code)
                test_change_map[alerting_file] = f"MisAlertingTest{len(mismatch_alerting_tests)}.java"
                mis_alerting_count += 1
            else:
                continue

        for non_alerting_file in val_res["DSL_ORI"]["pass"]:
            if non_alerting_file.startswith("NonAlerting"):
                non_alerting_test_code = (self.test_dir / "no-alert" / non_alerting_file).read_text(encoding="utf-8")
                true_non_alerting_tests.append(non_alerting_test_code)
                new_non_alerting_file = f"NonAlertingTest{len(true_non_alerting_tests)}.java"
                if non_alerting_file != new_non_alerting_file:
                    test_change_map[non_alerting_file] = new_non_alerting_file
            elif non_alerting_file.startswith("Alerting"):
                non_alerting_test_code = (self.test_dir / "alert" / non_alerting_file).read_text(encoding="utf-8")
                mismatch_non_alerting_tests.append(non_alerting_test_code)
                test_change_map[non_alerting_file] = f"MisNonAlertingTest{len(mismatch_non_alerting_tests)}.java"
                mis_non_alerting_count += 1
            else:
                continue

        logger.info(
            f"Rearrage result: identified {mis_alerting_count} MismatchAlerting and {mis_non_alerting_count} Mismatch-Non-Alerting."
        )
        rearraged_test_info = self.create_test_info(
            alerting_test_list=true_alerting_tests,
            non_alerting_test_list=true_non_alerting_tests,
            mismatch_alerting_test_list=mismatch_alerting_tests,
            mismatch_non_alerting_test_list=mismatch_non_alerting_tests,
        )

        val_res_str = json.dumps(val_res)
        pattern = re.compile("|".join(re.escape(k) for k in sorted(test_change_map, key=len, reverse=True)))
        new_val_res_str = pattern.sub(lambda m: test_change_map[m.group(0)], val_res_str)
        new_val_res = json.loads(new_val_res_str)

        return rearraged_test_info, new_val_res
