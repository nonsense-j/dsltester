"""
Preprocess the CodeCheck DSL for decomposition.
"""

import functools
from antlr4 import *
from nltk.sem import logic

from src.resources.ccl.CodeCheckLexer import CodeCheckLexer
from src.resources.ccl.CodeCheckParser import CodeCheckParser
from src.resources.ccl.CodeCheckVisitor import CodeCheckVisitor

# Let NLTK know about our logical operators
logic.Expression.fromstring = logic.LogicParser().parse


class DslConverterVisitor(CodeCheckVisitor):
    """
    This visitor walks the ANTLR parse tree and converts the DSL
    into an NLTK logical expression. It also builds a symbol map.
    """

    def __init__(self):
        # Maps descriptions to generated symbols (e.g., 'desc' -> 'P1' or 'F1')
        self.desc_to_symbol_map = {}
        # The final map to be returned (e.g., 'P1' -> 'desc', 'x' -> 'item')
        self.symbol_to_desc_map = {}
        self.p_counter = 0  # Counter for propositions (P1, P2, ...)
        self.f_counter = 0  # Counter for predicates/functions (F1, F2, ...)
        self.var_counter = 0
        # This holds the variable (e.g., x, y, z) for the current quantifier scope
        self.current_variable = None

    # FIX: Implement the top-level visit method to ignore EOF.
    def visitCheck(self, ctx: CodeCheckParser.CheckContext):
        # The 'check' rule is the entry point and has two children: 'condition' and 'EOF'.
        # We must explicitly visit the 'condition' child and return its result.
        return self.visit(ctx.condition())

    def _get_fresh_symbol(self, desc, prefix):
        # Core logic: Generate a new, unique symbol based on its type (P or F).
        if prefix == "P":
            self.p_counter += 1
            symbol_name = f"P{self.p_counter}"
        else:  # prefix == 'F'
            self.f_counter += 1
            symbol_name = f"F{self.f_counter}"

        self.desc_to_symbol_map[desc] = symbol_name
        self.symbol_to_desc_map[symbol_name] = desc
        return symbol_name

    def _get_fresh_variable(self):
        vars = "xyzuvwabcd"
        var_name = vars[self.var_counter % len(vars)]
        self.var_counter += 1
        return logic.Variable(var_name)

    def visitAtomicCondition(self, ctx: CodeCheckParser.AtomicConditionContext):
        desc = ctx.DESCRIPTION().getText()[1:-1]  # Remove quotes

        # Core logic: If we are inside a quantifier, treat this as a predicate (e.g., F(x)).
        # Otherwise, treat it as a simple proposition (e.g., P).
        if self.current_variable:
            if desc not in self.desc_to_symbol_map:
                symbol_name = self._get_fresh_symbol(desc, "F")
            else:
                symbol_name = self.desc_to_symbol_map[desc]
            predicate = logic.ConstantExpression(logic.Variable(symbol_name))
            return logic.ApplicationExpression(predicate, logic.VariableExpression(self.current_variable))
        else:
            if desc not in self.desc_to_symbol_map:
                symbol_name = self._get_fresh_symbol(desc, "P")
            else:
                symbol_name = self.desc_to_symbol_map[desc]
            return logic.ConstantExpression(logic.Variable(symbol_name))

    def visitAndExpr(self, ctx: CodeCheckParser.AndExprContext):
        children_expr = [self.visit(c) for c in ctx.conditionList().condition()]
        return functools.reduce(lambda a, b: a & b, children_expr)

    def visitOrExpr(self, ctx: CodeCheckParser.OrExprContext):
        children_expr = [self.visit(c) for c in ctx.conditionList().condition()]
        return functools.reduce(lambda a, b: a | b, children_expr)

    def visitNotExpr(self, ctx: CodeCheckParser.NotExprContext):
        return -self.visit(ctx.condition())

    def _visit_quantifier(self, ctx, QuantifierClass):
        # Core logic: EXISTS ('desc') { cond } becomes exists x.(cond(x)).
        # The description of the quantifier's subject is mapped to the variable.
        old_var = self.current_variable
        v = self._get_fresh_variable()
        self.current_variable = v

        # Map the variable ('x') to its description ('desc')
        domain_desc = ctx.DESCRIPTION().getText()[1:-1]
        self.symbol_to_desc_map[str(v)] = domain_desc

        inner_expr = self.visit(ctx.condition())

        self.current_variable = old_var  # Restore context for outer scopes
        return QuantifierClass(v, inner_expr)

    def visitExistsExpr(self, ctx: CodeCheckParser.ExistsExprContext):
        return self._visit_quantifier(ctx, logic.ExistsExpression)

    def visitForallExpr(self, ctx: CodeCheckParser.ForallExprContext):
        return self._visit_quantifier(ctx, logic.AllExpression)

    def visitCondition(self, ctx: CodeCheckParser.ConditionContext):
        if ctx.getChildCount() == 3 and ctx.LPAREN():
            return self.visit(ctx.condition(0))
        return self.visitChildren(ctx)


def dsl_to_logic_expr(dsl_string: str):
    """
    Converts a DSL string into an NLTK logical expression and a symbol map.
    """
    lexer = CodeCheckLexer(InputStream(dsl_string))
    stream = CommonTokenStream(lexer)
    parser = CodeCheckParser(stream)
    tree = parser.check()

    # check syntax errors
    if parser.getNumberOfSyntaxErrors() > 0:
        raise ValueError("DSL syntax errors found")

    visitor = DslConverterVisitor()
    logic_expr = visitor.visit(tree)

    return logic_expr, visitor.symbol_to_desc_map


