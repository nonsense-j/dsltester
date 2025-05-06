"""
[Faster]
This module is used to generate mock libraries for third-party packages using tree-sitter.
It can also be used to detect whether the Java codes is using third-party libraries.
"""

import json
import tree_sitter_java as tsjava
from pathlib import Path
from typing import TypedDict
from tree_sitter import Language, Parser

from src.utils._logger import logger

# Java Premitive Types -> defult value
PREMITIVE_TYPE_DEFAULT = {
    "byte": "0",
    "short": "0",
    "int": "0",
    "long": "0",
    "float": "0.0",
    "double": "0.0",
    "char": "\u0000",
    "boolean": "false",
}


class MethodSignature(TypedDict):
    is_static: bool
    name: str
    arg_type_list: list[str]
    type: str


class FieldSignature(TypedDict):
    is_static: bool
    name: str
    type: str


class ConstructorSignature(TypedDict):
    arg_type_list: list[str]


class LibUsageInfo(TypedDict):
    constructors: list[ConstructorSignature]
    methods: list[MethodSignature]
    fields: list[FieldSignature]


class JavaDependencyParser:
    def __init__(self):
        self.JAVA_LANGUAGE = Language(tsjava.language())
        self.parser = Parser(self.JAVA_LANGUAGE)

        self.inner_class_types = set()  # only single file: inner class types
        self.scoped_class_info = {}  # only single file: Cls -> x.y.z.Cls
        self.method_decl_map = {}  # only single file: method_name -> ([arg1_type, arg2_type, ...], ret_type)
        self.type_info = {}  # only single file: x -> String

        self.usage_info = {}  # share among dir: x.y.z.Cls -> {methods: [], fields: []}

    def parse_file(self, file_path: Path):
        """Parse a Java file and extract third-party dependency information."""
        with open(file_path, "rb") as f:
            source_code = f.read()

        tree = self.parser.parse(source_code)

        # clear previous data
        self.inner_class_types.clear()
        self.scoped_class_info.clear()
        self.type_info.clear()
        self.method_decl_map.clear()

        # Extract inner class types to self.inner_class_types
        self._extract_inner_class_types(tree.root_node)

        # Extract imports to self.scoped_class_info
        self._extract_imports(tree.root_node)

        # Extract method declarations to self.method_decl_map
        self._extract_method_decl(tree.root_node)

        if self.scoped_class_info:
            # Extract usage of imported classes to self.usage_info
            self._visit_node(tree.root_node)

        return self.usage_info

    def parse_directory(self, directory_path: Path):
        """Parse all Java files in a directory and extract third-party dependency information."""
        assert directory_path.is_dir(), f"directory_path {directory_path} is not a directory"
        java_files = list(directory_path.glob("*.java"))
        for java_file in java_files:
            logger.info(f"Parsing lib code for file: {java_file}")
            file_path = java_file.resolve()
            self.parse_file(file_path)
        return self.usage_info

    def usage_info_to_code(self) -> dict[str, str]:
        """
        Convert the usage information to code.
        :return: A dictionary containing the usage information -> {"{class_fqn}": "{mock_code}"}
        The return type is same as the gen_mock_lib_code_llm.
        """
        res = {}
        for class_fqn, usage in self.usage_info.items():
            # construct the class body
            class_body = ""
            # add fields
            field_sig_list = usage.get("fields", [])
            for field_sig in field_sig_list:
                if field_sig["is_static"]:
                    field_sig_str = f"public static {field_sig['type']} {field_sig['name']};"
                else:
                    field_sig_str = f"public {field_sig['type']} {field_sig['name']};"
                class_body += f"\t{field_sig_str}\n"
            class_body += "\n"
            # add constructors
            constructor_sig_list = usage.get("constructors", [])
            for constructor_sig in constructor_sig_list:
                arg_str_list = [f"{x} arg_{i+1}" for i, x in enumerate(constructor_sig["arg_type_list"])]
                class_name = class_fqn.split(".")[-1]
                constructor_str = f"public {class_name}({', '.join(arg_str_list)}) {{\n\t\t// pass\n\t}}\n"
                class_body += f"\t{constructor_str}\n"
            # add methods
            method_sig_list = usage.get("methods", [])
            for method_sig in method_sig_list:
                method_name = method_sig["name"]
                method_type = method_sig["type"]
                arg_str_list = [f"{x} arg_{i+1}" for i, x in enumerate(method_sig["arg_type_list"])]
                args_full_str = ", ".join(arg_str_list)
                if method_sig["is_static"]:
                    method_str = f"public static {method_type} {method_name}({args_full_str})"
                else:
                    method_str = f"public {method_type} {method_name}({args_full_str})"
                if method_type == "void":
                    method_str += " {\n\t\t// pass\n\t}"
                else:
                    method_type_value = PREMITIVE_TYPE_DEFAULT.get(method_type, "null")
                    method_str += f" {{\n\t\treturn {method_type_value};\n\t}}"
                class_body += f"\t{method_str}\n\n"

            # construct the lib code
            package_name, class_name = class_fqn.rsplit(".", 1)
            lib_code = f"package {package_name};\n\n"
            lib_code += f"public class {class_name} {{\n{class_body.rstrip()}\n}}"
            res[class_fqn] = lib_code
        return res

    def _extract_inner_class_types(self, root_node):
        """Extract all inner class types from the AST."""
        # inner class types
        inner_class_query = self.JAVA_LANGUAGE.query(
            """
            (class_declaration
            (identifier) @inner_class_type
            )
        """
        )
        captures = inner_class_query.captures(root_node)
        for node in captures.get("inner_class_type", []):
            class_name = node.text.decode("utf-8")
            if class_name in self.inner_class_types:
                continue
            self.inner_class_types.add(class_name)

    def _extract_imports(self, root_node):
        """Extract all third-party scope classes from the AST."""
        # import classes
        import_query = self.JAVA_LANGUAGE.query(
            """
            (import_declaration
            (scoped_identifier) @import_class
            )
        """
        )
        captures = import_query.captures(root_node)
        for node in captures.get("import_class", []):
            class_fqn = node.text.decode("utf-8")
            if class_fqn in self.scoped_class_info:
                continue
            self.scoped_class_info[class_fqn] = class_fqn
            access_name = node.child_by_field_name("name").text.decode("utf-8")
            self.scoped_class_info[access_name] = class_fqn

        # Process scoped type identifiers, use full name in the code
        scoped_type_query = self.JAVA_LANGUAGE.query(
            """
            (scoped_type_identifier (scoped_type_identifier)) @scoped_class_type
        """
        )
        captures = scoped_type_query.captures(root_node)
        for node in captures.get("scoped_class_type", []):
            class_fqn = node.text.decode("utf-8")
            if class_fqn in self.scoped_class_info:
                continue
            self.scoped_class_info[class_fqn] = class_fqn

    def _extract_method_decl(self, root_node):
        """Extract all method declarations from the AST."""
        # method declaration
        method_decl_query = self.JAVA_LANGUAGE.query(
            """
            (method_declaration) @method_decl
            """
        )
        captures = method_decl_query.captures(root_node)
        for node in captures.get("method_decl", []):
            method_name = node.child_by_field_name("name").text.decode("utf-8")
            if method_name in self.method_decl_map:
                continue
            # get the return type
            ret_type = node.child_by_field_name("type").text.decode("utf-8")
            # get the argument types
            args_node = node.child_by_field_name("parameters")
            arg_types = []
            for i in range(args_node.named_child_count):
                arg_node = args_node.named_child(i)
                arg_type = arg_node.child_by_field_name("type").text.decode("utf-8")
                arg_types.append(arg_type)
            self.method_decl_map[method_name] = (arg_types, ret_type)

    def _visit_node(self, node):
        """
        Visit the program and extract usage information.
        Since generated by LLM, we assume that the variables using the same name share the same type.
        """
        # Visit all nodes on the tree
        for child in node.named_children:
            if child.type == "local_variable_declaration":
                var_type = child.child_by_field_name("type").text.decode("utf-8")
                var_name = child.child_by_field_name("declarator").child_by_field_name("name").text.decode("utf-8")
                self.type_info[var_name] = var_type
            elif child.type == "formal_parameter":
                var_type = child.child_by_field_name("type").text.decode("utf-8")
                var_name = child.child_by_field_name("name").text.decode("utf-8")
                self.type_info[var_name] = var_type
            elif child.type == "object_creation_expression":
                self._process_constructor(child)
            elif child.type == "method_invocation":
                self._process_method_call(child)
            elif child.type == "field_access":
                self._process_field_access(child)
            # keep traversing
            self._visit_node(child)

    def _process_constructor(self, constructor_node):
        """Process constructor nodes."""
        class_name = constructor_node.child_by_field_name("type").text.decode("utf-8")
        if class_name in self.scoped_class_info:
            # argument signature
            args_node = constructor_node.child_by_field_name("arguments")
            arg_type_list = []
            for i in range(args_node.named_child_count):
                arg_node = args_node.named_child(i)
                arg_type = self._get_arg_type(arg_node)
                # if the arg_type is a class, use the full name
                if arg_type in self.scoped_class_info:
                    arg_type = self.scoped_class_info[arg_type]
                if arg_type in self.inner_class_types:
                    # inner class types should be set to Object
                    arg_type = "Object"
                arg_type_list.append(arg_type)

            constructor_sig = ConstructorSignature(arg_type_list=arg_type_list)
            # add constructor signature
            class_fqn = self.scoped_class_info[class_name]
            self._collect_usage(class_fqn, constructor_sig, "constructor")

    def _process_method_call(self, method_call_node):
        """Process method call nodes. distinguish static ones and instance ones."""
        if method_call_node.child_by_field_name("object") is None:
            return

        obj_name = method_call_node.child_by_field_name("object").text.decode("utf-8")
        # static method for scoped classes
        if obj_name in self.scoped_class_info:
            class_fqn = self.scoped_class_info[obj_name]
            method_sig = self._construct_method_signature(method_call_node, is_static=True)
            self._collect_usage(class_fqn, method_sig, "method")

        # instance method for scoped classes
        elif obj_name in self.type_info and self.type_info[obj_name] in self.scoped_class_info:
            class_fqn = self.scoped_class_info[self.type_info[obj_name]]
            method_sig = self._construct_method_signature(method_call_node, is_static=False)
            self._collect_usage(class_fqn, method_sig, "method")

    def _process_field_access(self, field_access_node):
        """Process field access nodes."""
        obj_name = field_access_node.child_by_field_name("object").text.decode("utf-8")
        field_name = field_access_node.child_by_field_name("field").text.decode("utf-8")

        # static field for scoped classes
        if obj_name in self.scoped_class_info:
            class_fqn = self.scoped_class_info[obj_name]
            field_sig = self._construct_field_signature(field_access_node, is_static=True)
            self._collect_usage(class_fqn, field_sig, "field")

        # instance field for scoped classes
        elif obj_name in self.type_info and self.type_info[obj_name] in self.scoped_class_info:
            class_fqn = self.scoped_class_info[self.type_info[obj_name]]
            field_sig = self._construct_field_signature(field_access_node, is_static=False)
            self._collect_usage(class_fqn, field_sig, "field")

    def _get_builtin_type(self, node):
        """Get the built-in type of a node."""
        type_ = node.type

        predefined_mapping = {
            "string_literal": "String",
            "character_literal": "char",
            "true": "boolean",
            "false": "boolean",
            "null_literal": "Object",
        }
        if type_ in predefined_mapping:
            return predefined_mapping[type_]

        # Integer types (decimal, hex, octal, binary)
        integer_types = {
            "decimal_integer_literal",
            "hex_integer_literal",
            "octal_integer_literal",
            "binary_integer_literal",
        }
        if type_ in integer_types:
            text = node.text.decode("utf8").lower()
            if text.endswith("l"):
                return "long"
            else:
                return "int"

        # floating point types (decimal, hex)
        float_types = {"decimal_floating_point_literal", "hex_floating_point_literal"}
        if type_ in float_types:
            text = node.text.decode("utf8").lower()
            if text.endswith("f"):
                return "float"
            else:
                return "double"

        # class_literal
        if type_ == "class_literal":
            return "Class"

        raise ValueError(f"Unsupported built-in type '{type_}'")

    def _get_arg_type(self, node):
        type_ = node.type
        if type_ == "identifier":
            name = node.text.decode("utf-8")
            return self.type_info.get(name, "Object")
        elif any([type_.endswith("_literal"), type_ in ["true", "false"]]):
            return self._get_builtin_type(node)
        elif type_ == "field_access":
            return self.type_info.get(node.text.decode("utf-8").split(".")[-1], "Object")
        elif type_ == "object_creation_expression":
            class_name = node.child_by_field_name("type").text.decode("utf-8")
            return class_name
        elif type_ == "method_invocation":
            method_name = node.child_by_field_name("name").text.decode("utf-8")
            if method_name in self.method_decl_map:
                return self.method_decl_map[method_name][1]

        return "Object"

    def _construct_method_signature(self, method_call_node, is_static=False):
        """Construct method signature from method call node."""
        method_name = method_call_node.child_by_field_name("name").text.decode("utf-8")
        args_node = method_call_node.child_by_field_name("arguments")
        # parse method type
        parent_node = method_call_node.parent
        if parent_node.type == "expression_statement":
            method_type = "void"
        elif parent_node.type == "variable_declarator":
            method_type = parent_node.parent.child_by_field_name("type").text.decode("utf-8")
        elif parent_node.type == "assignment_expression":
            identifier_node = parent_node.child_by_field_name("left")
            method_type = self.type_info.get(identifier_node.text.decode("utf-8"), "Object")
        elif parent_node.type == "argument_list":
            parent_method_node = parent_node.parent
            parent_method = parent_method_node.child_by_field_name("name").text.decode("utf-8")
            if parent_method in self.method_decl_map:
                # get the arg index, current method_type is the parent's param type with the same index
                arg_node_list = parent_node.named_children
                arg_index = -1
                for i, arg_node in enumerate(arg_node_list):
                    if arg_node == method_call_node:
                        arg_index = i
                if arg_index == -1:
                    raise ValueError(
                        f"Cannot find the argument index for '{parent_node.text.decode()}' in '{parent_method_node.text.decode()}'"
                    )
                method_type = self.method_decl_map[parent_method][0][arg_index]
            else:
                method_type = "Object"
        else:
            method_type = "Object"
        # if the method_type is a class, use the full name
        if method_type in self.scoped_class_info:
            method_type = self.scoped_class_info[method_type]
        # if the method_type is an inner class, set it to Object
        if method_type in self.inner_class_types:
            method_type = "Object"

        # argument signature
        arg_type_list = []
        for i in range(args_node.named_child_count):
            arg_node = args_node.named_child(i)
            arg_type = self._get_arg_type(arg_node)
            # if the arg_type is a class, use the full name
            if arg_type in self.scoped_class_info:
                arg_type = self.scoped_class_info[arg_type]
            if arg_type in self.inner_class_types:
                # inner class types should be set to Object
                arg_type = "Object"
            arg_type_list.append(arg_type)

        method_sig = MethodSignature(
            is_static=is_static,
            name=method_name,
            arg_type_list=arg_type_list,
            type=method_type,
        )
        return method_sig

    def _construct_field_signature(self, field_access_node, is_static=False):
        """Construct field signature from field access node."""
        field_name = field_access_node.child_by_field_name("field").text.decode("utf-8")
        parent_node = field_access_node.parent
        if parent_node.type == "variable_declarator":
            field_type = parent_node.parent.child_by_field_name("type").text.decode("utf-8")
        elif parent_node.type == "assignment_expression":
            identifier_node = parent_node.child_by_field_name("left")
            field_type = self.type_info.get(identifier_node.text.decode("utf-8"), "Object")
        else:
            field_type = "Object"
        # if the field_type is a class, use the full name
        if field_type in self.scoped_class_info:
            field_type = self.scoped_class_info[field_type]
        # if the field_type is an inner class, set it to Object
        if field_type in self.inner_class_types:
            field_type = "Object"
        # construct field signature
        return FieldSignature(
            is_static=is_static,
            name=field_name,
            type=field_type,
        )

    def _collect_usage(self, class_fqn, signature, usage_type):
        """
        Collect usage information.
        usage_type: "constructor", "method" or "field"
        """
        assert usage_type in ["constructor", "method", "field"], f"Invalid usage type {usage_type}"
        if class_fqn not in self.usage_info:
            self.usage_info[class_fqn] = {"constructors": [], "methods": [], "fields": []}
        usage_key = f"{usage_type}s"

        hash_list = [self._get_sig_hash(sig, usage_type) for sig in self.usage_info[class_fqn][usage_key]]
        # check if the signature is already in the list
        if not self._get_sig_hash(signature, usage_type) in hash_list:
            self.usage_info[class_fqn][usage_key].append(signature)

    def _get_sig_hash(self, signature, usage_type):
        assert usage_type in ["constructor", "method", "field"], f"Invalid usage type {usage_type}"
        if usage_type == "constructor":
            return " ".join(signature["arg_type_list"])
        elif usage_type == "method":
            hash_str = "static " if signature["is_static"] else ""
            hash_str += f"{signature['name']}({', '.join(signature['arg_type_list'])})"
            return hash_str
        else:
            hash_str = "static " if signature["is_static"] else ""
            hash_str += f"{signature['name']}"
            return hash_str


