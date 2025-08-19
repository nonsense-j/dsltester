SYS_PROMPTS = {}
PROMPTS = {}

SYS_PROMPTS[
    "gen_tests"
] = """\
You are an expert with deep experience in software analysis and development. You are very familiar with static code analysis \
techniques, especially AST (Abstract Syntax Tree) analysis and data flow analysis for Java codes. You
that uses code checkers in DSL (Domain Specific Language) format to find matches in the Java codes. \
Checkers are designed to find specific AST nodes or code elements that satisfy given conditions. \
You have a comprehensive understanding of various checker rules and their corresponding code checking scenarios."""

PROMPTS[
    "gen_all_tests"
] = """\
# General Goal
Given a code checker written in the DSL format, please generate comprehensive and concise test cases (Java code) for the checker, including alerting and non-alerting tests. 

# Important: Mandatory Guidelines for Test Case Generation
Strictly adhere to these rules when creating test cases:
1. **All Tests**. Alerting tests must contain checker-matching code patterns and can be reported by the checker, while non-alerting tests must not contain such patterns. \
Both types of tests should be generated with minimal overlapping logic.
2. **Checking Scenario Coverage**. Tests must cover all checking scenarios of the checker with minimal overlapping logic. Specifically, simplify regex coverage \
(e.g., use 1-2 options from "(a|b|c|d)"). Each test must correspond to a single scenario and ensure no duplicate scenarios across tests.
3. **Minimal Code Structure**. Keep code simple, minimal, and free of irrelevant logic. Use basic statements (e.g., separate calls) rather than \
complex patterns (e.g., chained methods) unless explicitly required in the checker. Use unchecked exceptions (e.g., RuntimeException, NullPointerException) \
rather than checked ones (e.g., IOException) unless explicitly required in the checker.
4. **Must Pass Compilation**. Guarantee 100%% compilability for every test case, which must be a complete Java file with a public main class and necessary imports. \
Throw necessary exceptions to ensure the code is valid and compilable unless explicitly excluded by the checker.
5. **Correct imports**. Every used symbol must either be defined in the code or correctly imported. For third-party classes or annotations, \
you must correctly import them with fully qualified names or directly use them in the fully qualified form. \
Strictly import each symbol (class or annotation) individually instead of using "import *". 
6. **Strict Class Usage**. For any class used in the test cases, ensure the methods or fields called are exactly defined in the class. Strictly \
must use **"com.exp.AnotherClass"** if you need a different or arbitrary class, which can accept any method or field calls and not cause compilation errors.
7. **Standardized Test Code**. Each test must include a main public class, whose name indicates the checking scenario it covers concisely. \
Also, add clear and targeted comments for each test, where the first line of the test should be a general comment describing the checking scenario \
as "// (Alert / Not Alert): {{checking_scenario}}". Never mention test index in the test code since the order may be changed in the future.

{additional_info}

# Output Steps
Step 1. **Analyze checker**. Summarize the semantics of the provided checker DSL and its comprehensive checking scenarios including simple and complex ones. \
During summarization, you must strictly adhere to the Important Explanations of DSL Semantics in the Additional Information section.
Step 2. **Generate Tests**. Directly output each alerting test wrapped in "<alerting_test>" and "</alerting_test>", and each non-alerting test wrapped in \
"<non_alerting_test>" and "</non_alerting_test>". Never use "```java".

# Your Task
### Checker DSL
<checker_dsl>
{checker_dsl}
</checker_dsl>
### Output Tests
"""

