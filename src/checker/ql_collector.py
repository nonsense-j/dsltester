import json, re
import tree_sitter_ql as tsql
from pathlib import Path
from tree_sitter import Language, Parser
from tqdm import tqdm

QL_LANGUAGE = Language(tsql.language())
QL_CATALOGS = [
    "Advisory",
    "Architecture",
    "Compatibility",
    "Complexity",
    "DeadCode",
    "Diagnostics",
    "Frameworks",
    "Language Abuse",
    "Likely Bugs",
    "Metrics",
    "Performance",
    "Security",
    "Telemetry",
    "Violations of Best Practice",
]


class QlParser:
    def __init__(self, ql_root: str):
        self.parser = Parser(QL_LANGUAGE)
        self.ql_root = Path(ql_root)

    def parse_ql(self, ql_code: str) -> tuple[str, list[str]]:
        """
        Get the qldoc and the list of imports from the parsed QL code.

        Returns:
            tuple[str, list[str]]: A tuple containing the qldoc and a list of imported modules.
        """
        ql_tree = self.parser.parse(bytes(ql_code, "utf8"))
        import_query = QL_LANGUAGE.query(
            """
            (importModuleExpr) @import_module
        """
        )
        captures = import_query.captures(ql_tree.root_node)
        module_list = []
        for node in captures.get("import_module", []):
            module_name = node.text.decode("utf-8")
            if module_name not in module_list:
                module_list.append(module_name)

        doc_query = QL_LANGUAGE.query(
            """
            (qldoc) @ql_doc
        """
        )
        captures = doc_query.captures(ql_tree.root_node)
        ql_doc = captures.get("ql_doc", [])[0].text.decode("utf-8") if captures.get("ql_doc") else ""

        return ql_doc, module_list

    def extract_qldoc_by_tag(self, tag_name: str, ql_doc: str) -> str | None:
        """
        Extract the QL docstring by tag name. *@{tag_name} xxx
        Args:
            tag_name (str): The tag name to search for (e.g., "problem.severity").
            ql_doc (str): The full QL docstring.
        """
        tag_content = re.search(rf"@{tag_name}\s+(\S+)", ql_doc)
        if tag_content:
            return tag_content.group(1).lower()
        return None

    def parse_ql_dir(self, dir_rel_path: str) -> dict[str, str]:
        """
        Parse all QL files in the given directory.

        Args:
            dir_rel_path (Path): The relative path to the directory containing QL files.

        Returns:
            dict[str, str]: A dictionary mapping file paths to their contents.
        """

        res_dict = {}
        dir_path = self.ql_root / dir_rel_path
        if not dir_path.is_dir():
            raise ValueError(f"QL directory path: {dir_path} not exists!")
        for ql_file in tqdm(dir_path.rglob("*.ql"), desc=f"Parsing {dir_rel_path} QL"):
            ql_rel_name = ql_file.relative_to(self.ql_root).as_posix()
            ql_content = ql_file.read_text(encoding="utf-8")
            ql_doc, modules = self.parse_ql(ql_content)

            ql_kind = self.extract_qldoc_by_tag("kind", ql_doc)
            if ql_kind == "problem":
                ql_precision = self.extract_qldoc_by_tag("precision", ql_doc)
                if ql_precision in {"high", "very-high"}:
                    res_dict[ql_rel_name] = modules
        return res_dict


if __name__ == "__main__":
    ql_parser = QlParser(ql_root="D:/01_Research/10_Code/codeql/java/ql/src")
    full_res_path = Path("data/ql_imports.json")
    full_res = json.load(full_res_path.open(encoding="utf-8")) if full_res_path.is_file() else {}

    for catalog in QL_CATALOGS:
        if catalog in full_res:
            print(f"Already exists Catalog: {catalog}")
            continue
        print(f"Processing Catalog: {catalog}")
        full_res[catalog] = ql_parser.parse_ql_dir(catalog)
        with open(full_res_path, "w", encoding="utf-8") as f:
            json.dump(full_res, f, ensure_ascii=False, indent=4)
