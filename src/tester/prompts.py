SYS_PROMPTS = {}
PROMPTS = {}

SYS_PROMPTS[
    "gen_tests"
] = """\
You are an expert with deep experience in software analysis and development. \
You are very familiar with a tool for code analysis that uses code checkers in DSL (Domain Specific Language) format to find matches in the Java codes. \
Checkers are designed to find specific AST nodes or code elements that satisfy given conditions. \
You have a comprehensive understanding of various checker rules and their corresponding code checking scenarios."""

PROMPTS[
    "gen_all_tests"
] = """\
## General Goal
Given a code checker written in the DSL format, please generate comprehensive test cases (Java codes) for me. 

## Additional information
### Explanations of DSL nodes and corresponding properties to better understand checkers in DSL formats
{node_properties}

## Notice: Must-follow guidelines
Here are detailed guildlines that you must always bear in mind and follow:
1. Test cases include both positive ones that will be reported by the checker and negative ones that pass the checker without issues.
2. Every test case should be able to pass compilation and keep minimal, excluding any code statements that are irrelevant to the checker.
3. Include simple, necessary comments to clarify the purpose of each test case and the label ("positive" or "negative").
4. Ensure that each case covering the same checking scenario only occurs once and that all possible scenarios are covered.
5. Test cases should be generally similar but vary in some specific code parts that reflect the differences of their checking scenarios.
6. Output test cases to me without detailed explanations and every test case must be independently surrounded with "```java" and "```".

## Your Task
### Checker DSL
```dsl
{dsl_input}
```
### Output
"""

PROMPTS[
    "gen_pos_tests"
] = """\
## General Goal
Given a code checker written in the DSL format, please generate comprehensive and concise test cases (Java codes) that the checker can report. 

{additional_info}
## Notice: Must-follow guidelines
Here are detailed guildlines that you must always bear in mind and follow:
1. Each test case must be reported by the checker, which means it contains checker-matching code patterns. Notely, do not be misled by the rule \
descriptions (if exists), which describes the suggested proper behaviors while the checker reports improper ones. Only generate test cases \
that can be reported by the checker.
2. Each test case should keep clear, simple and minimal, excluding any code that is irrelevant to the checker. Include simple, necessary comments \
to clarify the purpose of each test case and show their differences. 
3. Each test case must be able to pass compilation. Every used symbol should either be defined in the test case itself or correctly imported. \
Do not import unused classes or packages.
"com.example.AnotherClass", method "anotherMethod" or field "anotherField" with proper import statements and remember to avoid dependency conflits.\
4. Ensure that each case covering the same checking scenario only occurs once and that all necessary scenarios are covered. Specifically, \
for regex expressions that have multiple options like "(a|b|c|d)", just use one or two of them to make the test suite concise.   
5. Do not mention the test index in any comment in the test case. The test index should only occur in the main public class name of each test case. \
Specifically, strictly using "PositiveTest{{i}}" as each test's main public class name where {{i}} is the test index.
6. Output the test cases to me without detailed explanations and every test case must be independently surrounded with "```java" and "```".

### Your Task
### Checker DSL
```dsl
{dsl_input}
```
### Output
"""

PROMPTS[
    "gen_mock_lib_code"
] = """\
## General Goal
Write mock Java classes for third-party libraries used in a project, based on provided code snippets. Note that the project fail to compile due \
to missing third-party dependencies, so do generate the mock third-party classes for the code snippets. The mocks must replicate exact method \
signatures and field declarations referenced in the snippets, with minimum method bodies, default return \
and field values (e.g., null, 0, false, '', etc.). Prioritize using Object as argument/return/field types when possible to simplify dependencies. 

### Output Format
Directly Output the complete Java files (with correct pacakge declaration) for each mock library, each wrapped in "<lib-{{calss_fqn}}>" and \
"</lib-{{class_fqn}}>" without detailed explanations. {{class_fqn}} is the corresponding fully qualified class name of the mock library, e.g., \
output code of the class "com.example.AnotherClass" should be wrapped in "<lib-com.example.AnotherClass>" and "</lib-com.example.AnotherClass>". 

### Input
Here are the aggregated code snippets for references:
<input_code_snippets>
{code_snippets}
</input_code_snippets>

{additional_info}
## Output Mock Java Classes
"""

PROMPTS[
    "fix_syntax_error"
] = """\
## General Goal
You are an expert in Java programming and code analysis. I will provide you with a list of Java codes each wrapped in "```java" and "```". \
Each code is the content of a complete Java file containing syntax errors, and you need to fix these errors in them without changing the \
identifier names, structure and behaviors in the code. Directly output the fixed code in the same order as the input, each wrapped in "```java" and "```".

### Input java code
{wrapped_java_code}

### Output
"""

PROMPTS[
    "fix_mock_lib_code"
] = """\
The mock library code files generated in the last step are not able to pass package compilation using "javac" and "jar". \
Here are the compilation errors:
<error_msg>
{error_msg}
</error_msg>

Please fix the mock library code to make it pass compilation and directly output the fixed code files with the same format, each also wrapped in "<lib-{{calss_fqn}}>" \
and "</lib-{{class_fqn}}>".
"""

PROMPTS[
    "fix_test_compile_with_lib"
] = """\
## General Goal
You are an expert in Java programming and code analysis. Your goal is to fix the compilation errors in the providing Java code files \
(warnings can be ignored). As inputs, I will provide you with a list of the Java code files, their mocked third-party library code as \
dependencies and the error message. When compiling these Java files with the dependency libs, the compiler reports errors. \
You need to fix these errors by modifying the Java files and the library code if necessary. \
Keep the original code identifier naming, structure and logic as much as possible. \

### Input and Output Format
For both input and output, each Java code file is wrapped in "<java_file>" and "</java_file>" and each library code is wrapped in \
"<lib-{{calss_fqn}}>" and "</lib-{{class_fqn}}>". Directly output all the fixed code files and library code wrapped in the same format. \
Unchanged code files and library code should also be output as they are.

### Input
- Mock Library code files:
{wrapped_lib_code}
- Java code files:
{wrapped_java_code}
- Compilation error message:
{error_msg}

### Output
"""

PROMPTS[
    "fix_test_compile_wo_lib"
] = """\
## General Goal
You are an expert in Java programming and code analysis. Your goal is to fix the compilation errors in the providing Java code files \
(warnings can be ignored). As inputs, I will provide you with a list of the Java code files and the compilation error message.

### Input and Output Format
For both input and output, each Java code file must be wrapped in "<java_file>" and "</java_file>". \
Directly output the fixed code files wrapped in the same format. Unchanged code files and library code should also be output as they are.

### Input
- Java code files:
{wrapped_java_code}
- Compilation error message:
{error_msg}

### Output
"""
