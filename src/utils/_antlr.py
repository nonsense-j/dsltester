"""
Preprocess the Kirin DSL for decomposition.
"""

import hashlib, re
from antlr4 import *

from src.kirin.HornLexer import HornLexer
from src.kirin.DslParser import DslParser
from src.kirin.DslParserVisitor import DslParserVisitor
from src.utils._logger import logger
from src.utils._helper import is_third_class


class KirinThirdPkgAnalyzer(DslParserVisitor):
    """
    ==> Start from statements [for analyze_third_pkg]
    [Deprecated] Analyze the DSL code to fetch all the third-party resources.
    This module can only get third class names without methods and field, thus it is not used in the current version.
    [WARN] Cannot construct class that using endsWith, startWith, regex for match.
    """

    def __init__(self):
        super().__init__()
        self.third_pkg_list = set()

    def visitStrConditionEndInStr(self, ctx: DslParser.StrConditionEndInStrContext):
        left_text: str = ctx.getTypedRuleContext(DslParser.LeftStrOperandEndInStrContext, 0).getText()
        # only class name
        if any([left_text.endswith(tail) for tail in ["type.name", "enclosingClass.name"]]):
            right_ctx = ctx.getTypedRuleContext(DslParser.RightStrOperandEndInStrContext, 0)
            # only str constant
            if right_ctx.getTypedRuleContext(DslParser.StrConstantContext, 0) is not None:
                right_text = right_ctx.getText()[1:-1]
                if is_third_class(right_text):
                    self.third_pkg_list.add(right_text)
        return self.visitChildren(ctx)


class KirinBaseVisitor(DslParserVisitor):
    """
    Base visitor for the Kirin DSL parser.
    """

    def __init__(self, input_dsl_text: str):
        self.full_text = input_dsl_text
        super().__init__()

    def getOriText(self, ctx):
        return self.full_text[ctx.start.start : ctx.stop.stop + 1]


class KirinHashVisitor(KirinBaseVisitor):
    """
    ==> Start from statements
    DSL hash generation based on the Kirin DSL, used for deduplication.
    [input]: a dsl text
    [output]: a hash value
    """

    def __init__(self, input_dsl_text: str):
        super().__init__(input_dsl_text)

    def remove_ctx(self, ctx):
        alias = self.getOriText(ctx)
        replace_empty = " " * len(alias)
        self.full_text = self.full_text[: ctx.start.start] + replace_empty + self.full_text[ctx.stop.stop + 1 :]

    def visitStatements(self, ctx: DslParser.StatementsContext):
        self.visitChildren(ctx)
        hash_str = re.sub(r"\s+", "", self.full_text)
        hash_obj = hashlib.md5(hash_str.encode())
        hash_value = hash_obj.hexdigest()
        return hash_str, hash_value

    def visitComment(self, ctx: DslParser.CommentContext):
        self.remove_ctx(ctx)
        return 0

    def visitAlias(self, ctx: DslParser.AliasContext):
        self.remove_ctx(ctx)
        return 0

    def visitRuleSetMessage(self, ctx: DslParser.RuleSetMessageContext):
        self.remove_ctx(ctx)
        return 0

    def visitRuleMsg(self, ctx: DslParser.RuleMsgContext):
        self.remove_ctx(ctx)
        return 0


class KirinEntryVisitor(KirinBaseVisitor):
    """
    ==> Start from statements [for preprocess_dsl]
    DSL split into sub_dsls if statements has more than one nodeStmt
    clear_labels: if True, remove the labels (RuleSetMsg, RuleMsg) from the dsl text
    [input]: a dsl text
    [output]: a list of splitted dsl texts, e.g., source, sink...
    """

    def __init__(self, input_dsl_text: str, clear_labels: bool = True):
        super().__init__(input_dsl_text)
        self.clear_labels = clear_labels

    def visitStatements(self, ctx: DslParser.StatementsContext):
        node_stsmt_list = ctx.getTypedRuleContexts(DslParser.NodeStmtContext)
        node_dsl_text = []
        for node_stmt in node_stsmt_list:
            if self.clear_labels:
                # remove the labels
                query_stmt = node_stmt.getTypedRuleContext(DslParser.QueryStmtContext, 0)
                node_dsl = self.getOriText(query_stmt)
            else:
                node_dsl = self.getOriText(node_stmt)
            node_dsl_text.append(node_dsl)
        return node_dsl_text


