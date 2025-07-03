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
Given a code checker written in the DSL format, please generate comprehensive and concise test cases (Java code) for the checker, including alerting and non-alerting tests. 

{additional_info}


## Important: Mandatory Guidelines for Test Case Generation
Strictly adhere to these rules when creating test cases:
1. **All Tests**. Alerting tests must contain checker-matching code patterns and can be reported by the checker, while non-alerting tests must not contain such patterns. \
Both types of tests should be generated with minimal overlapping logic.
2. **Checking Scenario Coverage**. Tests must cover all checking scenarios of the checker with minimal overlapping logic. Specifically, simplify regex coverage \
(e.g., use 1-2 options from "(a|b|c|d)"). Each test must correspond to a single scenario and ensure no duplicate scenarios across tests.
3. **Minimal Code Structure**. Keep code simple, minimal, and free of irrelevant logic. Use basic statements (e.g., separate calls) rather than \
complex patterns (e.g., chained methods) unless explicitly required in the checker. Use unchecked exceptions (e.g., RuntimeException, NullPointerException) \
rather than checked ones (e.g., IOException) unless explicitly required in the checker.
4. **Must Pass Compilation**. Guarantee 100%% compilability for every test case, which must be a complete Java file including necessary imports. \
Throw necessary exceptions to ensure the code is valid and compilable unless explicitly excluded by the checker.
5. **Correct imports**. Every used symbol must either be defined in the code or correctly imported. For third-party classes or annotations, \
you must correctly import them with fully qualified names or directly use them in the fully qualified form. \
Strictly import each symbol (class or annotation) individually instead of using "import *". 
6. **Strict Class Usage**. For any class used in the test cases, ensure the methods or fields called are exactly defined in the class. Strictly \
must use **"com.exp.AnotherClass"** if you need a different or arbitrary class, which can accept any method or field calls and not cause compilation errors.
7. **Standardized Test Code**. Each test must have only one main public class, named as "AlertingTest{{i}}" or "NonAlertingTest{{j}}" where {{i}} \
refers to the index of alerting tests and {{j}} for the non-alerting tests, both starting from 1. For each test, add clear and targeted comments \
to highlight the specific checking scenario it covers. Never mention the test index in any comment.

## Output Steps
Step 1. **Analyze checker**. Summarize the semantics of the provided checker DSL and its comprehensive checking scenarios. During summarization, \
you should carefully understand every regex pattern in the DSL and its correct matching logic. 
Step 2. **Generate Tests**. Output each alerting test wrapped in "<alerting_test>" and "</alerting_test>", and each non-alerting test wrapped in \
"<non_alerting_test>" and "</non_alerting_test>". Never use "```java".

### Your Task
### Checker DSL
<checker_dsl>
{checker_dsl}
</checker_dsl>
### Output Tests
"""

PROMPTS[
    "gen_alerting_tests"
] = """\
## General Goal
Given a code checker written in the DSL format, please generate comprehensive and concise test cases (Java code) that the checker can report. 

{additional_info}


## Important: Mandatory Guidelines for Test Case Generation
Strictly adhere to these rules when creating test cases:
1. **Checker-Reportable Tests**. Ensure every test case contains checker-matching code patterns to guarantee reportability. \
Never generate test cases that pass silently—only those explicitly reported by the checker. Notely, prioritize checker requirements \
over rule descriptions (if provided), where the rule often describes suggested proper behaviors while the checker reports improper ones. \
2. **Checking Scenario Coverage**. Tests must cover all checking scenarios of the checker with minimal overlapping logic. Specifically, simplify regex coverage \
(e.g., use 1-2 options from "(a|b|c|d)"). Each test must correspond to a single scenario and ensure no duplicate scenarios across tests.
3. **Minimal Code Structure**. Keep code simple, minimal, and free of irrelevant logic. Use basic statements (e.g., separate calls) rather than \
complex patterns (e.g., chained methods) unless explicitly required in the checker. Use unchecked exceptions (e.g., RuntimeException, NullPointerException) \
rather than checked ones (e.g., IOException) unless explicitly required in the checker.
4. **Must Pass Compilation**. Guarantee 100%% compilability for every test case, which must be a complete Java file including necessary imports. \
Do throw necessary exceptions to ensure the code is valid and compilable unless explicitly excluded by the checker.
5. **Correct Imports**. Every used symbol must either be defined in the code or correctly imported. For third-party classes or annotations, \
you must correctly import them with fully qualified names or directly use them in the fully qualified form. \
Strictly import each symbol (class or annotation) individually instead of using "import *". 
6. **Strict Class Usage**. For any class used in the test cases, ensure the methods or fields called are exactly defined in the class. Strictly must\
use **"com.exp.AnotherClass"** if you need a different or arbitrary class, which can accept any method or field calls and not cause compilation errors.
7. **Standardized Test Code**. Each test only have one main public class, named as "AlertingTest{{i}}" where {{i}} refers to the index of \
alerting tests, starting from 1. For each test, add clear and targeted comments to highlight the specific checking scenario it covers. \
Never mention the test index in any comment.

