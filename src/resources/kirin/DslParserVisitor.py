# Generated from DslParser.g4 by ANTLR 4.13.2
from antlr4 import *
if "." in __name__:
    from .DslParser import DslParser
else:
    from DslParser import DslParser

# This class defines a complete generic visitor for a parse tree produced by DslParser.

class DslParserVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by DslParser#statements.
    def visitStatements(self, ctx:DslParser.StatementsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#removeOperation.
    def visitRemoveOperation(self, ctx:DslParser.RemoveOperationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#repeatOperation.
    def visitRepeatOperation(self, ctx:DslParser.RepeatOperationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#existOperation.
    def visitExistOperation(self, ctx:DslParser.ExistOperationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#existCondition.
    def visitExistCondition(self, ctx:DslParser.ExistConditionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#singleCondition.
    def visitSingleCondition(self, ctx:DslParser.SingleConditionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#stepList.
    def visitStepList(self, ctx:DslParser.StepListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#nodeStmt.
    def visitNodeStmt(self, ctx:DslParser.NodeStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#queryStmt.
    def visitQueryStmt(self, ctx:DslParser.QueryStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#nodeQueryExpr.
    def visitNodeQueryExpr(self, ctx:DslParser.NodeQueryExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#nodePathStmt.
    def visitNodePathStmt(self, ctx:DslParser.NodePathStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#singleNodeQueryExpr.
    def visitSingleNodeQueryExpr(self, ctx:DslParser.SingleNodeQueryExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#singleNodeAttrQueryExpr.
    def visitSingleNodeAttrQueryExpr(self, ctx:DslParser.SingleNodeAttrQueryExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#containedDesc.
    def visitContainedDesc(self, ctx:DslParser.ContainedDescContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#configInfo.
    def visitConfigInfo(self, ctx:DslParser.ConfigInfoContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#configStmt.
    def visitConfigStmt(self, ctx:DslParser.ConfigStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#preciseMatch.
    def visitPreciseMatch(self, ctx:DslParser.PreciseMatchContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#fileNameAttr.
    def visitFileNameAttr(self, ctx:DslParser.FileNameAttrContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#xPathAttr.
    def visitXPathAttr(self, ctx:DslParser.XPathAttrContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#keyValueAttr.
    def visitKeyValueAttr(self, ctx:DslParser.KeyValueAttrContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#taintInfo.
    def visitTaintInfo(self, ctx:DslParser.TaintInfoContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#taintSource.
    def visitTaintSource(self, ctx:DslParser.TaintSourceContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#taintSink.
    def visitTaintSink(self, ctx:DslParser.TaintSinkContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#taintPassthrough.
    def visitTaintPassthrough(self, ctx:DslParser.TaintPassthroughContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#taintCleanse.
    def visitTaintCleanse(self, ctx:DslParser.TaintCleanseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#inArgs.
    def visitInArgs(self, ctx:DslParser.InArgsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#outArgs.
    def visitOutArgs(self, ctx:DslParser.OutArgsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#taintList.
    def visitTaintList(self, ctx:DslParser.TaintListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#taint.
    def visitTaint(self, ctx:DslParser.TaintContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#symbolFlagInfo.
    def visitSymbolFlagInfo(self, ctx:DslParser.SymbolFlagInfoContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#flagList.
    def visitFlagList(self, ctx:DslParser.FlagListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#flag.
    def visitFlag(self, ctx:DslParser.FlagContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#flagOperator.
    def visitFlagOperator(self, ctx:DslParser.FlagOperatorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#ruleSetMessage.
    def visitRuleSetMessage(self, ctx:DslParser.RuleSetMessageContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#ruleSetName.
    def visitRuleSetName(self, ctx:DslParser.RuleSetNameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#language.
    def visitLanguage(self, ctx:DslParser.LanguageContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#ruleSetType.
    def visitRuleSetType(self, ctx:DslParser.RuleSetTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#engine.
    def visitEngine(self, ctx:DslParser.EngineContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#version.
    def visitVersion(self, ctx:DslParser.VersionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#descriptionMsg.
    def visitDescriptionMsg(self, ctx:DslParser.DescriptionMsgContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#customInfo.
    def visitCustomInfo(self, ctx:DslParser.CustomInfoContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#keyValuePair.
    def visitKeyValuePair(self, ctx:DslParser.KeyValuePairContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#vulnerability.
    def visitVulnerability(self, ctx:DslParser.VulnerabilityContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#category.
    def visitCategory(self, ctx:DslParser.CategoryContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#subCategory.
    def visitSubCategory(self, ctx:DslParser.SubCategoryContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#issueType.
    def visitIssueType(self, ctx:DslParser.IssueTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#cwe.
    def visitCwe(self, ctx:DslParser.CweContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#severity.
    def visitSeverity(self, ctx:DslParser.SeverityContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#severityLabel.
    def visitSeverityLabel(self, ctx:DslParser.SeverityLabelContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#ruleMsg.
    def visitRuleMsg(self, ctx:DslParser.RuleMsgContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#description.
    def visitDescription(self, ctx:DslParser.DescriptionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#ruleId.
    def visitRuleId(self, ctx:DslParser.RuleIdContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#reportExpr.
    def visitReportExpr(self, ctx:DslParser.ReportExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#parameterizedWarningInfo.
    def visitParameterizedWarningInfo(self, ctx:DslParser.ParameterizedWarningInfoContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#valueAttr.
    def visitValueAttr(self, ctx:DslParser.ValueAttrContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#imprt.
    def visitImprt(self, ctx:DslParser.ImprtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#condExpr.
    def visitCondExpr(self, ctx:DslParser.CondExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#condition.
    def visitCondition(self, ctx:DslParser.ConditionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#directCondition.
    def visitDirectCondition(self, ctx:DslParser.DirectConditionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#boolCondition.
    def visitBoolCondition(self, ctx:DslParser.BoolConditionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#nodeCondition.
    def visitNodeCondition(self, ctx:DslParser.NodeConditionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#nodeNullCondition.
    def visitNodeNullCondition(self, ctx:DslParser.NodeNullConditionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#numCondition.
    def visitNumCondition(self, ctx:DslParser.NumConditionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#originalNumCondition.
    def visitOriginalNumCondition(self, ctx:DslParser.OriginalNumConditionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#numCalCondition.
    def visitNumCalCondition(self, ctx:DslParser.NumCalConditionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#numLeftExpr.
    def visitNumLeftExpr(self, ctx:DslParser.NumLeftExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#objCondition.
    def visitObjCondition(self, ctx:DslParser.ObjConditionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#strCondition.
    def visitStrCondition(self, ctx:DslParser.StrConditionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#boolCollectionCondition.
    def visitBoolCollectionCondition(self, ctx:DslParser.BoolCollectionConditionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#objCollectionCondition.
    def visitObjCollectionCondition(self, ctx:DslParser.ObjCollectionConditionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#nodeCollectionCondition.
    def visitNodeCollectionCondition(self, ctx:DslParser.NodeCollectionConditionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#numCollectionCondition.
    def visitNumCollectionCondition(self, ctx:DslParser.NumCollectionConditionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#strCollectionCondition.
    def visitStrCollectionCondition(self, ctx:DslParser.StrCollectionConditionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#groupCondition.
    def visitGroupCondition(self, ctx:DslParser.GroupConditionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#hasCondition.
    def visitHasCondition(self, ctx:DslParser.HasConditionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#isCondition.
    def visitIsCondition(self, ctx:DslParser.IsConditionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#isAliasCondition.
    def visitIsAliasCondition(self, ctx:DslParser.IsAliasConditionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#dfgCondition.
    def visitDfgCondition(self, ctx:DslParser.DfgConditionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#dfgPathCondition.
    def visitDfgPathCondition(self, ctx:DslParser.DfgPathConditionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#encapsulateCondition.
    def visitEncapsulateCondition(self, ctx:DslParser.EncapsulateConditionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#objExpr.
    def visitObjExpr(self, ctx:DslParser.ObjExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#boolExpr.
    def visitBoolExpr(self, ctx:DslParser.BoolExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#numExpr.
    def visitNumExpr(self, ctx:DslParser.NumExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#nullExpr.
    def visitNullExpr(self, ctx:DslParser.NullExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#numRightExpr.
    def visitNumRightExpr(self, ctx:DslParser.NumRightExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#strExpr.
    def visitStrExpr(self, ctx:DslParser.StrExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#strConditionEndInStr.
    def visitStrConditionEndInStr(self, ctx:DslParser.StrConditionEndInStrContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#strConditionEndInNum.
    def visitStrConditionEndInNum(self, ctx:DslParser.StrConditionEndInNumContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#strConditionEndInBool.
    def visitStrConditionEndInBool(self, ctx:DslParser.StrConditionEndInBoolContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#leftStrOperandEndInStr.
    def visitLeftStrOperandEndInStr(self, ctx:DslParser.LeftStrOperandEndInStrContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#rightStrOperandEndInStr.
    def visitRightStrOperandEndInStr(self, ctx:DslParser.RightStrOperandEndInStrContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#strVariableEndInStr.
    def visitStrVariableEndInStr(self, ctx:DslParser.StrVariableEndInStrContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#strConstant.
    def visitStrConstant(self, ctx:DslParser.StrConstantContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#leftStrOperandEndInNum.
    def visitLeftStrOperandEndInNum(self, ctx:DslParser.LeftStrOperandEndInNumContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#rightStrOperandEndInNum.
    def visitRightStrOperandEndInNum(self, ctx:DslParser.RightStrOperandEndInNumContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#strVariableEndInNum.
    def visitStrVariableEndInNum(self, ctx:DslParser.StrVariableEndInNumContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#strInvokeStrChain.
    def visitStrInvokeStrChain(self, ctx:DslParser.StrInvokeStrChainContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#strInvokeIntExpr.
    def visitStrInvokeIntExpr(self, ctx:DslParser.StrInvokeIntExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#leftStrOperandEndInBool.
    def visitLeftStrOperandEndInBool(self, ctx:DslParser.LeftStrOperandEndInBoolContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#rightStrOperandEndInBool.
    def visitRightStrOperandEndInBool(self, ctx:DslParser.RightStrOperandEndInBoolContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#singleStrOperandEndInBool.
    def visitSingleStrOperandEndInBool(self, ctx:DslParser.SingleStrOperandEndInBoolContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#strVariableEndInBool.
    def visitStrVariableEndInBool(self, ctx:DslParser.StrVariableEndInBoolContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#strInvokeBoolExpr.
    def visitStrInvokeBoolExpr(self, ctx:DslParser.StrInvokeBoolExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#prefixStrConst.
    def visitPrefixStrConst(self, ctx:DslParser.PrefixStrConstContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#suffixStrConst.
    def visitSuffixStrConst(self, ctx:DslParser.SuffixStrConstContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#utilityOperator.
    def visitUtilityOperator(self, ctx:DslParser.UtilityOperatorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#prefixIntConst.
    def visitPrefixIntConst(self, ctx:DslParser.PrefixIntConstContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#suffixIntConst.
    def visitSuffixIntConst(self, ctx:DslParser.SuffixIntConstContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#boolAttr.
    def visitBoolAttr(self, ctx:DslParser.BoolAttrContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#normalBoolAttr.
    def visitNormalBoolAttr(self, ctx:DslParser.NormalBoolAttrContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#indexBoolAttr.
    def visitIndexBoolAttr(self, ctx:DslParser.IndexBoolAttrContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#aliasBoolAttr.
    def visitAliasBoolAttr(self, ctx:DslParser.AliasBoolAttrContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#nodeAttrWithAlias.
    def visitNodeAttrWithAlias(self, ctx:DslParser.NodeAttrWithAliasContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#nonRecursiveNodeAttrWithAlias.
    def visitNonRecursiveNodeAttrWithAlias(self, ctx:DslParser.NonRecursiveNodeAttrWithAliasContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#nodeAttr.
    def visitNodeAttr(self, ctx:DslParser.NodeAttrContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#nonRecursiveNodeAttr.
    def visitNonRecursiveNodeAttr(self, ctx:DslParser.NonRecursiveNodeAttrContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#recursiveNodeAttr.
    def visitRecursiveNodeAttr(self, ctx:DslParser.RecursiveNodeAttrContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#aliasNodeAttr.
    def visitAliasNodeAttr(self, ctx:DslParser.AliasNodeAttrContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#numAttr.
    def visitNumAttr(self, ctx:DslParser.NumAttrContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#normalNumAttr.
    def visitNormalNumAttr(self, ctx:DslParser.NormalNumAttrContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#indexNumAttr.
    def visitIndexNumAttr(self, ctx:DslParser.IndexNumAttrContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#aliasNumAttr.
    def visitAliasNumAttr(self, ctx:DslParser.AliasNumAttrContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#groupAttr.
    def visitGroupAttr(self, ctx:DslParser.GroupAttrContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#aliasGroupAttr.
    def visitAliasGroupAttr(self, ctx:DslParser.AliasGroupAttrContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#objAttr.
    def visitObjAttr(self, ctx:DslParser.ObjAttrContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#normalObjAttr.
    def visitNormalObjAttr(self, ctx:DslParser.NormalObjAttrContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#indexObjAttr.
    def visitIndexObjAttr(self, ctx:DslParser.IndexObjAttrContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#aliasObjAttr.
    def visitAliasObjAttr(self, ctx:DslParser.AliasObjAttrContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#strAttr.
    def visitStrAttr(self, ctx:DslParser.StrAttrContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#normalStrAttr.
    def visitNormalStrAttr(self, ctx:DslParser.NormalStrAttrContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#indexStrAttr.
    def visitIndexStrAttr(self, ctx:DslParser.IndexStrAttrContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#aliasStrAttr.
    def visitAliasStrAttr(self, ctx:DslParser.AliasStrAttrContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#collectionAttr.
    def visitCollectionAttr(self, ctx:DslParser.CollectionAttrContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#collectionBoolAttr.
    def visitCollectionBoolAttr(self, ctx:DslParser.CollectionBoolAttrContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#collectionNodeAttr.
    def visitCollectionNodeAttr(self, ctx:DslParser.CollectionNodeAttrContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#collectionNumAttr.
    def visitCollectionNumAttr(self, ctx:DslParser.CollectionNumAttrContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#collectionObjAttr.
    def visitCollectionObjAttr(self, ctx:DslParser.CollectionObjAttrContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#collectionStrAttr.
    def visitCollectionStrAttr(self, ctx:DslParser.CollectionStrAttrContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#singleNodeAttr.
    def visitSingleNodeAttr(self, ctx:DslParser.SingleNodeAttrContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#compositeSingleNodeAttr.
    def visitCompositeSingleNodeAttr(self, ctx:DslParser.CompositeSingleNodeAttrContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#collectionSingleNodeAttr.
    def visitCollectionSingleNodeAttr(self, ctx:DslParser.CollectionSingleNodeAttrContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#simpleSingleNodeAttr.
    def visitSimpleSingleNodeAttr(self, ctx:DslParser.SimpleSingleNodeAttrContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#aliasHead.
    def visitAliasHead(self, ctx:DslParser.AliasHeadContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#strUtilityStr.
    def visitStrUtilityStr(self, ctx:DslParser.StrUtilityStrContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#strUtilityStrNameWithoutParam.
    def visitStrUtilityStrNameWithoutParam(self, ctx:DslParser.StrUtilityStrNameWithoutParamContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#strUtilityStrNameWithSingleIntParam.
    def visitStrUtilityStrNameWithSingleIntParam(self, ctx:DslParser.StrUtilityStrNameWithSingleIntParamContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#strUtilityStrNameWithDoubleIntParam.
    def visitStrUtilityStrNameWithDoubleIntParam(self, ctx:DslParser.StrUtilityStrNameWithDoubleIntParamContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#strUtilityStrNameWithSingleStringParam.
    def visitStrUtilityStrNameWithSingleStringParam(self, ctx:DslParser.StrUtilityStrNameWithSingleStringParamContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#strUtilityStrNameWithDoubleStringParam.
    def visitStrUtilityStrNameWithDoubleStringParam(self, ctx:DslParser.StrUtilityStrNameWithDoubleStringParamContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#strUtilityStrNameWithSingleStringParamAndSingleIntParam.
    def visitStrUtilityStrNameWithSingleStringParamAndSingleIntParam(self, ctx:DslParser.StrUtilityStrNameWithSingleStringParamAndSingleIntParamContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#strUtilityInt.
    def visitStrUtilityInt(self, ctx:DslParser.StrUtilityIntContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#strUtilityIntNameWithoutParam.
    def visitStrUtilityIntNameWithoutParam(self, ctx:DslParser.StrUtilityIntNameWithoutParamContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#strUtilityIntNameWithSingleStringParam.
    def visitStrUtilityIntNameWithSingleStringParam(self, ctx:DslParser.StrUtilityIntNameWithSingleStringParamContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#strUtilityBool.
    def visitStrUtilityBool(self, ctx:DslParser.StrUtilityBoolContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#strUtiltiyBoolNameWithoutParam.
    def visitStrUtiltiyBoolNameWithoutParam(self, ctx:DslParser.StrUtiltiyBoolNameWithoutParamContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#allInt.
    def visitAllInt(self, ctx:DslParser.AllIntContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#size.
    def visitSize(self, ctx:DslParser.SizeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#index.
    def visitIndex(self, ctx:DslParser.IndexContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#boolOperator.
    def visitBoolOperator(self, ctx:DslParser.BoolOperatorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#numOperator.
    def visitNumOperator(self, ctx:DslParser.NumOperatorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#strOperator.
    def visitStrOperator(self, ctx:DslParser.StrOperatorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#collectionOperator.
    def visitCollectionOperator(self, ctx:DslParser.CollectionOperatorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#hasOperator.
    def visitHasOperator(self, ctx:DslParser.HasOperatorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#nullOperator.
    def visitNullOperator(self, ctx:DslParser.NullOperatorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#isOperator.
    def visitIsOperator(self, ctx:DslParser.IsOperatorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#rootNodeAttr.
    def visitRootNodeAttr(self, ctx:DslParser.RootNodeAttrContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#alias.
    def visitAlias(self, ctx:DslParser.AliasContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#stepName.
    def visitStepName(self, ctx:DslParser.StepNameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#comment.
    def visitComment(self, ctx:DslParser.CommentContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#direction.
    def visitDirection(self, ctx:DslParser.DirectionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DslParser#presence.
    def visitPresence(self, ctx:DslParser.PresenceContext):
        return self.visitChildren(ctx)



del DslParser