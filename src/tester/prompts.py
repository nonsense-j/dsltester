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
Given a code checker written in the DSL format, please generate comprehensive test cases (Java codes) that the checker can report. 

## Additional information
### Explanations of DSL nodes and corresponding properties to better understand checkers in DSL formats
{node_properties}

## Notice: Must-follow guidelines
Here are detailed guildlines that you must always bear in mind and follow:
1. Each test cases must be reported by the checker, which means checker-matching code patterns must be found in them. Notely, do not be misled by \
the rule descriptions (if exists), which describes the suggested proper behaviors while the checker reports improper ones. Since we only need test cases that \
will be reported by the checker, all the generated test cases should disobey the rule descriptions.
2. Each test case must be able to pass compilation, thus, it must be a complete code file with correct import statements (do not use *). Specifically, \
use class "com.example.AnotherClass", method "anotherMethod" or field "anotherField" when you are referring to a random or mismatch class, method, field.
3. Each test case should keep simple and minimal, excluding any code statements that are irrelevant to the checker.
4. Include simple, necessary comments to clarify the purpose of each test case and show their differences.
5. Ensure that each case covering the same checking scenario only occurs once and that all possible scenarios are covered. Specifically, \
for regex expressions that have multiple options like "(a|b|c|d)", just use one or two of them to make the test suite concise.   
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
Write mock Java classes for third-party libraries used in a project, based on provided code snippets. The mocks must replicate exact \
method signatures and field declarations referenced in the snippets, with empty method bodies, default return and field values \
(e.g., null, 0, false, '', etc.). Prioritize using Object as argument/return/field types when possible to simplify dependencies. \
Output the complete Java files (with correct pacakge declaration) for each mock library, each wrapped in "```java" and "```".

Here are the aggregated code snippets for references:
```java
{code_snippets}
```

## mock Java classes
"""