## Output Steps
Step 1. **Analyze checker**. Summarize the semantics of the provided checker DSL and its comprehensive checking scenarios. During summarization, \
you should carefully understand every regex pattern in the DSL and its correct matching logic. 
Step 2. **Generate Alerting Tests**. Output each alerting test wrapped in "<alerting_test>" and "</alerting_test>". Never use "```java".

### Your Task
### Checker DSL
<checker_dsl>
{checker_dsl}
</checker_dsl>
### Output Alerting Tests
"""

PROMPTS[
    "gen_non_alerting_tests"
] = """\
## General Goal
Given a code checker written in the DSL format, please generate comprehensive and concise test cases (Java code) that the checker will not report. 

{additional_info}


## Important: Mandatory Guidelines for Test Case Generation
Strictly adhere to these rules when creating test cases:
1. **Checker-Passing Tests**. Ensure every test case doesn't contain checker-matching code patterns to guarantee that it will not be reported by the checker. \
I only care about these non-alerting test cases, which are often compliant examples for the inherent rule of the checker.
2. **Checking Scenario Coverage**. Tests must cover all checking scenarios of the checker with minimal overlapping logic. Specifically, simplify regex coverage \
(e.g., use 1-2 options from "(a|b|c|d)"). Each test must correspond to a single scenario and ensure no duplicate scenarios across tests.
3. **Minimal Code Structure**. Keep code simple, minimal, and free of irrelevant logic. Use basic statements (e.g., separate calls) rather than \
complex patterns (e.g., chained methods) unless explicitly required in the checker. Use unchecked exceptions (e.g., RuntimeException, NullPointerException) \
rather than checked ones (e.g., IOException) unless explicitly required in the checker.
4. **Must Pass Compilation**. Guarantee 100%% compilability for every test case, which must be a complete Java file including necessary imports. \
Do throw necessary exceptions to ensure the code is valid and compilable unless explicitly excluded by the checker.
5. **Correct Imports**. Every used symbol must either be defined in the code or correctly imported. For third-party classes or annotations, \
you must correctly import them with fully qualified names or directly use them in the fully qualified form. \
Strictly import each symbol (class or annotation) individually instead of using "import *". 
6. **Strict Class Usage**. For any class used in the test cases, ensure the methods or fields called are exactly defined in the class. Strictly must\
use **"com.exp.AnotherClass"** if you need a different or arbitrary class, which can accept any method or field calls and not cause compilation errors.
7. **Standardized Test Code**. Each test only have one main public class, named as "NonAlertingTest{{i}}" where {{i}} refers to the index of \
non-alerting tests, starting from 1. For each test, add clear and targeted comments to highlight the specific checking scenario it covers. \
Never mention the test index in any comment.

## Output Steps
Step 1. **Analyze checker**. Summarize the semantics of the provided checker DSL and its comprehensive checking scenarios. During summarization, \
you should carefully understand every regex pattern in the DSL and its correct matching logic. 
Step 2. **Generate Non-alerting Tests**. Output each non-alerting test wrapped in "<non_alerting_test>" and "</non_alerting_test>". Never use "```java".

### Your Task
### Checker DSL
<checker_dsl
{checker_dsl}
</checker_dsl
### Output Non-Alerting Tests
"""

PROMPTS[
    "refine_alerting_tests"
] = """\
## General Goal
Given a code checker (in DSL format) and test cases (in Java code) that **fail to trigger alerts**, modify each test case minimally to ensure \
the checker reports it. Preserve the test's core scenario and main class name while closing the gap between the checker's logic and test code.

