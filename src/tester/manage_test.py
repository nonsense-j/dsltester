"""
Manage test cases in the folder kirin_ws/{dsl_id}
"""

import re, json
from pathlib import Path

from src.utils._logger import logger
from src.utils._helper import create_dir_with_path
from src.utils.types import TestInfoDict, TestIdxDict


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
    pattern = r"public.+class\s+(\w+)\s+{"
    # replace the class name with the new class name
    ori_class_name = re.search(pattern, test_case)
    if not ori_class_name:
        logger.error(f"--> No public main class found in the test case: {test_case}")
        return test_case
    else:
        ori_class_name = ori_class_name.group(1)
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

    def collect_local_start_ids(self, test_dir: Path = None) -> TestIdxDict:
        """
        Collect the start ids for appending alerting, non-alerting, and mismatch tests from the test directory.
        :return: TestIdxDict containing the start ids for alerting, non-alerting, and mismatch tests.
        """
        if not test_dir:
            test_dir = self.test_dir
        alerting_count = len(list(test_dir.glob("alert/AlertingTest*.java")))
        mismatch_alert_count = len(list(test_dir.glob("alert/MisAlertingTest*.java")))
        non_alerting_count = len(list(test_dir.glob("no-alert/NonAlertingTest*.java")))
        mismatch_non_alerting_count = len(list(test_dir.glob("no-alert/MisNonAlertingTest*.java")))
        logger.info(
            f"Found existed tests: alerting({alerting_count}), non-alerting({non_alerting_count}), mis_alerting({mismatch_alert_count}), mis_non_alerting=({mismatch_non_alerting_count})"
        )

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
        append_test_dir: Path = None,
    ) -> TestInfoDict:
        """
        create test info dict with alerting and non-alerting test cases.
        If do_test_aug is True, tests will be named from 1.
        If do_test_aug is False, tests will be named from the current count in the test directory.
        :param alerting_test_list: list of alerting test cases
        :param non_alerting_test_list: list of non-alerting test cases
        :param mismatch_alerting_test_list: list of mismatch alerting test cases
        :param mismatch_non_alerting_test_list: list of mismatch non-alerting test cases
        :param append_test_dir: whether to augment the test cases with new ids (start id from collect_local_start_ids)
        :return: test info dict
        """
        test_info = TestInfoDict(alerting=[], non_alerting=[])
        # set start ids for all types of tests
        if append_test_dir:
            start_id_map = self.collect_local_start_ids(append_test_dir)
            logger.info(
                f"Appending test cases with start ids: {start_id_map['alerting_id']}, {start_id_map['non_alerting_id']}, "
                f"{start_id_map['mis_alerting_id']}, {start_id_map['mis_non_alerting_id']}"
            )
        else:
            start_id_map = TestIdxDict(
                alerting_id=1,
                non_alerting_id=1,
                mis_alerting_id=1,
                mis_non_alerting_id=1,
            )

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

    def save_test_info(self, test_info: TestInfoDict, append_test_dir: Path = None) -> None:
        """
        Save the test information to the test directory from scratch.
        Each time, the test dir will be cleaned up and recreated.
        Args:
            test_info (TestInfoDict): The test information dictionary.
            do_test_aug (bool): Whether to add the test cases without cleanning existing ones.
        """
        assert self.test_dir.is_dir(), f"--> Test directory {self.test_dir} not found!"

        if not append_test_dir:
            test_dir = self.test_dir
            create_dir_with_path(self.test_dir, cleanup=True)
        else:
            test_dir = append_test_dir
            logger.info(f"Appending test information to {append_test_dir} without cleanup.")

        for label, sub_test_info in test_info.items():
            logger.info(f"Saving {len(sub_test_info)} {label} test cases...")
            # Alerting/MisAlerting -> alert; NonAlerting/MisNonAlerting -> no-alert
            sub_test_dir = test_dir / "no-alert" if "non_alerting" in label else test_dir / "alert"
            sub_test_dir.mkdir(parents=True, exist_ok=True)
            for single_test_info in sub_test_info:
                file_stem, test_case_code = single_test_info
                test_case_path = sub_test_dir / f"{file_stem}.java"
                test_case_path.write_text(test_case_code, encoding="utf-8")

        logger.info(f"All test cases have saved to {test_dir}.")

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

        true_alerting_test_info = []
        true_non_alerting_test_info = []
        mis_alerting_test_info = [
            (p.stem, p.read_text(encoding="utf-8")) for p in sorted(self.test_dir.glob("alert/MisAlerting*.java"))
        ]
        mis_non_alerting_test_info = [
            (p.stem, p.read_text(encoding="utf-8")) for p in sorted(self.test_dir.glob("no-alert/MisNonAlerting*.java"))
        ]

        test_change_map = dict()
        mis_alerting_count = 0
        mis_non_alerting_count = 0

        for alerting_file in val_res["DSL_ORI"]["report"].keys():
            # true alerting test cases
            if alerting_file.startswith("Alerting"):
                alerting_test_code = (self.test_dir / "alert" / alerting_file).read_text(encoding="utf-8")
                new_alerting_file = f"AlertingTest{len(true_alerting_test_info) + 1}.java"
                true_alerting_test_info.append((Path(new_alerting_file).stem, alerting_test_code))
                if alerting_file != new_alerting_file:
                    test_change_map[alerting_file] = new_alerting_file
            # mismatch alerting test cases
            elif alerting_file.startswith("NonAlerting"):
                alerting_test_code = (self.test_dir / "no-alert" / alerting_file).read_text(encoding="utf-8")
                new_file_name = f"MisAlertingTest{len(mis_alerting_test_info) + 1}.java"
                test_change_map[alerting_file] = new_file_name
                mis_alerting_test_info.append((Path(new_file_name).stem, alerting_test_code))
                mis_alerting_count += 1
            else:
                continue

        for non_alerting_file in val_res["DSL_ORI"]["pass"]:
            # true non-alerting test cases
            if non_alerting_file.startswith("NonAlerting"):
                non_alerting_test_code = (self.test_dir / "no-alert" / non_alerting_file).read_text(encoding="utf-8")
                new_non_alerting_file = f"NonAlertingTest{len(true_non_alerting_test_info) + 1}.java"
                true_non_alerting_test_info.append((Path(new_non_alerting_file).stem, non_alerting_test_code))
                if non_alerting_file != new_non_alerting_file:
                    test_change_map[non_alerting_file] = new_non_alerting_file
            # mismatch non-alerting test cases
            elif non_alerting_file.startswith("Alerting"):
                non_alerting_test_code = (self.test_dir / "alert" / non_alerting_file).read_text(encoding="utf-8")
                new_file_name = f"MisNonAlertingTest{len(mis_non_alerting_test_info) + 1}.java"
                mis_non_alerting_test_info.append((Path(new_file_name).stem, non_alerting_test_code))
                test_change_map[non_alerting_file] = new_file_name
                mis_non_alerting_count += 1
            else:
                continue

        logger.info(
            f"Rearrage result: identified {mis_alerting_count} MismatchAlerting and {mis_non_alerting_count} Mismatch-Non-Alerting."
        )
        rearraged_test_info = TestInfoDict(
            alerting=true_alerting_test_info,
            non_alerting=true_non_alerting_test_info,
            mis_alerting=mis_alerting_test_info,
            mis_non_alerting=mis_non_alerting_test_info,
        )

        val_res_str = json.dumps(val_res)
        pattern = re.compile("|".join(re.escape(k) for k in sorted(test_change_map, key=len, reverse=True)))
        new_val_res_str = pattern.sub(lambda m: test_change_map[m.group(0)], val_res_str)
        new_val_res = json.loads(new_val_res_str)

        return rearraged_test_info, new_val_res

    def append_test_info(self, final_test_info: TestInfoDict, target_test_dir: Path = None) -> TestInfoDict:
        """
        Append tests with test info to the aggregate test directory.
        """
        if not target_test_dir:
            target_test_dir = self.test_dir if self.test_dir.endswith("/test") else self.test_dir.parent / "test"

        logger.info(f"Apending final rearranged test information to {target_test_dir}")
        # collect the start ids for appending alerting, non-alerting, and mismatch tests
        new_test_info = self.create_test_info(
            alerting_test_list=[t[1] for t in final_test_info["alerting"]],
            non_alerting_test_list=[t[1] for t in final_test_info["non_alerting"]],
            mismatch_alerting_test_list=[t[1] for t in final_test_info["mis_alerting"]],
            mismatch_non_alerting_test_list=[t[1] for t in final_test_info["mis_non_alerting"]],
            append_test_dir=target_test_dir,
        )
        self.save_test_info(new_test_info, append_test_dir=target_test_dir)


