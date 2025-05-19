"""
[INFO] Kirin DSL parser Main Class Entrance
"""

from pathlib import Path

from src.utils._antlr import *
from src.utils.types import *
from src.utils._kirin import KirinRunner
from src.utils._helper import create_dir_with_path


class KirinAntlrParser:
    """
    Kirin DSL Antlr Parser
    """

    def __init__(self, dsl_text: str):
        self.dsl_stream = InputStream(dsl_text)
        self.lexer = HornLexer(self.dsl_stream)
        self.stream = CommonTokenStream(self.lexer)
        self.parser = DslParser(self.stream)


def analyze_third_pkg(dsl_text: str) -> list[str]:
    """
    [Not-Used] Analyze and fetch the DSL code to fetch all the third-party resources.
    :param dsl_text: DSL code as a string
    :return: A list of third-party resources
    [WARN] Cannot construct class that using endsWith, startWith, regex for match.
    """
    # DSL analysis
    pkg_parser = KirinAntlrParser(dsl_text)
    tree = pkg_parser.parser.statements()
    if pkg_parser.parser.getNumberOfSyntaxErrors() > 0:
        raise ValueError(f"--> DSL syntax error: {pkg_parser.parser.getNumberOfSyntaxErrors()} errors found!")
    analyzer = KirinThirdPkgAnalyzer()
    analyzer.visit(tree)
    return list(analyzer.third_pkg_list)


def get_dsl_hash(dsl_text: str) -> tuple[str, str]:
    """
    [NOT-USED] Get the hash of the DSL text
    :param dsl_text: DSL text
    :return: hash of the DSL text
    TODO)) order in ("or, and") will affect the hash value
    """
    # DSL analysis
    hash_parser = KirinAntlrParser(dsl_text)
    tree = hash_parser.parser.statements()
    if hash_parser.parser.getNumberOfSyntaxErrors() > 0:
        raise ValueError(f"--> DSL syntax error: {hash_parser.parser.getNumberOfSyntaxErrors()} errors found!")
    hash_visitor = KirinHashVisitor(dsl_text)
    hash_str, hash_value = hash_visitor.visit(tree)
    logger.info(f"==> DSL hash: \n{hash_str}")
    return hash_value