### Critical Rules
1. **Trigger Checker Reporting**  
   - Analyze why the original test wasn't reported by comparing the DSL's violation patterns with test code
   - Make surgical changes ONLY where needed to match checker's detection logic
2. **Preserve Core Identity**  
   - Keep main class name identical (e.g., `AlertingTest1` remains unchanged)
   - Retain existing imports and core logic flow
   - The modified test must still be a complete Java file that can compile successfully
   - Retain or refine comments to highlight the specific checking scenario for each test and never mention the test index in any comment

   
### Checker DSL
<checker_dsl>
{checker_dsl}
</checker_dsl>

### Test Cases Should be Reported by the Checker but not
{wrapped_tests}

First, carefully analyze the provided test cases and the checker DSL to identify why the tests are not reported. Then, output modified \
test cases in the same order without detailed explanations, each wrapped in "<alerting_test>" and "</alerting_test>".
"""

PROMPTS[
    "refine_non_alerting_tests"
] = """\
## General Goal
Given a code checker (in DSL format) and test cases (Java code) that **are incorrectly triggering alerts**, modify each test case minimally to ensure the checker no longer reports them. \
Preserve the test's core scenario and main class name while closing the gap between the checker's logic and test code.

### Critical Rules
1. **Suppress Checker Reporting**  
   - Analyze why the original test was reported by comparing the DSL's violation patterns with test code
   - Make surgical changes ONLY where needed to avoid matching checker's detection logic
   - Ensure modifications preserve the test's original valid behavior
2. **Preserve Core Identity**  
   - Maintain identical main class names (e.g., `NonAlertingTest1` unchanged)
   - Retain existing imports and primary logic flow
   - All modifications must yield compilable Java files
   - Retain or refine comments to highlight the specific checking scenario for each test and never mention the test index in any comment

### Checker DSL
<checker_dsl>
{checker_dsl}
</checker_dsl>

### Test Cases Unexpectedly Reported by Checker
{wrapped_tests}

First, carefully analyze the provided test cases and the checker DSL to identify why the tests are incorrectly reported. Then, output \
modified test cases in the same order without detailed explanations, each wrapped in "<non_alerting_test>" and "</non_alerting_test>".
"""

PROMPTS[
    "gen_mock_lib_code"
] = """\
## General Goal
Write mock Java classes for third-party libraries used in a project, based on provided code snippets. \
The mocks must replicate exact method signatures and field declarations referenced in the snippets, with minimum method bodies, default return \
and field values (e.g., null, 0, false, '', etc.). Always using **Object** as argument/return/field types if possible to minimize nested dependencies.

### Output Format
Directly Output the complete Java files (with correct pacakge declaration) for each mock library, each wrapped in "<lib-{{calss_fqn}}>" and \
"</lib-{{class_fqn}}>" without detailed explanations. {{class_fqn}} is the corresponding fully qualified class name of the mock library, e.g., \
output code of the class "com.example.AnotherClass" should be wrapped in "<lib-com.example.AnotherClass>" and "</lib-com.example.AnotherClass>". 

### Input
Here are the aggregated code snippets for references:
<input_code_snippets>
{code_snippets}
</input_code_snippets>

{potential_libs}


## Output Mock Java Classes
"""

PROMPTS[
    "fix_syntax_error"
] = """\
## General Goal
You are an expert in Java programming and code analysis. I will provide you with a list of Java codes each wrapped in "```java" and "```". \
Each code is the content of a complete Java file containing syntax errors, and you need to fix these errors in them without changing the \
identifier names, comments, structure and behaviors in the code. Directly output the fixed code in the same order as the input, each wrapped in "```java" and "```".

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

Please fix the mock library code to make it pass compilation and directly output the fixed code files with the same format, \
each also wrapped in "<lib-{{calss_fqn}}>" and "</lib-{{class_fqn}}>".
"""

PROMPTS[
    "fix_test_compile_with_lib"
] = """\
## General Goal
You are an expert in Java programming and code analysis. Your goal is to fix compilation errors in the given checker tests (Java code files).\
These tests are designed to be reported (alerting) or passed (non-alerting) by a static code checker written in DSL format but fail to be compiled. \
As inputs, I will provide you with a list of the checker tests, their mocked third-party library code as dependencies, and the error message. \
When compiling the input tests with the provided library code, compilation errors with the error message will be raised. \
You need to resolve these errors by modifying the test and the library code if necessary. 

