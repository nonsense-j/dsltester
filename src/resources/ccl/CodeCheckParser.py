# Generated from CodeCheck.g4 by ANTLR 4.13.2
# encoding: utf-8
from antlr4 import *
from io import StringIO
import sys
if sys.version_info[1] > 5:
	from typing import TextIO
else:
	from typing.io import TextIO

def serializedATN():
    return [
        4,1,12,82,2,0,7,0,2,1,7,1,2,2,7,2,2,3,7,3,2,4,7,4,2,5,7,5,2,6,7,
        6,2,7,7,7,2,8,7,8,2,9,7,9,1,0,1,0,1,0,1,1,1,1,1,1,1,1,1,1,1,1,3,
        1,30,8,1,1,2,1,2,1,2,1,2,1,2,3,2,37,8,2,1,3,1,3,1,3,1,3,1,3,1,4,
        1,4,1,4,1,4,1,4,1,5,1,5,1,5,1,5,1,5,1,6,1,6,1,6,1,6,1,6,1,6,1,6,
        1,6,1,7,1,7,1,7,1,7,1,7,1,7,1,7,1,7,1,8,1,8,1,8,5,8,73,8,8,10,8,
        12,8,76,9,8,1,9,1,9,1,9,1,9,1,9,0,0,10,0,2,4,6,8,10,12,14,16,18,
        0,0,78,0,20,1,0,0,0,2,29,1,0,0,0,4,36,1,0,0,0,6,38,1,0,0,0,8,43,
        1,0,0,0,10,48,1,0,0,0,12,53,1,0,0,0,14,61,1,0,0,0,16,69,1,0,0,0,
        18,77,1,0,0,0,20,21,3,2,1,0,21,22,5,0,0,1,22,1,1,0,0,0,23,30,3,4,
        2,0,24,30,3,18,9,0,25,26,5,6,0,0,26,27,3,2,1,0,27,28,5,7,0,0,28,
        30,1,0,0,0,29,23,1,0,0,0,29,24,1,0,0,0,29,25,1,0,0,0,30,3,1,0,0,
        0,31,37,3,6,3,0,32,37,3,8,4,0,33,37,3,10,5,0,34,37,3,12,6,0,35,37,
        3,14,7,0,36,31,1,0,0,0,36,32,1,0,0,0,36,33,1,0,0,0,36,34,1,0,0,0,
        36,35,1,0,0,0,37,5,1,0,0,0,38,39,5,1,0,0,39,40,5,8,0,0,40,41,3,16,
        8,0,41,42,5,9,0,0,42,7,1,0,0,0,43,44,5,2,0,0,44,45,5,8,0,0,45,46,
        3,16,8,0,46,47,5,9,0,0,47,9,1,0,0,0,48,49,5,3,0,0,49,50,5,8,0,0,
        50,51,3,2,1,0,51,52,5,9,0,0,52,11,1,0,0,0,53,54,5,4,0,0,54,55,5,
        6,0,0,55,56,5,11,0,0,56,57,5,7,0,0,57,58,5,8,0,0,58,59,3,2,1,0,59,
        60,5,9,0,0,60,13,1,0,0,0,61,62,5,5,0,0,62,63,5,6,0,0,63,64,5,11,
        0,0,64,65,5,7,0,0,65,66,5,8,0,0,66,67,3,2,1,0,67,68,5,9,0,0,68,15,
        1,0,0,0,69,74,3,2,1,0,70,71,5,10,0,0,71,73,3,2,1,0,72,70,1,0,0,0,
        73,76,1,0,0,0,74,72,1,0,0,0,74,75,1,0,0,0,75,17,1,0,0,0,76,74,1,
        0,0,0,77,78,5,6,0,0,78,79,5,11,0,0,79,80,5,7,0,0,80,19,1,0,0,0,3,
        29,36,74
    ]