PROMPTS[
    "gen_alerting_tests"
] = """\
# General Goal
Given a code checker written in the DSL format, please generate comprehensive and concise test cases (Java code) that the checker can report. 

# Important: Mandatory Guidelines for Test Case Generation
Strictly adhere to these rules when creating test cases:
1. **Checker-Reportable Tests**. Ensure every test case contains checker-matching code patterns to guarantee reportability. \
Never generate test cases that pass silently—only those explicitly reported by the checker. Notely, prioritize checker requirements \
over rule descriptions (if provided), where the rule often describes suggested proper behaviors while the checker reports improper ones. \
2. **Checking Scenario Coverage**. Tests must cover all checking scenarios of the checker with minimal overlapping logic. Specifically, simplify regex coverage \
(e.g., use 1-2 options from "(a|b|c|d)"). Each test must correspond to a single scenario and ensure no duplicate scenarios across tests.
3. **Minimal Code Structure**. Keep code simple, minimal, and free of irrelevant logic. Use basic statements (e.g., separate calls) rather than \
complex patterns (e.g., chained methods) unless explicitly required in the checker. Use unchecked exceptions (e.g., RuntimeException, NullPointerException) \
rather than checked ones (e.g., IOException) unless explicitly required in the checker.
4. **Must Pass Compilation**. Guarantee 100%% compilability for every test case, which must be a complete Java file with a public main class and necessary imports. \
Do throw necessary exceptions to ensure the code is valid and compilable unless explicitly excluded by the checker.
5. **Correct Imports**. Every used symbol must either be defined in the code or correctly imported. For third-party classes or annotations, \
you must correctly import them with fully qualified names or directly use them in the fully qualified form. \
Strictly import each symbol (class or annotation) individually instead of using "import *". 
6. **Strict Class Usage**. For any class used in the test cases, ensure the methods or fields called are exactly defined in the class. Strictly must\
use **"com.exp.AnotherClass"** if you need a different or arbitrary class, which can accept any method or field calls and not cause compilation errors.
7. **Standardized Test Code**. Each test must include a main public class, whose name indicates the checking scenario it covers concisely. \
Also, add clear and targeted comments for each test, where the first line of the test should be a general comment describing the checking scenario \
as "// Alert: {{checking_scenario}}". Never mention test index in the test code since the order may be changed in the future.

{additional_info}

# Output Steps
Step 1. **Analyze checker**. Summarize the semantics of the provided checker DSL and its comprehensive checking scenarios including simple and complex ones. \
During summarization, you must strictly adhere to the Important Explanations of DSL Semantics in the Additional Information section.
Step 2. **Generate Alerting Tests**. Directly output only alerting tests, each wrapped in "<alerting_test>" and "</alerting_test>". Never use "```java".

# Your Task
### Checker DSL
<checker_dsl>
{checker_dsl}
</checker_dsl>
### Output Alerting Tests
"""

PROMPTS[
    "gen_non_alerting_tests"
] = """\
# General Goal
Given a code checker written in the DSL format, please generate comprehensive and concise test cases (Java code) that the checker will not report. 

# Important: Mandatory Guidelines for Test Case Generation
Strictly adhere to these rules when creating test cases:
1. **Checker-Passing Tests**. Ensure every test case doesn't contain checker-matching code patterns to guarantee that it will not be reported by the checker. \
I only care about these non-alerting test cases, which are often compliant examples for the inherent rule of the checker.
2. **Checking Scenario Coverage**. Tests must cover all checking scenarios of the checker with minimal overlapping logic. Specifically, simplify regex coverage \
(e.g., use 1-2 options from "(a|b|c|d)"). Each test must correspond to a single scenario and ensure no duplicate scenarios across tests.
3. **Minimal Code Structure**. Keep code simple, minimal, and free of irrelevant logic. Use basic statements (e.g., separate calls) rather than \
complex patterns (e.g., chained methods) unless explicitly required in the checker. Use unchecked exceptions (e.g., RuntimeException, NullPointerException) \
rather than checked ones (e.g., IOException) unless explicitly required in the checker.
4. **Must Pass Compilation**. Guarantee 100%% compilability for every test case, which must be a complete Java file with a public main class and necessary imports. \
Do throw necessary exceptions to ensure the code is valid and compilable unless explicitly excluded by the checker.
5. **Correct Imports**. Every used symbol must either be defined in the code or correctly imported. For third-party classes or annotations, \
you must correctly import them with fully qualified names or directly use them in the fully qualified form. \
Strictly import each symbol (class or annotation) individually instead of using "import *". 
6. **Strict Class Usage**. For any class used in the test cases, ensure the methods or fields called are exactly defined in the class. Strictly must\
use **"com.exp.AnotherClass"** if you need a different or arbitrary class, which can accept any method or field calls and not cause compilation errors.
7. **Standardized Test Code**. Each test must include a main public class, whose name indicates the checking scenario it covers concisely. \
Also, add clear and targeted comments for each test, where the first line of the test should be a general comment describing the checking scenario \
as "// Not Alert: {{checking_scenario}}". Never mention test index in the test code since the order may be changed in the future.

{additional_info}

# Output Steps
Step 1. **Analyze checker**. Summarize the semantics of the provided checker DSL and its comprehensive checking scenarios including simple and complex ones. \
During summarization, you must strictly adhere to the Important Explanations of DSL Semantics in the Additional Information section.
Step 2. **Generate Non-alerting Tests**. Directly output only non-alerting tests, each wrapped in "<non_alerting_test>" and "</non_alerting_test>". Never use "```java".

# Your Task
### Checker DSL
<checker_dsl
{checker_dsl}
</checker_dsl
### Output Non-Alerting Tests
"""

