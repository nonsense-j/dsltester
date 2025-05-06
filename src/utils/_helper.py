"""
helper functions
"""

import shutil
from pathlib import Path
from .types import DslInfoDict, DslPrepResDict
from ._logger import logger


def create_dir_with_path(dir_path: Path, cleanup=True):
    """
    only allow create folders and files in kirin_ws
    :param dir_path: path to create
    :param cleanup: if True, remove the folder if it exists
    """
    dir_abspath = dir_path.absolute()
    kirin_ws_abspath = Path("kirin_ws").absolute()
    if not str(dir_abspath).startswith(str(kirin_ws_abspath)):
        raise ValueError(f"[Exception] not allowed to create folder {dir_path} beyond kirin_ws")
    # cleanup
    if cleanup and dir_path.exists():
        shutil.rmtree(dir_path)

    dir_path.mkdir(parents=True, exist_ok=True)


def del_kirin_logs(dir_path: Path):
    """
    delete kirin logs
    :param dir_path: path to delete
    """
    if dir_path.exists():
        # only delete .log files in the subfolder without recursing
        for file in dir_path.glob("*.log"):
            file.unlink()


def read_file(file_path: Path) -> str:
    """
    read file
    :param file_path: path to read
    :return: content of the file
    """
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    return content


def is_third_class(class_name: str) -> bool:
    """
    check if the class name is a third class
    :param class_name: class name
    :return: True if the class name is a third class
    """
    # look for: https://docs.oracle.com/en/java/javase/17/docs/api/allpackages-index.html
    builtin_pkg_prefixes = [
        "com.sun",
        "java",
        "javax",
        "jdk",
        "netscape.javascript",
        "org.ietf.jgss",
        "org.w3c.dom",
        "org.xml.sax",
    ]
    return not any([class_name.startswith(prefix) for prefix in builtin_pkg_prefixes])


def save_dsl_prep_result(dsl_prep_result: DslPrepResDict, save_dir: Path):
    """
    save dsl prep result to file
    :param dsl_prep_result: dsl prep result
    :param save_dir: path to save the result
    """
    if not save_dir.exists():
        save_dir.mkdir(parents=True, exist_ok=True)
    for key, value in dsl_prep_result.items():
        with open(save_dir / f"{key}.json", "w", encoding="utf-8") as f:
            f.write(value)
