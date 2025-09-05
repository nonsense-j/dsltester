# Generated from CodeCheck.g4 by ANTLR 4.13.2
from antlr4 import *
if "." in __name__:
    from .CodeCheckParser import CodeCheckParser
else:
    from CodeCheckParser import CodeCheckParser

# This class defines a complete listener for a parse tree produced by CodeCheckParser.
class CodeCheckListener(ParseTreeListener):

    # Enter a parse tree produced by CodeCheckParser#check.
    def enterCheck(self, ctx:CodeCheckParser.CheckContext):
        pass

    # Exit a parse tree produced by CodeCheckParser#check.
    def exitCheck(self, ctx:CodeCheckParser.CheckContext):
        pass


    # Enter a parse tree produced by CodeCheckParser#condition.
    def enterCondition(self, ctx:CodeCheckParser.ConditionContext):
        pass

    # Exit a parse tree produced by CodeCheckParser#condition.
    def exitCondition(self, ctx:CodeCheckParser.ConditionContext):
        pass


    # Enter a parse tree produced by CodeCheckParser#logicalExpr.
    def enterLogicalExpr(self, ctx:CodeCheckParser.LogicalExprContext):
        pass

    # Exit a parse tree produced by CodeCheckParser#logicalExpr.
    def exitLogicalExpr(self, ctx:CodeCheckParser.LogicalExprContext):
        pass


    # Enter a parse tree produced by CodeCheckParser#andExpr.
    def enterAndExpr(self, ctx:CodeCheckParser.AndExprContext):
        pass

    # Exit a parse tree produced by CodeCheckParser#andExpr.
    def exitAndExpr(self, ctx:CodeCheckParser.AndExprContext):
        pass


    # Enter a parse tree produced by CodeCheckParser#orExpr.
    def enterOrExpr(self, ctx:CodeCheckParser.OrExprContext):
        pass

    # Exit a parse tree produced by CodeCheckParser#orExpr.
    def exitOrExpr(self, ctx:CodeCheckParser.OrExprContext):
        pass


    # Enter a parse tree produced by CodeCheckParser#notExpr.
    def enterNotExpr(self, ctx:CodeCheckParser.NotExprContext):
        pass

    # Exit a parse tree produced by CodeCheckParser#notExpr.
    def exitNotExpr(self, ctx:CodeCheckParser.NotExprContext):
        pass


    # Enter a parse tree produced by CodeCheckParser#existsExpr.
    def enterExistsExpr(self, ctx:CodeCheckParser.ExistsExprContext):
        pass

    # Exit a parse tree produced by CodeCheckParser#existsExpr.
    def exitExistsExpr(self, ctx:CodeCheckParser.ExistsExprContext):
        pass


    # Enter a parse tree produced by CodeCheckParser#forallExpr.
    def enterForallExpr(self, ctx:CodeCheckParser.ForallExprContext):
        pass

    # Exit a parse tree produced by CodeCheckParser#forallExpr.
    def exitForallExpr(self, ctx:CodeCheckParser.ForallExprContext):
        pass


    # Enter a parse tree produced by CodeCheckParser#conditionList.
    def enterConditionList(self, ctx:CodeCheckParser.ConditionListContext):
        pass

    # Exit a parse tree produced by CodeCheckParser#conditionList.
    def exitConditionList(self, ctx:CodeCheckParser.ConditionListContext):
        pass


    # Enter a parse tree produced by CodeCheckParser#atomicCondition.
    def enterAtomicCondition(self, ctx:CodeCheckParser.AtomicConditionContext):
        pass

    # Exit a parse tree produced by CodeCheckParser#atomicCondition.
    def exitAtomicCondition(self, ctx:CodeCheckParser.AtomicConditionContext):
        pass



del CodeCheckParser