class KirinOrVisitor(KirinBaseVisitor):
    """
    ==> Start from nodeStmt [for preprocess_dsl]
    DSL decomposition based on the "OR" CondExpr only (for a single nodeStmt).
    [input]: a dsl text
    [output]: a list of decomposed dsl texts
    """

    def __init__(self, input_dsl_text: str):
        super().__init__(input_dsl_text)
        self.scope_start = -1
        self.scope_stop = -1
        self.sub_dsl_list = []

    def visitNodeStmt(self, ctx: DslParser.NodeStmtContext):
        self.scope_start = ctx.start.start
        self.scope_stop = ctx.stop.stop
        result = self.visitChildren(ctx)
        # for dsl that has no "OR", return the original dsl
        if len(self.sub_dsl_list) == 0:
            self.sub_dsl_list.append(self.getOriText(ctx))
        return result

    def visitCondExpr(self, ctx: DslParser.CondExprContext):
        if ctx.OR():
            logger.info(f"Found OR condition on line {ctx.OR().symbol.line}, column {ctx.OR().symbol.column}")
            text_before = self.full_text[self.scope_start : ctx.start.start]
            text_after = self.full_text[ctx.stop.stop + 1 : self.scope_stop + 1]

            cur_dsl_list = []
            for sub_cond_expr in ctx.condExpr():
                sub_cond_text = self.getOriText(sub_cond_expr)
                self.scope_start = sub_cond_expr.start.start
                self.scope_stop = sub_cond_expr.stop.stop
                self.sub_dsl_list.clear()

                self.visit(sub_cond_expr)
                # After visiting sub_cond_expr, its sub_dsl_list has been populated
                # Thus, we add text_before + sub_dsl + text_after to cur_dsl_list
                if len(self.sub_dsl_list) == 0:
                    cur_dsl_list.append(text_before + sub_cond_text + text_after)
                else:
                    for sub_cond_dsl in self.sub_dsl_list:
                        cur_dsl_list.append(text_before + sub_cond_dsl + text_after)
            self.sub_dsl_list = cur_dsl_list
            return 0
        elif ctx.AND():
            # TODO)) Optimization for Combinatorial Test
            logger.info(f"Found AND condition on line {ctx.AND().symbol.line}, column {ctx.AND().symbol.column}")
            text_before = self.full_text[self.scope_start : ctx.start.start]
            text_after = self.full_text[ctx.stop.stop + 1 : self.scope_stop + 1]
            cur_dsl_list = []
            for sub_cond_expr in ctx.condExpr():
                sub_cond_text = self.getOriText(sub_cond_expr)
                self.scope_start = sub_cond_expr.start.start
                self.scope_stop = sub_cond_expr.stop.stop
                self.sub_dsl_list.clear()

                self.visit(sub_cond_expr)
                # After visiting sub_cond_expr, its sub_dsl_list has been populated
                if len(self.sub_dsl_list) == 0:
                    self.sub_dsl_list = [sub_cond_text]

                # for the first conditon
                if len(cur_dsl_list) == 0:
                    cur_dsl_list.extend(self.sub_dsl_list)
                else:
                    tmp_dsl_list = []
                    for cur_dsl in cur_dsl_list:
                        for add_dsl in self.sub_dsl_list:
                            tmp_dsl_list.append(f"{cur_dsl},\n{add_dsl}")
                    cur_dsl_list = tmp_dsl_list
            # add text_before and text_after to each dsl
            self.sub_dsl_list.clear()
            for cur_dsl in cur_dsl_list:
                self.sub_dsl_list.append(text_before + "and(\n" + cur_dsl + "\n)" + text_after)
            return 0

        return self.visitChildren(ctx)

    def visitDirectCondition(self, ctx: DslParser.DirectConditionContext):
        """
        do not decompose the OR conditions in "notContain" and "notIn" blocks
        """
        spec_direct_cond = ctx.getChild(0)
        if isinstance(spec_direct_cond, DslParser.HasConditionContext):
            has_ctx = spec_direct_cond.getTypedRuleContext(DslParser.HasOperatorContext, 0)
            has_text = self.getOriText(has_ctx)
            if has_text == "notContain" or has_text == "notIn":
                # skip
                return 0
        return self.visitChildren(ctx)