class CodeCheckParser ( Parser ):

    grammarFileName = "CodeCheck.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [ "<INVALID>", "'AND'", "'OR'", "'NOT'", "'EXISTS'", 
                     "'FORALL'", "'('", "')'", "'{'", "'}'", "','" ]

    symbolicNames = [ "<INVALID>", "AND", "OR", "NOT", "EXISTS", "FORALL", 
                      "LPAREN", "RPAREN", "LBRACE", "RBRACE", "COMMA", "DESCRIPTION", 
                      "WS" ]

    RULE_check = 0
    RULE_condition = 1
    RULE_logicalExpr = 2
    RULE_andExpr = 3
    RULE_orExpr = 4
    RULE_notExpr = 5
    RULE_existsExpr = 6
    RULE_forallExpr = 7
    RULE_conditionList = 8
    RULE_atomicCondition = 9

    ruleNames =  [ "check", "condition", "logicalExpr", "andExpr", "orExpr", 
                   "notExpr", "existsExpr", "forallExpr", "conditionList", 
                   "atomicCondition" ]

    EOF = Token.EOF
    AND=1
    OR=2
    NOT=3
    EXISTS=4
    FORALL=5
    LPAREN=6
    RPAREN=7
    LBRACE=8
    RBRACE=9
    COMMA=10
    DESCRIPTION=11
    WS=12

    def __init__(self, input:TokenStream, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.13.2")
        self._interp = ParserATNSimulator(self, self.atn, self.decisionsToDFA, self.sharedContextCache)
        self._predicates = None




    class CheckContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def condition(self):
            return self.getTypedRuleContext(CodeCheckParser.ConditionContext,0)


        def EOF(self):
            return self.getToken(CodeCheckParser.EOF, 0)

        def getRuleIndex(self):
            return CodeCheckParser.RULE_check

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterCheck" ):
                listener.enterCheck(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitCheck" ):
                listener.exitCheck(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitCheck" ):
                return visitor.visitCheck(self)
            else:
                return visitor.visitChildren(self)




    def check(self):

        localctx = CodeCheckParser.CheckContext(self, self._ctx, self.state)
        self.enterRule(localctx, 0, self.RULE_check)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 20
            self.condition()
            self.state = 21
            self.match(CodeCheckParser.EOF)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ConditionContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def logicalExpr(self):
            return self.getTypedRuleContext(CodeCheckParser.LogicalExprContext,0)


        def atomicCondition(self):
            return self.getTypedRuleContext(CodeCheckParser.AtomicConditionContext,0)


        def LPAREN(self):
            return self.getToken(CodeCheckParser.LPAREN, 0)

        def condition(self):
            return self.getTypedRuleContext(CodeCheckParser.ConditionContext,0)


        def RPAREN(self):
            return self.getToken(CodeCheckParser.RPAREN, 0)

        def getRuleIndex(self):
            return CodeCheckParser.RULE_condition

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterCondition" ):
                listener.enterCondition(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitCondition" ):
                listener.exitCondition(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitCondition" ):
                return visitor.visitCondition(self)
            else:
                return visitor.visitChildren(self)




    def condition(self):

        localctx = CodeCheckParser.ConditionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 2, self.RULE_condition)
        try:
            self.state = 29
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,0,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 23
                self.logicalExpr()
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 24
                self.atomicCondition()
                pass

            elif la_ == 3:
                self.enterOuterAlt(localctx, 3)
                self.state = 25
                self.match(CodeCheckParser.LPAREN)
                self.state = 26
                self.condition()
                self.state = 27
                self.match(CodeCheckParser.RPAREN)
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class LogicalExprContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def andExpr(self):
            return self.getTypedRuleContext(CodeCheckParser.AndExprContext,0)


        def orExpr(self):
            return self.getTypedRuleContext(CodeCheckParser.OrExprContext,0)


        def notExpr(self):
            return self.getTypedRuleContext(CodeCheckParser.NotExprContext,0)


        def existsExpr(self):
            return self.getTypedRuleContext(CodeCheckParser.ExistsExprContext,0)


        def forallExpr(self):
            return self.getTypedRuleContext(CodeCheckParser.ForallExprContext,0)


        def getRuleIndex(self):
            return CodeCheckParser.RULE_logicalExpr

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterLogicalExpr" ):
                listener.enterLogicalExpr(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitLogicalExpr" ):
                listener.exitLogicalExpr(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitLogicalExpr" ):
                return visitor.visitLogicalExpr(self)
            else:
                return visitor.visitChildren(self)




    def logicalExpr(self):

        localctx = CodeCheckParser.LogicalExprContext(self, self._ctx, self.state)
        self.enterRule(localctx, 4, self.RULE_logicalExpr)
        try:
            self.state = 36
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [1]:
                self.enterOuterAlt(localctx, 1)
                self.state = 31
                self.andExpr()
                pass
            elif token in [2]:
                self.enterOuterAlt(localctx, 2)
                self.state = 32
                self.orExpr()
                pass
            elif token in [3]:
                self.enterOuterAlt(localctx, 3)
                self.state = 33
                self.notExpr()
                pass
            elif token in [4]:
                self.enterOuterAlt(localctx, 4)
                self.state = 34
                self.existsExpr()
                pass
            elif token in [5]:
                self.enterOuterAlt(localctx, 5)
                self.state = 35
                self.forallExpr()
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class AndExprContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def AND(self):
            return self.getToken(CodeCheckParser.AND, 0)

        def LBRACE(self):
            return self.getToken(CodeCheckParser.LBRACE, 0)

        def conditionList(self):
            return self.getTypedRuleContext(CodeCheckParser.ConditionListContext,0)


        def RBRACE(self):
            return self.getToken(CodeCheckParser.RBRACE, 0)

        def getRuleIndex(self):
            return CodeCheckParser.RULE_andExpr

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterAndExpr" ):
                listener.enterAndExpr(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitAndExpr" ):
                listener.exitAndExpr(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitAndExpr" ):
                return visitor.visitAndExpr(self)
            else:
                return visitor.visitChildren(self)




    def andExpr(self):

        localctx = CodeCheckParser.AndExprContext(self, self._ctx, self.state)
        self.enterRule(localctx, 6, self.RULE_andExpr)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 38
            self.match(CodeCheckParser.AND)
            self.state = 39
            self.match(CodeCheckParser.LBRACE)
            self.state = 40
            self.conditionList()
            self.state = 41
            self.match(CodeCheckParser.RBRACE)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class OrExprContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def OR(self):
            return self.getToken(CodeCheckParser.OR, 0)

        def LBRACE(self):
            return self.getToken(CodeCheckParser.LBRACE, 0)

        def conditionList(self):
            return self.getTypedRuleContext(CodeCheckParser.ConditionListContext,0)


        def RBRACE(self):
            return self.getToken(CodeCheckParser.RBRACE, 0)

        def getRuleIndex(self):
            return CodeCheckParser.RULE_orExpr

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterOrExpr" ):
                listener.enterOrExpr(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitOrExpr" ):
                listener.exitOrExpr(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitOrExpr" ):
                return visitor.visitOrExpr(self)
            else:
                return visitor.visitChildren(self)




    def orExpr(self):

        localctx = CodeCheckParser.OrExprContext(self, self._ctx, self.state)
        self.enterRule(localctx, 8, self.RULE_orExpr)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 43
            self.match(CodeCheckParser.OR)
            self.state = 44
            self.match(CodeCheckParser.LBRACE)
            self.state = 45
            self.conditionList()
            self.state = 46
            self.match(CodeCheckParser.RBRACE)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class NotExprContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def NOT(self):
            return self.getToken(CodeCheckParser.NOT, 0)

        def LBRACE(self):
            return self.getToken(CodeCheckParser.LBRACE, 0)

        def condition(self):
            return self.getTypedRuleContext(CodeCheckParser.ConditionContext,0)


        def RBRACE(self):
            return self.getToken(CodeCheckParser.RBRACE, 0)

        def getRuleIndex(self):
            return CodeCheckParser.RULE_notExpr

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterNotExpr" ):
                listener.enterNotExpr(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitNotExpr" ):
                listener.exitNotExpr(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitNotExpr" ):
                return visitor.visitNotExpr(self)
            else:
                return visitor.visitChildren(self)




    def notExpr(self):

        localctx = CodeCheckParser.NotExprContext(self, self._ctx, self.state)
        self.enterRule(localctx, 10, self.RULE_notExpr)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 48
            self.match(CodeCheckParser.NOT)
            self.state = 49
            self.match(CodeCheckParser.LBRACE)
            self.state = 50
            self.condition()
            self.state = 51
            self.match(CodeCheckParser.RBRACE)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ExistsExprContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def EXISTS(self):
            return self.getToken(CodeCheckParser.EXISTS, 0)

        def LPAREN(self):
            return self.getToken(CodeCheckParser.LPAREN, 0)

        def DESCRIPTION(self):
            return self.getToken(CodeCheckParser.DESCRIPTION, 0)

        def RPAREN(self):
            return self.getToken(CodeCheckParser.RPAREN, 0)

        def LBRACE(self):
            return self.getToken(CodeCheckParser.LBRACE, 0)

        def condition(self):
            return self.getTypedRuleContext(CodeCheckParser.ConditionContext,0)


        def RBRACE(self):
            return self.getToken(CodeCheckParser.RBRACE, 0)

        def getRuleIndex(self):
            return CodeCheckParser.RULE_existsExpr

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterExistsExpr" ):
                listener.enterExistsExpr(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitExistsExpr" ):
                listener.exitExistsExpr(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitExistsExpr" ):
                return visitor.visitExistsExpr(self)
            else:
                return visitor.visitChildren(self)




    def existsExpr(self):

        localctx = CodeCheckParser.ExistsExprContext(self, self._ctx, self.state)
        self.enterRule(localctx, 12, self.RULE_existsExpr)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 53
            self.match(CodeCheckParser.EXISTS)
            self.state = 54
            self.match(CodeCheckParser.LPAREN)
            self.state = 55
            self.match(CodeCheckParser.DESCRIPTION)
            self.state = 56
            self.match(CodeCheckParser.RPAREN)
            self.state = 57
            self.match(CodeCheckParser.LBRACE)
            self.state = 58
            self.condition()
            self.state = 59
            self.match(CodeCheckParser.RBRACE)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ForallExprContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def FORALL(self):
            return self.getToken(CodeCheckParser.FORALL, 0)

        def LPAREN(self):
            return self.getToken(CodeCheckParser.LPAREN, 0)

        def DESCRIPTION(self):
            return self.getToken(CodeCheckParser.DESCRIPTION, 0)

        def RPAREN(self):
            return self.getToken(CodeCheckParser.RPAREN, 0)

        def LBRACE(self):
            return self.getToken(CodeCheckParser.LBRACE, 0)

        def condition(self):
            return self.getTypedRuleContext(CodeCheckParser.ConditionContext,0)


        def RBRACE(self):
            return self.getToken(CodeCheckParser.RBRACE, 0)

        def getRuleIndex(self):
            return CodeCheckParser.RULE_forallExpr

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterForallExpr" ):
                listener.enterForallExpr(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitForallExpr" ):
                listener.exitForallExpr(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitForallExpr" ):
                return visitor.visitForallExpr(self)
            else:
                return visitor.visitChildren(self)




    def forallExpr(self):

        localctx = CodeCheckParser.ForallExprContext(self, self._ctx, self.state)
        self.enterRule(localctx, 14, self.RULE_forallExpr)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 61
            self.match(CodeCheckParser.FORALL)
            self.state = 62
            self.match(CodeCheckParser.LPAREN)
            self.state = 63
            self.match(CodeCheckParser.DESCRIPTION)
            self.state = 64
            self.match(CodeCheckParser.RPAREN)
            self.state = 65
            self.match(CodeCheckParser.LBRACE)
            self.state = 66
            self.condition()
            self.state = 67
            self.match(CodeCheckParser.RBRACE)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ConditionListContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def condition(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(CodeCheckParser.ConditionContext)
            else:
                return self.getTypedRuleContext(CodeCheckParser.ConditionContext,i)


        def COMMA(self, i:int=None):
            if i is None:
                return self.getTokens(CodeCheckParser.COMMA)
            else:
                return self.getToken(CodeCheckParser.COMMA, i)

        def getRuleIndex(self):
            return CodeCheckParser.RULE_conditionList

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterConditionList" ):
                listener.enterConditionList(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitConditionList" ):
                listener.exitConditionList(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitConditionList" ):
                return visitor.visitConditionList(self)
            else:
                return visitor.visitChildren(self)




    def conditionList(self):

        localctx = CodeCheckParser.ConditionListContext(self, self._ctx, self.state)
        self.enterRule(localctx, 16, self.RULE_conditionList)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 69
            self.condition()
            self.state = 74
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==10:
                self.state = 70
                self.match(CodeCheckParser.COMMA)
                self.state = 71
                self.condition()
                self.state = 76
                self._errHandler.sync(self)
                _la = self._input.LA(1)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class AtomicConditionContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def LPAREN(self):
            return self.getToken(CodeCheckParser.LPAREN, 0)

        def DESCRIPTION(self):
            return self.getToken(CodeCheckParser.DESCRIPTION, 0)

        def RPAREN(self):
            return self.getToken(CodeCheckParser.RPAREN, 0)

        def getRuleIndex(self):
            return CodeCheckParser.RULE_atomicCondition

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterAtomicCondition" ):
                listener.enterAtomicCondition(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitAtomicCondition" ):
                listener.exitAtomicCondition(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitAtomicCondition" ):
                return visitor.visitAtomicCondition(self)
            else:
                return visitor.visitChildren(self)




    def atomicCondition(self):

        localctx = CodeCheckParser.AtomicConditionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 18, self.RULE_atomicCondition)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 77
            self.match(CodeCheckParser.LPAREN)
            self.state = 78
            self.match(CodeCheckParser.DESCRIPTION)
            self.state = 79
            self.match(CodeCheckParser.RPAREN)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx





