## Additional information
### Extra Explanations of DSL Semantics
- For a variableAccess node va, "va.variable" locates the variable definition of the used variable, which is a variableDeclaration node.
- For a functionCall node fc, "fc.function" locates the function definition of the called function, which is a functionDeclaration node.
- For a functionDeclaration node fd, "fd.functionUsage" locates all the function uasges that call fd, which are functionCall nodes. "fd.callers" locates all the callers of fd, which are functionDeclaration nodes that call fd. "fd.functionCalls" locates all the function calls in the body of fd, which are functionCall nodes. "fd.subMethods" locates all the overridden methods of fd, which are functionDeclaration nodes. "fd.superMethods" locates all the parent methods of fd, which are also functionDeclaration nodes.
- Indexing in DSL is 0-based, e.g., argumentIndex 0 refers to the first argument.
- Strings the DSL are in the regex format, which may contain inline flags: "(?i)" means Case-insensitivity mode; (?s) means Dot-all mode; (?m) means multiline mode; (?x) means ignoring whitespace. 