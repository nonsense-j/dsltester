"""
[INFO] CodeCheck DSL (ccl) parser Main Class Entrance
"""

from nltk.sem import logic
from src.checker.antlr_ccl import dsl_to_logic_expr, logic_expr_to_dsl
from src.utils.config import SPEC_NEG_AND_STRATEGY


def decompose_checker_dsl(checker_dsl: str) -> list[str]:
    """Decompose a checker's DSL (ccl) by modelling as a logical expr"""
    logic_expr, symbol_map = dsl_to_logic_expr(checker_dsl)
    nnf_expr = to_nnf(logic_expr)
    distributed_expr = distribute(nnf_expr)
    decomposed_expr_list = split_by_or(distributed_expr)
    return [logic_expr_to_dsl(piece, symbol_map) for piece in decomposed_expr_list]


def to_nnf(expr: logic.Expression) -> logic.Expression:
    """Recursively converts a logic expression to Negation Normal Form."""
    if isinstance(expr, logic.NegatedExpression):
        sub_expr = expr.term
        if isinstance(sub_expr, logic.NegatedExpression):
            return to_nnf(sub_expr.term)
        if isinstance(sub_expr, logic.OrExpression):
            return to_nnf(logic.NegatedExpression(sub_expr.first)) & to_nnf(logic.NegatedExpression(sub_expr.second))
        if isinstance(sub_expr, logic.AndExpression):
            # If SPEC_NEG_AND_STRATEGY=False, -(A & B) -> -A | -B
            # If SPEC_NEG_AND_STRATEGY=True, -(A & B) -> (-A & B) | (A & -B)
            if SPEC_NEG_AND_STRATEGY:
                return (to_nnf(logic.NegatedExpression(sub_expr.first)) & sub_expr.second) | (
                    sub_expr.first & to_nnf(logic.NegatedExpression(sub_expr.second))
                )
            else:
                return to_nnf(logic.NegatedExpression(sub_expr.first)) | to_nnf(
                    logic.NegatedExpression(sub_expr.second)
                )
        if isinstance(sub_expr, logic.AllExpression):
            return logic.ExistsExpression(sub_expr.variable, to_nnf(logic.NegatedExpression(sub_expr.term)))
        if isinstance(sub_expr, logic.ExistsExpression):
            return logic.AllExpression(sub_expr.variable, to_nnf(logic.NegatedExpression(sub_expr.term)))
    if isinstance(expr, logic.BinaryExpression):
        return type(expr)(to_nnf(expr.first), to_nnf(expr.second))
    if isinstance(expr, logic.QuantifiedExpression):
        # We don't transform inside the quantifier in NNF, only the negation of it
        return type(expr)(expr.variable, to_nnf(expr.term))
    return expr


# NEW and CRITICAL function to create the DNF-like form
def distribute(expr: logic.Expression) -> logic.Expression:
    """Recursively distributes AND over OR."""
    # recursive case for ExistsExpression
    if isinstance(expr, logic.ExistsExpression):
        return logic.ExistsExpression(expr.variable, distribute(expr.term))

    # Recurse on the children first
    if isinstance(expr, logic.BinaryExpression):
        left = distribute(expr.first)
        right = distribute(expr.second)
        expr = type(expr)(left, right)

    # --- Distribution Logic ---
    # Case 1: A & (B | C) -> (A & B) | (A & C)
    if isinstance(expr, logic.AndExpression):
        if isinstance(expr.second, logic.OrExpression):
            # Distribute expr.first over the parts of expr.second
            new_left = distribute(expr.first & expr.second.first)
            new_right = distribute(expr.first & expr.second.second)
            return new_left | new_right
        # Case 2: (A | B) & C -> (A & C) | (B & C)
        if isinstance(expr.first, logic.OrExpression):
            # Distribute expr.second over the parts of expr.first
            new_left = distribute(expr.first.first & expr.second)
            new_right = distribute(expr.first.second & expr.second)
            return new_left | new_right

    return expr


# This final splitter is simple and now works correctly on the distributed form.
def split_by_or(expr: logic.Expression) -> list[logic.Expression]:
    """Splits an expression by the top-level OR operator."""
    if isinstance(expr, logic.ExistsExpression):
        return [logic.ExistsExpression(expr.variable, term) for term in split_by_or(expr.term)]
    if isinstance(expr, logic.OrExpression):
        return split_by_or(expr.first) + split_by_or(expr.second)
    if isinstance(expr, logic.AndExpression):
        return [
            logic.AndExpression(first, second)
            for first in split_by_or(expr.first)
            for second in split_by_or(expr.second)
        ]
    else:
        return [expr]


if __name__ == "__main__":
    # expression_string = "exists x. (F1(x) & (F2(x) | F3(x)))"
    # # expression_string = "P & (Q & (T1 | T2))"

    # # 1. Parse the string
    # logic_parser = logic.LogicParser()
    # original_expr = logic_parser.parse(expression_string)
    # print(f"Original Expression:\n  {original_expr}\n")

    # # 2. Convert to NNF (doesn't change this specific expression, but is good practice)
    # nnf_expr = to_nnf(original_expr)

    # # 3. STEP 2 (NEW): Distribute AND over OR
    # distributed_expr = distribute(nnf_expr)
    # print(f"After Distribution (DNF-like form):\n  {distributed_expr}\n")
    # # Expected intermediate result: (T() & P()) | (T() & (all x. Q(x)))

    # # 4. STEP 3: Split the distributed expression by 'OR'
    # decomposed_pieces = split_by_or(distributed_expr)

    # # 5. Print the final decomposed list
    # print("Final Decomposed Pieces:")
    # for i, piece in enumerate(decomposed_pieces):
    #     print(f"  Piece {i+1}: {piece}")

    #     checker_dsl = """AND {
    #     ( 'The input request is not null' ),
    #     OR {
    #         ( 'The user is an administrator' ),
    #         AND {
    #             ( 'The user is a member of the "editors" group' ),
    #             NOT { ( 'The user account is locked' ) }
    #         }
    #     }
    # }"""
    #     checker_dsl = """AND {
    #     ( 'The input request is not null' ),
    #     NOT {
    #         AND {
    #             ( 'The user is a member of the "editors" group' ),
    #             NOT { ( 'The user account is locked' ) }
    #         }
    #     }
    # }"""
    checker_dsl = """AND {
  ('The file is a Java source file'),
  ('The class instance expression is a bad closeable initialization'),
  ('The class instance expression type matches the variable type'),
  EXISTS ('ancestor type of the reference type') {
    OR {
      ('The ancestor is java.io.Reader or java.io.InputStream'),
      ('The ancestor is java.util.zip.ZipFile')
    }
  },
  NOT {
    EXISTS ('ancestor type in the derivation') {
      OR {
        ('The ancestor is java.io.CharArrayReader, java.io.StringReader, or java.io.ByteArrayInputStream'),
        ('The ancestor is StringInputStream')
      }
    }
  },
  NOT {
    ('The class instance expression does not need to be closed')
  }
}"""
    decomposed = decompose_checker_dsl(checker_dsl)
    print("Decomposed Checker DSL (CCL):")
    for i, piece in enumerate(decomposed):
        print(f"=> Piece {i+1}: {piece}")