def _flatten_binary_logic(expr, operator_class):
    """Helper to walk a binary expression tree (like ANDs or ORs) and flatten it into a list."""
    if isinstance(expr, operator_class):
        return _flatten_binary_logic(expr.first, operator_class) + _flatten_binary_logic(expr.second, operator_class)
    else:
        return [expr]


def _logic_expr_to_dsl_recursive(expr, symbol_map, indent=0):
    """Recursive helper for converting NLTK expression back to DSL."""
    idt = "  " * indent
    idt_child = "  " * (indent + 1)

    if isinstance(expr, logic.AndExpression):
        conditions = _flatten_binary_logic(expr, logic.AndExpression)
        dsl_conditions = ",\n".join(
            [f"{idt_child}{_logic_expr_to_dsl_recursive(c, symbol_map, indent + 1)}" for c in conditions]
        )
        return f"AND {{\n{dsl_conditions}\n{idt}}}"

    elif isinstance(expr, logic.OrExpression):
        conditions = _flatten_binary_logic(expr, logic.OrExpression)
        dsl_conditions = ",\n".join(
            [f"{idt_child}{_logic_expr_to_dsl_recursive(c, symbol_map, indent + 1)}" for c in conditions]
        )
        return f"OR {{\n{dsl_conditions}\n{idt}}}"

    elif isinstance(expr, logic.NegatedExpression):
        if isinstance(expr.term, logic.ApplicationExpression) or isinstance(expr.term, logic.ConstantExpression):
            return f"NOT {{ {_logic_expr_to_dsl_recursive(expr.term, symbol_map, indent)} }}"
        else:
            inner_dsl_indented = _logic_expr_to_dsl_recursive(expr.term, symbol_map, indent + 1)
            return f"NOT {{\n{idt_child}{inner_dsl_indented}\n{idt}}}"

    elif isinstance(expr, logic.AllExpression) or isinstance(expr, logic.ExistsExpression):
        # Core logic: Reconstruct the quantifier based on the new simplified structure.
        quantifier_str = "FORALL" if isinstance(expr, logic.AllExpression) else "EXISTS"
        variable_name = str(expr.variable)
        desc = symbol_map.get(variable_name, "???")
        inner_dsl = _logic_expr_to_dsl_recursive(expr.term, symbol_map, indent + 1)
        return f"{quantifier_str} ('{desc}') {{\n{idt_child}{inner_dsl}\n{idt}}}"

    elif isinstance(expr, logic.ApplicationExpression):
        symbol = str(expr.function.variable)
        desc = symbol_map.get(symbol, "???")
        return f"('{desc}')"

    elif isinstance(expr, logic.ConstantExpression):
        symbol = str(expr.variable)
        desc = symbol_map.get(symbol, "???")
        return f"('{desc}')"
    else:
        return str(expr)


def logic_expr_to_dsl(logic_expr: logic.Expression, symbol_map: dict) -> str:
    """
    Converts an NLTK logical expression and its symbol map back into a DSL string.
    """
    return _logic_expr_to_dsl_recursive(logic_expr, symbol_map)


DSL_SAMPLES = [
    """
AND {
    ( 'The input request is not null' ),
    OR {
        ( 'The user is an administrator' ),
        AND {
            ( 'The user is a member of the "editors" group' ),
            NOT { ( 'The user account is locked' ) }
        }
    }
}
""",
    """
FORALL ('class in the project') {
    EXISTS ('"Inject" annotation') {
        ( 'The annotated field is private' )
    }
}
""",
    """
AND {
    FORALL ('public API method') {
        ( 'The method has a "ResponseBody" annotation' )
    },
    FORALL ('database entity') {
        ( 'The entity has a primary key defined' )
    }
}
""",
    """
NOT {
    OR {
        ( 'The file is empty' ),
        NOT {
            ( 'The file has a ".txt" extension' )
        }
    }
}
""",
    """
AND {
    ( 'The application context is successfully loaded' ),
    FORALL ('controller bean') {
        OR {
            ( 'The bean name is "healthCheckController"' ),
            EXISTS ('method with "RequestMapping" annotation') {
                AND {
                    ( 'The method is public' ),
                    NOT { ( 'The method is deprecated' ) }
                }
            }
        }
    },
    NOT { ( 'The database connection pool is exhausted' ) }
}
""",
]

# --- Example Usage ---
if __name__ == "__main__":
    for i, dsl_code_sample in enumerate(DSL_SAMPLES):
        print(f"### Sample {i + 1} ###")
        print("--- 1. Converting DSL to Logic Expression ---")
        expression, sym_map = dsl_to_logic_expr(dsl_code_sample)

        print("=> Original DSL:")
        print(dsl_code_sample.strip())

        print("=> Generated NLTK Expression:")
        print(expression)

        print("=> Generated Symbol Map:")
        import json

        print(json.dumps(sym_map, indent=2))

        print("--- 2. Converting Logic Expression back to DSL ---")
        reconstructed_dsl = logic_expr_to_dsl(expression, sym_map)
        print("=> Reconstructed DSL:")
        print(reconstructed_dsl)
        print("\n")