if __name__ == "__main__":
    # test rearrange_test_info using kirin_ws\ONLINE_Use_Unsafe_Algorithm_IDEA\test
    test_manager = TestManager(Path("kirin_ws/ONLINE_Use_Unsafe_Algorithm_IDEA/tmp/test"))
    val_res = {
        "DSL_ORI": {
            "report": {
                "AlertingTest1.java": [1],
                "AlertingTest2.java": [1],
                "AlertingTest4.java": [2],
                "NonAlertingTest1.java": [3],
            },
            "pass": ["NonAlertingTest2.java", "NonAlertingTest3.java", "AlertingTest3.java"],
        }
    }
    re_test_info, new_val_res = test_manager.rearrage_test_info(val_res)
    logger.info("Rearranged Test Information:")
    for label in re_test_info:
        file_list = list(map(lambda x: x[0], re_test_info[label]))
        logger.info(f"{label}: {', '.join(file_list)}")
    test_manager.save_test_info(re_test_info)

    # move all the folders in kirin_ws/test-tmp to kirin_ws/test-cur
    test_cur_dir = Path("kirin_ws/test-cur")
    test_cur_dir.mkdir(parents=True, exist_ok=True)
    # using Pathlib rename to move the folder
    import shutil

    for item in test_cur_dir.iterdir():
        shutil.move(str(item), str(test_cur_dir / item.name))

    logger.info(f"New Validation Result: {new_val_res}")
