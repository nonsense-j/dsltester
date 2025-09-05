# Generated from CodeCheck.g4 by ANTLR 4.13.2
from antlr4 import *
if "." in __name__:
    from .CodeCheckParser import CodeCheckParser
else:
    from CodeCheckParser import CodeCheckParser

# This class defines a complete generic visitor for a parse tree produced by CodeCheckParser.

class CodeCheckVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by CodeCheckParser#check.
    def visitCheck(self, ctx:CodeCheckParser.CheckContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CodeCheckParser#condition.
    def visitCondition(self, ctx:CodeCheckParser.ConditionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CodeCheckParser#logicalExpr.
    def visitLogicalExpr(self, ctx:CodeCheckParser.LogicalExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CodeCheckParser#andExpr.
    def visitAndExpr(self, ctx:CodeCheckParser.AndExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CodeCheckParser#orExpr.
    def visitOrExpr(self, ctx:CodeCheckParser.OrExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CodeCheckParser#notExpr.
    def visitNotExpr(self, ctx:CodeCheckParser.NotExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CodeCheckParser#existsExpr.
    def visitExistsExpr(self, ctx:CodeCheckParser.ExistsExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CodeCheckParser#forallExpr.
    def visitForallExpr(self, ctx:CodeCheckParser.ForallExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CodeCheckParser#conditionList.
    def visitConditionList(self, ctx:CodeCheckParser.ConditionListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CodeCheckParser#atomicCondition.
    def visitAtomicCondition(self, ctx:CodeCheckParser.AtomicConditionContext):
        return self.visitChildren(ctx)



del CodeCheckParser