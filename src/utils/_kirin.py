"""
This module provides functions to run dsl_kirin analysis using the command line interface (CLI) of the dsl_kirin jar file.
"""

import os, subprocess
from pathlib import Path
from typing import Optional, List

from .types import DslInfoDict, TestInfoDict
from .config import KIRIN_JAVA_HOME, KIRIN_CLI_PATH
from ._helper import create_dir_with_path, del_kirin_logs
from ._logger import logger


class KirinRunner:
    """
    KirinRunner is a class that provides methods to run dsl_kirin analysis using the command line interface (CLI).
    """

    java_executable = os.path.join(KIRIN_JAVA_HOME, "bin", "java")
    if os.name == "nt":
        java_executable += ".exe"

    kirin_cli_path = KIRIN_CLI_PATH

    @classmethod
    def check_config(cls):
        """
        check the configuration of the KirinRunner
        """
        if not os.path.isfile(cls.java_executable):
            raise ValueError(f"--> Java executable {cls.java_executable} does not exist!")

        if not os.path.isfile(cls.kirin_cli_path):
            raise ValueError(f"--> Kirin CLI related jar path {cls.kirin_cli_path} does not exist!")

    @classmethod
    def execute_kirin_dsl(
        cls, dsl_dir: Path, test_dir: Path, report_dir: Path, third_resources_dir: Optional[Path] = None
    ):
        """
        Execute dsl_kirin analysis using the CLI.
        :param dsl_dir: Directory containing the DSL files.
        :param test_dir: Directory containing the test files to scan.
        :param report_dir: Directory to save the report.
        :param third_resources_dir: Optional directory for third-party resources.
        """
        # check the configuration
        cls.check_config()
        logger.info(f"Executing dsl_kirin analysis with dsl_dir: {dsl_dir}")
        # check whether the dsls and test cases have been prepared
        if (not dsl_dir.is_dir()) or len(list(dsl_dir.rglob("*.kirin"))) == 0:
            logger.error(f"--> No dsls are found in {dsl_dir}!")
            return None
        if (not test_dir.is_dir()) or len(list(test_dir.rglob("*.java"))) == 0:
            logger.error(f"--> No test cases are found in {test_dir}!")
            return None

        # create and clean the report dir
        create_dir_with_path(report_dir, cleanup=True)

        test_dir_list = [str(test_dir.absolute())]
        if third_resources_dir is not None:
            logger.info(f"Loading third resources from {third_resources_dir}")
            if not third_resources_dir.is_dir():
                logger.error(f"--> Third resources directory {third_resources_dir} does not exist!")
                return None
            test_dir_list.append(str(third_resources_dir.absolute()))

        command = [
            cls.java_executable,
            "-Dfile.encoding=UTF-8",
            "--add-opens=java.base/java.lang.reflect=ALL-UNNAMED",
            "--enable-preview",
            "-cp",
            cls.kirin_cli_path,
            "com.huawei.secbrella.kirin.Main",
            "--pugin",
            "--dir",
            ",".join(test_dir_list),
            "--checkerDir",
            str(dsl_dir.absolute()),
            "--outputFormat",
            "xml",
            "--output",
            str(report_dir.absolute()),
            "--language",
            "java",
            # "--persist-graph"
        ]

        try:
            logger.debug(f"Kirin executor command: \n{' '.join(command)}")
            result = subprocess.run(command, capture_output=True, text=True, check=True, cwd=dsl_dir)
            logger.debug(f"Kirin executor output: {result.stdout}")
            # With check=True, we'll only reach here if returncode is 0
            logger.info(f"Kirin executor report has been saved to {report_dir}")

        except subprocess.CalledProcessError as e:
            logger.error(f"--> Kirin executor failed with error: {e}")
            logger.error(f"--> Kirin executor error output: {e.stderr}")

        finally:
            # delete the kirin logs
            del_kirin_logs(dsl_dir)

    @classmethod
    def format_dsl_file(cls, input_path: Path, do_replace=True) -> str:
        """
        Format the dsl file to a single line.
        :param input_path: path to the dsl file
        :param do_replace: if True, replace the original file with the formatted one
        :return: formatted dsl string
        """
        # check the configuration
        cls.check_config()
        if not input_path.exists():
            logger.error(f"--> Dsl file {input_path} does not exist!")
            return ""
        command = [
            cls.java_executable,
            "-Dfile.encoding=UTF-8",
            "--add-opens=java.base/java.lang.reflect=ALL-UNNAMED",
            "--enable-preview",
            "-cp",
            cls.kirin_cli_path,
            "com.huawei.secbrella.kirin.horn.HornMain",
            "format",
            str(input_path.absolute()),
        ]
        try:
            logger.debug(f"Kirin formatter command: \n{' '.join(command)}")
            result = subprocess.run(command, capture_output=True, text=True, check=True, cwd=input_path.parent)
            logger.debug(f"Kirin formatter output: {result.stdout}")
            # With check=True, we'll only reach here if returncode is 0
            if "| ERROR |" in result.stdout or not result.stdout:
                logger.error(f"--> Kirin formatter error for {input_path}: \n{input_path.read_text(encoding='utf-8')}")
                logger.error(f"--> Kirin formatter stdout: \n{result.stdout}")
                logger.error(f"--> Kirin formatter stderr: \n{result.stderr}")
                return ""
            else:
                formatted_dsl_text = result.stdout.replace("\r\n", "\n").strip()
                if do_replace:
                    input_path.write_text(formatted_dsl_text, encoding="utf-8")
                    logger.info(f"{input_path} has been formatted")
                else:
                    logger.info(f"-- Dsl formatting done.")
            return formatted_dsl_text

        except subprocess.CalledProcessError as e:
            logger.error(f"--> Kirin formatter error for {input_path}: \n{input_path.read_text(encoding='utf-8')}")
            logger.error(f"--> Kirin format failed with error: {e}")
            logger.error(f"--> Kirin format error output: {e.stderr}")
            return ""

        finally:
            # delete the kirin logs
            del_kirin_logs(input_path.parent)

    @classmethod
    def format_dsl_text(cls, dsl_text: str) -> str:
        """
        create a temporary file with the dsl text and format it
        """
        tmp_file = Path("kirin_ws/tmp/tmp.kirin")
        if not tmp_file.parent.exists():
            tmp_file.parent.mkdir(parents=True, exist_ok=True)
        tmp_file.write_text(dsl_text, encoding="utf-8")

        formatted_dsl_text = cls.format_dsl_file(tmp_file, do_replace=False)
        assert formatted_dsl_text, f"--> Kirin formatter failed for this dsl"

        # delete the tmp file
        # tmp_file.unlink()
        return formatted_dsl_text


if __name__ == "__main__":
    # Example usage
    dsl_path = Path("tmp_or.kirin")
    dsl_text = dsl_path.read_text(encoding="utf-8")
    print(KirinRunner.format_dsl_text(dsl_text))
