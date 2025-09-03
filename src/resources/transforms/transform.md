### Literal-level
- literal_add_var_wrapper: Wrap a literal value (e.g., a string, boolean or number) in a new variable with "final" to obscure its direct usage.
- literal_add_method_wrapper: Wrap a literal value (e.g., a string, boolean or number) in a new method call to obscure its direct usage.
- literal_add_field_wrapper: Wrap a literal value (e.g., a string, boolean or number) in a new field to obscure its direct usage.
- literal_create_complex_expression: Construct a complex operation that evaluates to the literal value, e.g. "3->1+2", "false->false||false", etc.
- literal_use_standard_library: Replace a literal value with a call to a standard library (factory method like "X.valueOf") function that produces the same value.


### Variable-level
- var_add_intermediate_var_wrapper: Introduce a new variable to hold a value, making the original usage less direct.
- var_add_method_wrapper: Wrap a variable in a new method call to obscure its direct usage.
- var_add_field_wrapper: Wrap a variable in a new field to obscure its direct usage.


### Expression-level
- create_complex_expression: 


Introduce layers of indirection between where data is defined and where it is used. \
How could you wrap a variable or constant to make its access less direct? Consider wrapping constants/variables with intermediate \
variables, method calls, field accesses, and even nested/anonymous/lambda classes.
- **Statement-level: Vary Statement and Expression Granularity:** Think about the complexity of your statements. Can a single, complex expression be broken down into \
a series of simpler steps using intermediate variables? Conversely, can a sequence of simple operations be fused into a single, more dense statement? \
Play with the atomicity of the code.
- **Structure-level: Reimagine Control Flow Logic:** Look at the program's execution path. Can you reconstruct the same logic using different control flow structures? \
Explore alternative ways to write loops, conditional branches, and boolean comparisons that result in the exact same execution sequence.
- **Feature-level: Leverage the Full Spectrum of Java's Syntax:** Java often provides multiple ways to achieve the same result. Utilize the language's rich feature set, \
including its type system (e.g., primitives vs. wrapper classes), syntactic sugar, alternative annotations/libraries in best practice \
(e.g., "final"->lombok.Value, "!null"-> "java.util.Object.nonnull"),  and new features from different Java versions (e.g., lambdas vs. anonymous classes, \
modern switch expressions vs. traditional statements). 
- **Inject Dead Code:** Add code that does not affect the program's behavior (e.g., extra variable assignments, unused method calls) to obfuscate the \
original logic. You can also add duplicate code under unreachable conditions.