class KirinNotVisitor(KirinBaseVisitor):
    """
    ==> Start from nodeStmt [for preprocess_dsl]
    DSL transformation based on the "NOT", where "not" is propagated to all the deepest inner meta-conditions.
    [input]: a dsl text
    [output]: a transformed dsl text

    -> common strategy for na: not (and (A, B)) -> or (not A, not B)
    -> specific strategy for na: not (and (A, B)) -> or (and (not A, B), and (A, not B))

    -> common strategy for not has (keep): notContain x where xx split -> notContain x where xx split
    -> do split not has: notContain x where xx split ==> or (notContain xx, notContain x where xx)
    """

    def __init__(
        self,
        input_dsl_text: str,
        init_transform: bool = False,
        spec_na_strategy: bool = False,
        split_not_has: bool = False,
    ):
        super().__init__(input_dsl_text)
        self.do_transform = init_transform
        # spec_na_strategy: if True, use the specific strategy for "not(and)" transformation
        self.spec_na_strategy = spec_na_strategy
        # split_not_has: if True, notContain x where xx split ==> or (notContain xx, notContain x where xx)
        self.split_not_has = split_not_has

    def visitNodeStmt(self, ctx: DslParser.NodeStmtContext):
        # Since we return the transformed text, we need to control the full incoking chain strarting from NodeStmt
        query_stmt_ctx = ctx.getTypedRuleContext(DslParser.QueryStmtContext, 0)
        node_query_expr_ctx = query_stmt_ctx.getTypedRuleContext(DslParser.NodeQueryExprContext, 0)

        cond_expr_ctx = node_query_expr_ctx.getTypedRuleContext(DslParser.CondExprContext, 0)
        if cond_expr_ctx is not None:
            # visit the condExpr
            text_before = self.full_text[: cond_expr_ctx.start.start]
            text_after = self.full_text[cond_expr_ctx.stop.stop + 1 :]
            return text_before + self.visitCondExpr(cond_expr_ctx) + text_after
        else:
            # no condExpr, just return the original dsl
            return self.getOriText(ctx)

    def visitCondExpr(self, ctx: DslParser.CondExprContext):
        # CondExpr is (OR, AND, NOT)
        if ctx.getChildCount() > 1:
            cond_op = ctx.getChild(0)
            cond_op_type = cond_op.symbol.type
            # Handle -- Not CondExpr
            if cond_op_type == DslParser.NOT:
                logger.info(f"Found NOT condition on line {cond_op.symbol.line}, column {cond_op.symbol.column}")
                sub_cond_expr = ctx.condExpr(0)
                self.do_transform = not self.do_transform
                res = self.visitCondExpr(sub_cond_expr)
                # do_transform should be reverted to the original state
                self.do_transform = not self.do_transform
                return res
            # Handle -- Or CondExpr
            elif cond_op_type == DslParser.OR:
                cond_op_text = "and" if self.do_transform else "or"
                # construct the sub_dsl based on every sub_cond_expr
                aggregate_text = self.full_text[ctx.start.start : cond_op.symbol.start] + cond_op_text
                cursor_pos = cond_op.symbol.stop + 1
                for sub_cond_expr in ctx.condExpr():
                    aggregate_text += self.full_text[cursor_pos : sub_cond_expr.start.start]
                    aggregate_text += self.visitCondExpr(sub_cond_expr)
                    cursor_pos = sub_cond_expr.stop.stop + 1
                aggregate_text += self.full_text[cursor_pos : ctx.stop.stop + 1]
                return aggregate_text
            # Handle -- And CondExpr
            elif cond_op_type == DslParser.AND:
                cond_op_text = "or" if self.do_transform else "and"
                # construct the sub_dsl based on every sub_cond_expr
                aggregate_text = self.full_text[ctx.start.start : cond_op.symbol.start] + cond_op_text
                cursor_pos = cond_op.symbol.stop + 1

                # common strategy for na: not (and (A, B)) -> or (not A, not B)
                if not self.spec_na_strategy:
                    cursor_pos = cond_op.symbol.stop + 1
                    for sub_cond_expr in ctx.condExpr():
                        aggregate_text += self.full_text[cursor_pos : sub_cond_expr.start.start]
                        aggregate_text += self.visitCondExpr(sub_cond_expr)
                        cursor_pos = sub_cond_expr.stop.stop + 1
                # specific strategy for na: not (and (A, B)) -> or (and (not A, B), and (A, not B))
                else:
                    # store the transformed dsl for every single cond_expr
                    cond_list = []
                    for sub_cond_expr in ctx.condExpr():
                        tmp_dt = self.do_transform
                        self.do_transform = False
                        cond_list.append(self.visitCondExpr(sub_cond_expr))
                        self.do_transform = tmp_dt
                    # construct the sub_dsl based on every sub_cond_expr
                    for c_i, sub_cond_expr in enumerate(ctx.condExpr()):
                        # c_i is the not sub_cond_expr index
                        aggregate_text += self.full_text[cursor_pos : sub_cond_expr.start.start]
                        if self.do_transform:
                            aggregate_text += "and(\n"
                            for cond_str in cond_list[:c_i]:
                                aggregate_text += cond_str + ",\n"
                            aggregate_text += self.visitCondExpr(sub_cond_expr)
                            for cond_str in cond_list[c_i + 1 :]:
                                aggregate_text += ",\n" + cond_str
                            aggregate_text += "\n)"
                        else:
                            aggregate_text += cond_list[c_i]
                        cursor_pos = sub_cond_expr.stop.stop + 1

                aggregate_text += self.full_text[cursor_pos : ctx.stop.stop + 1]
                return aggregate_text
            else:
                # As defined in DslParser.g4, the cond_op should be either OR, AND or NOT if childCount > 1
                raise ValueError(
                    f"--> Unsupported Condition type {cond_op.symbol.type} on line {cond_op.symbol.line}, column {cond_op.symbol.column}"
                )
        # child_count == 1, it is a condition, whose child is a directCondition or encapsulatedCondExpr
        # encapsulatedCondExpr is not used in the current version of Kirin DSL
        elif isinstance(ctx.getChild(0), DslParser.ConditionContext):
            # Handle Condition
            cond_ctx = ctx.getChild(0)
            spec_cond_ctx = cond_ctx.getChild(0)
            if isinstance(spec_cond_ctx, DslParser.DirectConditionContext):
                # Handle DirectCondition
                return self.visitDirectCondition(spec_cond_ctx)
            else:
                # TODO)) Handle EncapsulatedCondition
                cond_text = self.getOriText(cond_ctx)
                return f"not( {cond_text} )" if self.do_transform else cond_text
        else:
            # Not defined in the DSL grammar
            raise ValueError(
                f"--> Unsupported Condition {ctx.getText()} on line {ctx.start.line}, column {ctx.start.column}"
            )

    def visitDirectCondition(self, ctx: DslParser.DirectConditionContext):
        """
        Notably, three condition with SATISFY (if where) should be handled.
            hasCondition.containedDesc: [may have] SATISFY; isCondition: [may have] SATISFY;
            nodeCondition and nodeCollectionCondition: [must have] SATISFY;
        containning SATISFY means containning sub_cond_expr
        e.g., input -> fc.enclosingFunction contain functionCall fc1 where (and (cond1, cond2))
            transformed -> fc.enclosingFunction notContain functionCall fc1 where (and (not cond1, cond2))
            do_has_split -> or(
                fc.enclosingFunction notContain functionCall fc1,
                fc.enclosingFunction notContain functionCall fc1 where (and (not cond1, not cond2))
            )
        """
        spec_dirct_cond = ctx.getChild(0)

        if isinstance(spec_dirct_cond, DslParser.HasConditionContext):
            has_ctx = spec_dirct_cond.getTypedRuleContext(DslParser.HasOperatorContext, 0)
            has_text = self.getOriText(has_ctx)
            if self.do_transform:
                if "contain" in has_text.lower():
                    has_text = "notContain" if has_text == "contain" else "contain"
                else:
                    has_text = "notIn" if has_text == "in" else "in"
            contained_desc = spec_dirct_cond.getTypedRuleContext(DslParser.ContainedDescContext, 0)
            contained_cond_expr = contained_desc.getTypedRuleContext(DslParser.CondExprContext, 0)

            if contained_cond_expr is not None:
                text_before = self.full_text[spec_dirct_cond.start.start : has_ctx.start.start] + has_text
                text_before += self.full_text[has_ctx.stop.stop + 1 : contained_cond_expr.start.start]
                text_after = self.full_text[contained_cond_expr.stop.stop + 1 : spec_dirct_cond.stop.stop + 1]

                # don't propaganda do_transform to inner condition, only transform the hasOperator
                tmp_dt = self.do_transform
                self.do_transform = False
                if self.split_not_has:
                    # First condition: notContain
                    root_node_attr = contained_desc.getTypedRuleContext(DslParser.RootNodeAttrContext, 0)
                    only_contain_text = self.full_text[spec_dirct_cond.start.start : has_ctx.start.start] + has_text
                    only_contain_text += self.full_text[has_ctx.stop.stop + 1 : root_node_attr.stop.stop + 1]
                    aggregate_text = f"{only_contain_text},\n"
                    # Second condition: original condition, inner condExpr should be visited
                    aggregate_text += text_before + self.visitCondExpr(contained_cond_expr)
                    result = f"or(\n{aggregate_text}\n){text_after}"
                else:
                    result = text_before + self.visitCondExpr(contained_cond_expr) + text_after
                self.do_transform = tmp_dt
                return result
            else:
                # no condExpr, just replace the has symbol
                text_res = self.full_text[spec_dirct_cond.start.start : has_ctx.start.start] + has_text
                text_res += self.full_text[has_ctx.stop.stop + 1 : spec_dirct_cond.stop.stop + 1]
                return text_res

        elif isinstance(spec_dirct_cond, DslParser.IsConditionContext):
            is_ctx = spec_dirct_cond.getTypedRuleContext(DslParser.IsOperatorContext, 0)
            is_text = self.getOriText(is_ctx)
            # isOperator can only be "is" or "isnot"
            if self.do_transform:
                is_text = "isnot" if is_text == "is" else "is"

            contained_cond_expr = spec_dirct_cond.getTypedRuleContext(DslParser.CondExprContext, 0)
            if contained_cond_expr is not None:
                text_before = self.full_text[spec_dirct_cond.start.start : contained_cond_expr.start.start]
                text_after = self.full_text[contained_cond_expr.stop.stop + 1 : spec_dirct_cond.stop.stop + 1]
                if self.do_transform:
                    # the [satisfy_op: is] condition should be added as the first new condition
                    # First condition: satisfy_op
                    satisy_sym = spec_dirct_cond.Satisfy().symbol
                    only_satisfy_op_text = self.full_text[spec_dirct_cond.start.start : is_ctx.start.start] + is_text
                    only_satisfy_op_text += self.full_text[is_ctx.stop.stop + 1 : satisy_sym.start]
                    aggregate_text = f"{only_satisfy_op_text}, \n"
                    # Second condition: original condition, inner condExpr should be visited using [visit]
                    aggregate_text += text_before + self.visitCondExpr(contained_cond_expr)
                    return f"or(\n{aggregate_text}\n){text_after}"
                else:
                    return text_before + self.visitCondExpr(contained_cond_expr) + text_after
            else:
                # no condExpr, just replace the is symbol
                text_res = self.full_text[spec_dirct_cond.start.start : is_ctx.start.start] + is_text
                text_res += self.full_text[is_ctx.stop.stop + 1 : spec_dirct_cond.stop.stop + 1]
                return text_res

        elif isinstance(spec_dirct_cond, (DslParser.NodeConditionContext, DslParser.NodeCollectionConditionContext)):
            # TODO)) Handle NodeCondition and NodeCollectionCondition, currrently fall back to the default treatment
            pass

        # desult transformation
        cond_text = self.getOriText(ctx)
        return f"not( {cond_text} )" if self.do_transform else cond_text