PROMPTS[
    "refine_alerting_tests"
] = """\
# General Goal
Given a code checker (in DSL format) and test cases (in Java code) that **fail to trigger alerts**, modify each test case minimally to ensure \
the checker reports it. Preserve the test's core scenario and main class name while closing the gap between the checker's logic and test code. \
Only when you strongly persist that the test has already satisfied the checking logic, you can output it without any modification.

# Critical Rules
1. **Trigger Checker Reporting**  
   - Analyze why the original test wasn't reported by comparing the DSL's violation patterns with test code
   - Make surgical changes ONLY where needed to match checker's detection logic
2. **Preserve Core Identity**
   - Retain existing imports and core logic flow
   - The modified test must still be a complete Java file that can compile successfully
   - Retain or refine comments to highlight the specific checking scenario for each test and never mention the test index in any comment

{additional_info}

# Your Task
### Checker DSL
<checker_dsl>
{checker_dsl}
</checker_dsl>
### Test Cases Should be Reported by the Checker but not
{wrapped_tests}
### Output
First, carefully analyze the provided test cases and the checker DSL to identify why the tests are not reported. Then, output modified \
test cases in the same order without detailed explanations, each wrapped in "<alerting_test>" and "</alerting_test>".
"""

PROMPTS[
    "refine_non_alerting_tests"
] = """\
# General Goal
Given a code checker (in DSL format) and test cases (Java code) that **are incorrectly triggering alerts**, modify each test case minimally to ensure the checker no longer reports them. \
Preserve the test's core scenario and main class name while closing the gap between the checker's logic and test code. \
Only when you strongly persist that the test has already passed the checking logic, you can output it without any modification.

# Critical Rules
1. **Suppress Checker Reporting**  
   - Analyze why the original test was reported by comparing the DSL's violation patterns with test code
   - Make surgical changes ONLY where needed to avoid matching checker's detection logic
   - Ensure modifications preserve the test's original valid behavior
2. **Preserve Core Identity**  
   - Retain existing imports and primary logic flow
   - All modifications must yield compilable Java files
   - Retain or refine comments to highlight the specific checking scenario for each test and never mention the test index in any comment

{additional_info}

# Your Task
### Checker DSL
<checker_dsl>
{checker_dsl}
</checker_dsl>
### Test Cases Unexpectedly Reported by Checker
{wrapped_tests}
### Output
First, carefully analyze the provided test cases and the checker DSL to identify why the tests are incorrectly reported. Then, output \
modified test cases in the same order without detailed explanations, each wrapped in "<non_alerting_test>" and "</non_alerting_test>".
"""

