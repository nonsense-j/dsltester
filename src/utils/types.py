from typing import TypedDict, List

"""
Basic types for dsl_kirin analysis
"""


class DslInfoDict(TypedDict):
    id: str
    dsl: str


class TestInfoDict(TypedDict):
    # tuple: file_stem, code
    pos: List[tuple[str, str]]
    neg: List[tuple[str, str]]
    true_pos: List[tuple[str, str]]
    true_neg: List[tuple[str, str]]
    false_pos: List[tuple[str, str]]
    false_neg: List[tuple[str, str]]


class TestIdxDict(TypedDict):
    TP_id: int
    TN_id: int
    FP_id: int
    FN_id: int


class DslPrepResDict(TypedDict):
    node_dsl_list: List[str]
    sub_dsl_collection: List[List[str]]


class DslValResDict(TypedDict):
    reported: dict[str, list[int]]  # {file_name: [report_line, ...]}
    passed: list[str]  # [file_name, ...]


"""
Used for node property knowledge collection
"""


# single node property dict
class NodePropertyInfoDict(TypedDict):
    description: str  # 属性描述
    value_type: str  # 属性值类型
    example: str  # 属性示例
    example_dsl: str  # 属性示例对应的DSL


# single node dict
class NodeInfoDict(TypedDict):
    description: str  # 节点描述
    example: str  # 节点示例
    example_node_part: str  # 节点示例对应的节点部分
    properties: dict[str, NodePropertyInfoDict]  # 节点属性字典，prop_name -> NodePropertyInfoDict


# the full knowledge collection, node_type->node_name->node_info
NodeCollectionDict = dict[str, dict[str, NodeInfoDict]]
