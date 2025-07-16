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
    pattern = r"public.+class\s+(\w+)\s+.*{"
    match = re.search(pattern, test_case)
    class_name = ""
    if match:
        class_name = match.group(1)
    else:
        coarse_pattern = r"class\s+(\w+)\s+.*{"
        coarse_match = re.search(coarse_pattern, test_case)
        class_name = coarse_match.group(1) if coarse_match else ""
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
    pattern = r"public.+class\s+(\w+)\s+.*{"
    # replace the class name with the new class name
    ori_class_match = re.search(pattern, test_case)
    ori_class_name = ori_class_match.group(1) if ori_class_match else ""
    if not ori_class_name:
        coarse_pattern = r"class\s+(\w+)\s+.*{"
        ori_class_coarse_match = re.search(coarse_pattern, test_case)
        ori_class_name = ori_class_coarse_match.group(1) if ori_class_coarse_match else ""

    if not ori_class_name:
        logger.error(f"--> No public main class found in the test case: {test_case}")
        return test_case
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
                │   ├── TruePosTest1.java
                │   ├── TruePosTest2.java
                │   ├── FalsePosTest1.java
                ├── no-alert/
                │   ├── TrueNegTest1.java
                │   ├── FalseNegTest1.java
        """
        assert test_dir.is_dir(), f"--> Test directory {test_dir} not found!"
        logger.info(f"Initialize TestManager with test directory: {test_dir}")
        self.test_dir = test_dir

    def collect_local_start_ids(self, test_dir: Path = None) -> TestIdxDict:
        """
        Collect the start ids for appending TP, TN, FP, FN tests.
        :return: TestIdxDict containing the start ids for TP, TN, FP, FN tests.
        """
        if not test_dir:
            test_dir = self.test_dir
        TP_count = len(list(test_dir.glob("alert/TruePosTest*.java")))
        TN_count = len(list(test_dir.glob("no-alert/TrueNegTest*.java")))
        FP_count = len(list(test_dir.glob("alert/FalsePosTest*.java")))
        FN_count = len(list(test_dir.glob("no-alert/FalseNegTest*.java")))
        logger.info(f"Found existed tests: TP=({TP_count}), TN=({TN_count}), FP=({FP_count}), FN=({FN_count})")

        return TestIdxDict(
            TP_id=TP_count + 1,
            TN_id=TN_count + 1,
            FP_id=FP_count + 1,
            FN_id=FN_count + 1,
        )

    def create_test_info(
        self,
        pos_test_list: list[str],
        neg_test_list: list[str],
        false_pos_test_list: list[str] = [],
        false_neg_test_list: list[str] = [],
        append_test_dir: Path = None,
        is_rearranged: bool = False,
    ) -> TestInfoDict:
        """
        create test info dict with positive and negative test cases.
        :param pos_test_list: list of alerting test cases
        :param neg_test_list: list of non-alerting test cases
        :param false_pos_test_list: list of mismatch alerting test cases, should not alerted but alerted
        :param false_neg_test_list: list of mismatch non-alerting test cases, should alert but not alerted
        :param append_test_dir: whether to augment the test cases with new ids (start id from collect_local_start_ids)
        :param is_rearranged: whether the test cases are rearranged from the validation result -- naming TP, TN, FP, FN
        :return: test info dict
        """
        # set start ids for all types of tests
        if append_test_dir:
            is_rearranged = True
            start_id_map = self.collect_local_start_ids(append_test_dir)
            logger.info(
                f"Appending test cases with start ids: {start_id_map['TP_id']}, {start_id_map['TN_id']}, {start_id_map['FP_id']}, {start_id_map['FN_id']}"
            )
        else:
            start_id_map = TestIdxDict(TP_id=1, TN_id=1, FP_id=1, FN_id=1)

        test_info = TestInfoDict()
        pos_key = "true_pos" if is_rearranged else "pos"
        neg_key = "true_neg" if is_rearranged else "neg"

        test_info[pos_key] = []
        TP_prefix = "TruePosTest" if is_rearranged else "PosTest"
        for i, test_case in enumerate(pos_test_list):
            class_name = extract_main_class(test_case)
            expected_class_name = f"{TP_prefix}{start_id_map['TP_id'] + i}"
            if class_name != expected_class_name:
                test_case = update_main_class(test_case, expected_class_name)
            test_info[pos_key].append((expected_class_name, test_case))

        test_info[neg_key] = []
        TN_prefix = "TrueNegTest" if is_rearranged else "NegTest"
        for i, test_case in enumerate(neg_test_list):
            class_name = extract_main_class(test_case)
            expected_class_name = f"{TN_prefix}{start_id_map['TN_id'] + i}"
            if class_name != expected_class_name:
                test_case = update_main_class(test_case, expected_class_name)
            test_info[neg_key].append((expected_class_name, test_case))

        # mismatch alerting tests
        if false_pos_test_list:
            test_info["false_pos"] = []
            FP_prefix = "FalsePosTest"
            for i, test_case in enumerate(false_pos_test_list):
                class_name = extract_main_class(test_case)
                expected_class_name = f"{FP_prefix}{start_id_map['FP_id'] + i}"
                if class_name != expected_class_name:
                    test_case = update_main_class(test_case, expected_class_name)
                test_info["false_pos"].append((expected_class_name, test_case))

        # mismatch non-alerting tests
        if false_neg_test_list:
            test_info["false_neg"] = []
            FN_prefix = "FalseNegTest"
            for i, test_case in enumerate(false_neg_test_list):
                class_name = extract_main_class(test_case)
                expected_class_name = f"{FN_prefix}{start_id_map['FN_id'] + i}"
                if class_name != expected_class_name:
                    test_case = update_main_class(test_case, expected_class_name)
                test_info["false_neg"].append((expected_class_name, test_case))

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
            # Pos/TruePos/FalsePos -> alert; Neg/TrueNeg/FalseNeg -> no-alert
            sub_test_dir = test_dir / "alert" if "pos" in label else test_dir / "no-alert"
            sub_test_dir.mkdir(parents=True, exist_ok=True)
            for single_test_info in sub_test_info:
                file_stem, test_case_code = single_test_info
                test_case_path = sub_test_dir / f"{file_stem}.java"
                test_case_path.write_text(test_case_code, encoding="utf-8")

        logger.info(f"All test cases have saved to {test_dir}.")

    def rearrange_test_info(self, val_res: dict) -> tuple[TestInfoDict, dict]:
        """
        Rearrange the alert and no-alert sub-dir of the test directory based on the validation result.
        Based on the validation result, rearrange pos and neg test cases into TP, TN, FP, FN categories.
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

        true_pos_test_info = [
            (p.stem, p.read_text(encoding="utf-8")) for p in sorted(self.test_dir.glob("alert/TruePosTest*.java"))
        ]
        true_neg_test_info = [
            (p.stem, p.read_text(encoding="utf-8")) for p in sorted(self.test_dir.glob("no-alert/TrueNegTest*.java"))
        ]
        false_pos_test_info = [
            (p.stem, p.read_text(encoding="utf-8")) for p in sorted(self.test_dir.glob("alert/FalsePosTest*.java"))
        ]
        false_neg_test_info = [
            (p.stem, p.read_text(encoding="utf-8")) for p in sorted(self.test_dir.glob("no-alert/FalseNegTest*.java"))
        ]

        test_change_map = dict()

        for pos_file in val_res["DSL_ORI"]["report"].keys():
            # true alerting test cases
            if pos_file.startswith("PosTest"):
                pos_test_code = (self.test_dir / "alert" / pos_file).read_text(encoding="utf-8")
                new_pos_stem = f"TruePosTest{len(true_pos_test_info) + 1}"
                new_pos_file = f"{new_pos_stem}.java"
                if pos_file != new_pos_file:
                    pos_test_code = update_main_class(pos_test_code, new_pos_stem)
                    test_change_map[pos_file] = new_pos_file
                true_pos_test_info.append((new_pos_stem, pos_test_code))
            # mismatch alerting test cases
            elif pos_file.startswith("NegTest"):
                pos_test_code = (self.test_dir / "no-alert" / pos_file).read_text(encoding="utf-8")
                new_file_stem = f"FalsePosTest{len(false_pos_test_info) + 1}"
                pos_test_code = update_main_class(pos_test_code, new_file_stem)
                false_pos_test_info.append((new_file_stem, pos_test_code))
                test_change_map[pos_file] = f"{new_file_stem}.java"
            elif "Neg" in pos_file:
                # FalseNegTest or TrueNegTest
                logger.error(f"Unexpected file {pos_file} is reported.")
                continue

        for neg_file in val_res["DSL_ORI"]["pass"]:
            # true non-alerting test cases
            if neg_file.startswith("NegTest"):
                neg_test_code = (self.test_dir / "no-alert" / neg_file).read_text(encoding="utf-8")
                new_neg_file = f"TrueNegTest{len(true_neg_test_info) + 1}.java"
                if neg_file != new_neg_file:
                    neg_test_code = update_main_class(neg_test_code, Path(new_neg_file).stem)
                    test_change_map[neg_file] = new_neg_file
                true_neg_test_info.append((Path(new_neg_file).stem, neg_test_code))
            # mismatch non-alerting test cases
            elif neg_file.startswith("PosTest"):
                neg_test_code = (self.test_dir / "alert" / neg_file).read_text(encoding="utf-8")
                new_file_name = f"FalseNegTest{len(false_neg_test_info) + 1}.java"
                neg_test_code = update_main_class(neg_test_code, Path(new_file_name).stem)
                false_neg_test_info.append((Path(new_file_name).stem, neg_test_code))
                test_change_map[neg_file] = new_file_name
            elif "Pos" in neg_file:
                # FalsePosTest or TruePosTest
                logger.error(f"Unexpected file {neg_file} is not reported.")
                continue

        logger.info(
            f"Rearrage result: identified {len(false_pos_test_info)} False-Positive and {len(false_neg_test_info)} False-Negative."
        )
        rearraged_test_info = TestInfoDict(
            true_pos=true_pos_test_info,
            true_neg=true_neg_test_info,
            false_pos=false_pos_test_info,
            false_neg=false_neg_test_info,
        )

        if not test_change_map:
            return rearraged_test_info, val_res

        val_res_str = json.dumps(val_res)
        pattern = re.compile("|".join(re.escape(k) for k in sorted(test_change_map, key=len, reverse=True)))
        new_val_res_str = pattern.sub(lambda m: test_change_map[m.group(0)], val_res_str)
        new_val_res = json.loads(new_val_res_str)

        return rearraged_test_info, new_val_res

    def append_test_info(
        self, final_test_info: TestInfoDict, target_test_dir: Path = None, do_opposite: bool = False
    ) -> TestInfoDict:
        """
        :param final_test_info: Final rearranged test information to append.
        :param target_test_dir: Target test directory to append the test information.
        :param do_opposite: If True, the dsl_checker is in the opposite mode, meaning the test cases should also be reverted
        Append tests with test info to the aggregate test directory.
        """
        if not target_test_dir:
            target_test_dir = self.test_dir if self.test_dir.endswith("/test") else self.test_dir.parent / "test"

        logger.info(f"Apending final rearranged test information to {target_test_dir}")
        # collect the start ids for appending all TP, TN, FP, FN tests
        if do_opposite:
            new_test_info = self.create_test_info(
                pos_test_list=[t[1] for t in final_test_info["true_neg"]],
                neg_test_list=[t[1] for t in final_test_info["true_pos"]],
                false_pos_test_list=[t[1] for t in final_test_info["false_neg"]],
                false_neg_test_list=[t[1] for t in final_test_info["false_pos"]],
                append_test_dir=target_test_dir,
            )
        else:
            new_test_info = self.create_test_info(
                pos_test_list=[t[1] for t in final_test_info["true_pos"]],
                neg_test_list=[t[1] for t in final_test_info["true_neg"]],
                false_pos_test_list=[t[1] for t in final_test_info["false_pos"]],
                false_neg_test_list=[t[1] for t in final_test_info["false_neg"]],
                append_test_dir=target_test_dir,
            )
        self.save_test_info(new_test_info, append_test_dir=target_test_dir)


if __name__ == "__main__":
    # test rearrange_test_info using kirin_ws\ONLINE_Use_Unsafe_Algorithm_IDEA\test
    test_manager = TestManager(Path("kirin_ws/test_tmp/tmp/test"))
    val_res = {
        "DSL_ORI": {
            "report": {
                "TruePosTest1.java": [1],
                "PosTest1.java": [1],
                "PosTest2.java": [1],
                "NegTest1.java": [3],
            },
            "pass": ["PosTest3.java", "NegTest2.java"],
        }
    }
    re_test_info, new_val_res = test_manager.rearrange_test_info(val_res)
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