def gen_mock_lib_code_ts(test_dir: Path) -> dict[str, str]:
    """
    Use tree-sitter to get all the mock lib codes for each third-party package.
    :param test_dir: The directory containing the test cases.
    :return: {"{class_fqn}": "{mock_code}"}
    """
    assert test_dir.is_dir(), f"Test directory {test_dir} does not exist!"
    # read all the test cases
    all_test_files = list(test_dir.glob("*.java"))
    if len(all_test_files) == 0:
        logger.warning(f"--> No test cases are found in {test_dir}!")
        return dict()

    logger.info(f"Generating mock lib for {len(all_test_files)} test cases in {test_dir}")
    jd_parser = JavaDependencyParser()
    jd_parser.parse_directory(test_dir)
    logger.info(f"Lib Parser result for {test_dir}: \n{json.dumps(jd_parser.usage_info, indent=2)}")
    res = jd_parser.usage_info_to_code()

    logger.info(f"Generated {len(res)} mock lib codes: \n{', '.join(list(res.keys()))}.")

    return res


if __name__ == "__main__":
    # test_with_example()
    res = gen_mock_lib_code_ts(Path("kirin_ws/test_tmp/test"))
    for class_fqn, mock_code in res.items():
        print(f"==> {class_fqn}: \n{mock_code}")