PROMPTS[
    "gen_mock_lib_code"
] = """\
# General Goal
Write mock Java classes for third-party libraries used in a project, based on provided code snippets. \
The mocks must replicate exact method signatures and field declarations referenced in the snippets, with minimum method bodies, default return \
and field values (e.g., null, 0, false, '', etc.). Always using **Object** as argument/return/field types if possible to minimize nested dependencies.

# Output Format
Directly Output the complete Java files (with correct pacakge declaration) for each mock library, each wrapped in "<lib-{{calss_fqn}}>" and \
"</lib-{{class_fqn}}>" without detailed explanations. {{class_fqn}} is the corresponding fully qualified class name of the mock library, e.g., \
output code of the class "com.example.AnotherClass" should be wrapped in "<lib-com.example.AnotherClass>" and "</lib-com.example.AnotherClass>". 

# Input
Here are the aggregated code snippets for references:
<input_code_snippets>
{code_snippets}
</input_code_snippets>

{potential_libs}


# Output Mock Java Classes
"""

PROMPTS[
    "fix_syntax_error"
] = """\
# General Goal
You are an expert in Java programming and code analysis. I will provide you with a list of Java codes each wrapped in "```java" and "```". \
Each code is the content of a complete Java file containing syntax errors, and you need to fix these errors in them without changing the \
identifier names, comments, structure and behaviors in the code. Directly output the fixed code in the same order as the input, each wrapped in "```java" and "```".

# Input java code
{wrapped_java_code}

# Output java code
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
# General Goal
You are an expert in Java programming and code analysis. Your goal is to fix compilation errors in the given checker tests (Java code files).\
These tests are designed to be reported (alerting) or passed (non-alerting) by a static code checker written in DSL format but fail to be compiled. \
As inputs, I will provide you with a list of the failed checker tests, their mocked third-party library code as dependencies, and the error messages. \
Every test fails when compiled with the provided library code, and you need to resolve these errors by refining the test code and the library code if necessary.

# Madatory Guidelines for Fixing
1. Fix Compilation Errors. Analyze the failure cause for each test and fix all compilation errors while ignoring warnings. Since the error \
message maybe incomplete, you also need to carefully analyze the inputs and fix any similar or potential compilation-failure-inducing problems. \
Never change the original comments unless breaking code changes are introduced.
2. Never change the original alerting or non-alerting logic for each test. During fixing, you must ensure that the alerting tests \
still contain checker-matching code patterns to guarantee reportability, while the non-alerting tests must not contain such patterns. 
3. Library Code Requirements. Each library code is just a mock code for test compilation with minimal logic. Always use minimum method bodies, default return \
and field values (e.g., null, 0, false, '', etc.). Always using **Object** as argument/return/field types if possible to minimize nested dependencies. library code \
fix should still follow these requirements.

# Input and Output Format
- Each alerting Checker Test is wrapped in "<alerting_test>" and "</alerting_test>".
- Each non-alerting Checker Test is wrapped in "<non_alerting_test>" and "</non_alerting_test>".
- Each library code is wrapped in "<lib-{{calss_fqn}}>" and "</lib-{{class_fqn}}>".
Output all the fixed tests (must in the same order with the same count as input) and library code (only those that need to be fixed, each must still be complete) \
with the correct wrapping format.

# Your Task
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
# General Goal
You are an expert in Java programming and code analysis. Your goal is to fix compilation errors in the given checker tests (Java code files).\
These tests are designed to be reported (alerting) or passed (non-alerting) by a static code checker written in DSL format but all fail to be compiled. \
As inputs, I will provide you with a list of the failed checker tests and the error messages. Every test fails when directly compiled without dependencies, \
and you need to resolve these errors by refining the test code.

# Madatory Guidelines for Fixing
1. Fix Compilation Errors. Analyze the failure cause for each test and fix all compilation errors while ignoring warnings. Since the error \
message maybe incomplete, you need to carefully analyze the inputs and fix any similar or potential compilation-failure-inducing problems. \
Never change the original comments unless breaking code changes are introduced.
2. Never change the original alerting or non-alerting logic for each test. During fixing, you must ensure that the alerting tests \
still contain checker-matching code patterns to guarantee reportability, while the non-alerting tests must not contain such patterns. 
3. Library Code Requirements. If you add import statements or use third-party dependencies with fully qualified names, you must also provide mock library code \
for them. Each mock library code is uesd for test compilation with minimal logic. Always use minimum method bodies, default return \
and field values (e.g., null, 0, false, '', etc.). Always using **Object** as argument/return/field types if possible to minimize nested dependencies.


# Input and Output Format
For both input and output, each alerting test is wrapped in "<alerting_test>" and "</alerting_test>", while each non-alerting test is wrapped in \
"<non_alerting_test>" and "</non_alerting_test>". If you add any third-party dependencies as imports, the library code should also be output, \
each wrapped in "<lib-{{calss_fqn}}>" and "</lib-{{class_fqn}}>". Output all the fixed tests (must in the same order with the same count as input) \
and library code (if necessary, each must be a complete lib file) with the correct wrapping format.

# Your Task
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

PROMPTS[
    "transform_checker_test"
] = """\
You are a creative and expert Java programmer specializing in code transformation to test static analysis tools. Your mission is to refactor a given Java code snippet in a concise and effective manner while preserving its semantics.