def preprocess_dsl(
    dsl_text: str,
    clear_labels: bool = True,
    init_transform: bool = False,
    spec_na_strategy: bool = False,
    split_not_has: bool = False,
    do_format: bool = True,
) -> DslPrepResDict:
    """
    Preprocess_dsl the DSL text for decomposition and return decomposed dsls
    :param clear_labels: Whether to clear labels (RuleSetMsg, RuleMsg)
    :param init_transform: Whether to initialize transform
    :param spec_na_strategy: Whether to use special strategy for "not and"
    :param split_not_has: Whether to split not has
    :param do_format: Whether to format each DSL text
    :return: cleaned dsl, Decomposed dsls [[node1_sub_1, node1_sub_2], [node2_sub_1, node2_sub_2] ... ]
    """
    if init_transform:
        logger.info("==> Preprocess DSL in the opposite setting")
    else:
        logger.info("==> Preprocess DSL in the normal setting")

    # DSL split -- start from statements -- KirinEntryVisitor
    full_parser = KirinAntlrParser(dsl_text)
    full_tree = full_parser.parser.statements()
    if full_parser.parser.getNumberOfSyntaxErrors() > 0:
        raise ValueError("--> Original DSL syntax error, check the DSL syntax!")
    full_visitor = KirinEntryVisitor(dsl_text, clear_labels=clear_labels)
    node_dsl_list = full_visitor.visit(full_tree)

    if len(node_dsl_list) > 0:
        logger.info(f"Multi nodes detected: node count is {len(node_dsl_list)}.")
    else:
        logger.info("Single node detected.")

    sub_dsl_result = []
    for i, node_dsl in enumerate(node_dsl_list):
        i += 1
        logger.info(f"[#{i}] Node DSL parsing starts...")
        # DSL transformation -- starting from node Stmt -- KirinNotVisitor
        node_parser = KirinAntlrParser(node_dsl)
        node_tree = node_parser.parser.nodeStmt()
        if node_parser.parser.getNumberOfSyntaxErrors() > 0:
            raise ValueError("--> Node DSL syntax error, check the DSL syntax!")
        not_visitor = KirinNotVisitor(
            node_dsl,
            init_transform=init_transform,
            spec_na_strategy=spec_na_strategy,
            split_not_has=split_not_has,
        )
        transformed_dsl = not_visitor.visit(node_tree)
        logger.info(f"[#{i}] Node DSL transformation done~")

        # DSL decomposition -- starting from node Stmt -- KirinOrVisitor
        trans_parser = KirinAntlrParser(transformed_dsl)
        trans_tree = trans_parser.parser.nodeStmt()
        if trans_parser.parser.getNumberOfSyntaxErrors() > 0:
            raise ValueError("--> Transformed Node DSL syntax error, check the DSL syntax!")
        or_visitor = KirinOrVisitor(transformed_dsl)
        or_visitor.visit(trans_tree)
        logger.info(f"[#{i}] Node DSL decomposition done, sub dsl count is {len(or_visitor.sub_dsl_list)}~")
        sub_dsl_result.append(or_visitor.sub_dsl_list)

    assert len(node_dsl_list) == len(sub_dsl_result), "[SHould not happen] Node DSL count and sub DSL count mismatch!"
    if do_format:
        # Format the DSL text
        for i, node_dsl in enumerate(node_dsl_list):
            logger.info(f"Formatting [#{i + 1}] Node DSL~")
            node_dsl_list[i] = KirinRunner.format_dsl_text(node_dsl)
            for j, sub_dsl in enumerate(sub_dsl_result[i]):
                logger.info(f"Formatting [#{i + 1}] Node DSL - (#{j+1}) Sub DSL~")
                sub_dsl_result[i][j] = KirinRunner.format_dsl_text(sub_dsl)

    return DslPrepResDict(
        node_dsl_list=node_dsl_list,
        sub_dsl_collection=sub_dsl_result,
    )


def save_dsl_prep_res(dsl_prep_res: DslPrepResDict, dsl_dir: Path) -> None:
    """
    Save the dsl preprocess result to the dsl directory
    :param dsl_prep_res: dsl preprocess result
    :param dsl_dir: dsl directory, which is the kirin_ws/{dsl_id}/dsl directory
    :return: None, the dsl preprocess result will be saved to dsl_dir
    """
    assert dsl_dir.is_dir(), f"--> DSL directory {dsl_dir} not found!"
    create_dir_with_path(dsl_dir, cleanup=True)

    for i, node_dsl in enumerate(dsl_prep_res["node_dsl_list"]):
        i += 1
        node_dsl_path = dsl_dir / f"DSL_N{i}.kirin"
        node_dsl_path.write_text(node_dsl, encoding="utf-8")

    for i, sub_dsl_list in enumerate(dsl_prep_res["sub_dsl_collection"]):
        i += 1
        sub_dsl_dir = dsl_dir / f"sub_n{i}"
        sub_dsl_dir.mkdir(parents=True, exist_ok=True)
        for j, sub_dsl in enumerate(sub_dsl_list):
            j += 1
            sub_dsl_path = sub_dsl_dir / f"DSL_N{i}_S{j}.kirin"
            sub_dsl_path.write_text(sub_dsl, encoding="utf-8")

    logger.info(f"DSL preprocess result saved to {dsl_dir}")


if __name__ == "__main__":
    # Test the parse_dsl function
    dsl_path = Path("data/tmp/tmp_new.kirin")
    dsl_text = dsl_path.read_text(encoding="utf-8")
    dsl_prep_res = preprocess_dsl(dsl_text, init_transform=False, split_not_has=True, do_format=True)

    result_str = "==> Preprocess Result:\n"

    for i, sub_dsl_list in enumerate(dsl_prep_res["sub_dsl_collection"]):
        # fmt_sub_dsl_list = list(map(KirinRunner.format_dsl_text, sub_dsl_list))
        result_str += f"--> Node {i + 1}:"
        result_str += "\n" + f"\n{'-'*20}\n".join(sub_dsl_list)
    logger.info(result_str)