### Madatory Guidelines for Fixing
1. Fix Compilation Errors. Analyze the failure cause for each test and fix all compilation errors while ignoring warnings. Since the error \
message maybe incomplete, you also need to carefully analyze the inputs and fix any similar or potential compilation-failure-inducing problems. \
Never change the original comments unless breaking code changes are introduced.
2. Never change the original alerting or non-alerting logic for each test. During fixing, you must ensure that the alerting tests \
still contain checker-matching code patterns to guarantee reportability, while the non-alerting tests must not contain such patterns. \
The checking scenario of a test can be inferred from both the original code comments and main class name (AlertingTest is designed to \
be reported while NonAlertingTest is expected be non-alerting).
3. Library Code Requirements. Each library code is just a mock code for test compilation with minimal logic. Always use minimum method bodies, default return \
and field values (e.g., null, 0, false, '', etc.). Always using **Object** as argument/return/field types if possible to minimize nested dependencies. library code \
fix should still follow these requirements.


### Input and Output Format
For both input and output, each checker test is wrapped in "<java_file>" and "</java_file>" and each library code is wrapped in \
"<lib-{{calss_fqn}}>" and "</lib-{{class_fqn}}>". Output all the fixed tests (must in the same order as input) \
and library code wrapped in the correct format. Unchanged input code files must also be output as they are.

### Input
- Checker test files:
{wrapped_java_code}

- Mock Library code files:
{wrapped_lib_code}

- Compilation error message:
{error_msg}

- Checker DSL:
<checker_dsl>
{checker_dsl}
</checker_dsl>

### Output
For each test, first fully understand the checking scenario it covers, then analyze the compilation errors and fix the test without changing \
its scenario and the original alerting/non-alerting logic. 
"""

PROMPTS[
    "fix_test_compile_wo_lib"
] = """\
## General Goal
You are an expert in Java programming and code analysis. Your goal is to fix compilation errors in the given checker tests (Java code files).\
These tests are designed to be reported (alerting) or passed (non-alerting) by a static code checker written in DSL format but all fail to be compiled. \
As inputs, I will provide you with a list of the checker tests and the error message. When compiling these tests directly without dependencies, \
compilation errors with the error message will be raised. You need to resolve these errors by refining the test code. 

### Madatory Guidelines for Fixing
1. Fix Compilation Errors. Analyze the failure cause for each test and fix all compilation errors while ignoring warnings. Since the error \
message maybe incomplete, you need to carefully analyze the inputs and fix any similar or potential compilation-failure-inducing problems. \
Never change the original comments unless breaking code changes are introduced.
2. Never change the original alerting or non-alerting logic for each test. During fixing, you must ensure that the alerting tests \
still contain checker-matching code patterns to guarantee reportability, while the non-alerting tests must not contain such patterns. \
The checking scenario of a test can be inferred from both the original code comments and main class name (AlertingTest is designed to \
be reported while NonAlertingTest is expected be non-alerting).
3. Library Code Requirements. If you add import statements or use third-party dependencies with fully qualified names, you must also provide mock library code \
for them. Each mock library code is uesd for test compilation with minimal logic. Always use minimum method bodies, default return \
and field values (e.g., null, 0, false, '', etc.). Always using **Object** as argument/return/field types if possible to minimize nested dependencies.


### Input and Output Format
For both input and output, each Java code file is wrapped in "<java_file>" and "</java_file>". If you add any third-party dependencies as imports, \
the library code should also be output, each wrapped in "<lib-{{calss_fqn}}>" and "</lib-{{class_fqn}}>". \
Output all the fixed code files (in the same order as input) and library code (if necessary) wrapped in the correct format.

### Input
- Checker test files:
{wrapped_java_code}

- Compilation error message:
{error_msg}

- Checker DSL:
<checker_dsl>
{checker_dsl}
</checker_dsl>

### Output
For each test, first fully understand the checking scenario it covers, then analyze the compilation errors and fix the test without changing \
its scenario and the original alerting/non-alerting logic. 
"""