---

### The Golden Rule: Absolute Semantic Preservation

The transformed code **must** be a perfect and clear semantic equivalent of the original. It must compile successfully and exhibit the exact same runtime behavior, produce the identical output, and have the same side effects for all possible inputs. **This is the most important directive; there are no exceptions.**

---

### Guiding Principles for Transformation

Instead of following a rigid list, use the following principles to inspire your transformations. You are encouraged to be inventive and combine these ideas to create unique code variants that match best practices. Note that you are not restricted to these principles.

* **Obfuscate Data Pathways and Representation.**
    Introduce layers of indirection between where data is defined and where it is used. How could you wrap a variable or constant to make its access less direct? Consider wrapping constants/variables with intermediate variables, method calls, field accesses, and even nested/anonymous/lambda classes.

* **Vary Statement and Expression Granularity.**
    Think about the complexity of your statements. Can a single, complex expression be broken down into a series of simpler steps using intermediate variables? Conversely, can a sequence of simple operations be fused into a single, more dense statement? Play with the atomicity of the code.

* **Reimagine Control Flow Logic.**
    Look at the program's execution path. Can you reconstruct the same logic using different control flow structures? Explore alternative ways to write loops, conditional branches, and boolean comparisons that result in the exact same execution sequence.

* **Inject Dead Code.**
    Add code that does not affect the program's behavior (e.g., extra variable assignments, unused method calls) to obfuscate the original logic. You can also add duplicate code under unreachable conditions.

* **Leverage the Full Spectrum of Java's Syntax.**
    Java often provides multiple ways to achieve the same result. Utilize the language's rich feature set, including its type system (e.g., primitives vs. wrapper classes), syntactic sugar, alternative annotations/libraries in best practice (e.g., "final"->lombok.Value, "!null"-> "java.util.Object.nonnull"),  and new features from different Java versions (e.g., lambdas vs. anonymous classes, modern switch expressions vs. traditional statements). 

### General Constraints

* **Only Transform Code:** The goal is syntactic diversity, not speed or efficiency, so avoid optimization and never add extra features. You need to find alternative ways to achieve the same function as the code.
* **Follow Java Syntax:** Ensure all transformations result in valid, standard Java code. Add import statements for the extra methods and annotations used.
---

### Your Task

You will be given a Java program with a section of code marked by `// TARGET START` and `// TARGET END`. Your task is to apply your creative, semantic-preserving transformations **only to the code within this targeted section**.

Respond with all the complete, modified Java programs after applying various reasonable transformations.

{seed_program}"""
