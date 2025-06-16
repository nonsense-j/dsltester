parser grammar DslParser;

options {
  tokenVocab = HornLexer;
}

statements: (imprt)*? (ruleSetMessage)? (nodeStmt)* (removeOperation)?
        | nodePathStmt*;

//////////// remove checker /////////////
removeOperation: (comment* repeatOperation comment* |comment*  existOperation comment*)+;

repeatOperation: Remove stepList In stepName Semicolon;
existOperation: Remove stepList Satisfy comment* existCondition comment* Semicolon;
existCondition: (AND | OR) LeftBracket comment* existCondition comment*
                                       (Comma comment* existCondition comment*)+ RightBracket
                | NOT LeftBracket comment* existCondition comment* RightBracket
                | singleCondition;
singleCondition: stepName Point Size numOperator numExpr
               | stepName;
stepList: stepName
        | LeftBracket stepName (Comma stepName)+ RightBracket;

/////////// query checker ////////////
nodeStmt: (ruleMsg)? (taintInfo)? (vulnerability)? queryStmt
        | (taintInfo)? (ruleMsg)? (vulnerability)? queryStmt
        | (ruleMsg)? (vulnerability)? configInfo (configStmt)*;

queryStmt: comment* (stepName Colon)? nodeQueryExpr Semicolon comment*;

nodeQueryExpr: comment* rootNodeAttr (Satisfy comment* condExpr comment*)?;

nodePathStmt: comment* singleNodeQueryExpr comment* (Point singleNodeAttrQueryExpr comment*)* Point Path
    (LeftBracket RightBracket | LeftBracket alias (Comma alias)* RightBracket) Semicolon;
singleNodeQueryExpr: comment* Node (alias | As alias)? (Satisfy comment* condExpr comment*)?;
singleNodeAttrQueryExpr: comment* singleNodeAttr (alias | As alias)? (Satisfy comment* condExpr comment*)?;

containedDesc: comment* rootNodeAttr Satisfy comment* condExpr comment*
        | comment* rootNodeAttr comment*
        ;

//////////// configInfo ///////////////
configInfo: ConfigLabel;
configStmt: Properties Equal LeftCurlyBracket
    fileNameAttr
    Comma (xPathAttr | keyValueAttr)
    (Comma PreciseMatch Equal preciseMatch)? RightCurlyBracket;

preciseMatch: True | False;
fileNameAttr: FileName (Eq | Match) strExpr;
xPathAttr: XpathMatchExpression (Eq | Match) strExpr;
keyValueAttr: PropertyKey (Eq | Match) strExpr Comma PropertyValue (Eq | Match) strExpr;

//////////// Taint info //////////////
taintInfo: comment* (taintSource | taintSink | taintPassthrough | taintCleanse);

// source only supports "+"
taintSource: SourceLabel LeftBracket outArgs Comma symbolFlagInfo RightBracket;

// sink supports flag with both "+" and "-", 均不用告警and(or(+1, +2), not(-3), not(-4));
taintSink: SinkLabel LeftBracket inArgs Comma symbolFlagInfo RightBracket;

// passthrough supports both "+" and "-"
// taintIn means the in flow fact, it could be argument, node itself
// taintOut means the out flow fact, it could be argument, node itself, return value
taintPassthrough: PassthroughLabel LeftBracket inArgs Comma outArgs (Comma symbolFlagInfo)? RightBracket;

taintCleanse: CleanseLabel LeftBracket inArgs RightBracket;

inArgs: InArgs Equal taintList;

outArgs: OutArgs Equal taintList;

taintList: LeftMidBracket taint (Comma taint)? RightMidBracket
       | taint;

taint: This
   | Return
   | INT
   | INT Minus INT
   | INT Point Point Point
   | INT (Point Point Dollar INT)*;

symbolFlagInfo: Flag Equal flagList;

flagList: LeftMidBracket flag (Comma flag)? RightMidBracket
        | flag;

flag: (flagOperator)? ALIAS
        | Cooddy;

flagOperator: Plus | Minus;

////////// ruleSetMessage  ////////////
ruleSetMessage: comment* RuleSetMessageLabel LeftBracket
                    RuleSetName Equal ruleSetName
                    (Comma Language Equal language)?
                    (Comma Type Equal ruleSetType)?
                    (Comma Engine Equal engine)?
                    (Comma Version Equal version)?
                    Comma ReportMsg Equal descriptionMsg
                    (Comma CustomInfo Equal LeftBracket customInfo RightBracket)?
                    RightBracket;

ruleSetName: strExpr;
language: Java | Python | CPP | C | ArkTs | TypeScript | JavaScript;
ruleSetType: Taint | Structural;
engine: Cooddy | CSA | Soot | Cpg;
version: strExpr;
descriptionMsg: strExpr;
customInfo: (keyValuePair)? (Comma keyValuePair)* ;
keyValuePair: strExpr Equal strExpr;

/////////// vulnerability ///////////
vulnerability: VulnerabilityLabel LeftBracket category
                  Comma subCategory
                  Comma issueType
                  Comma cwe
                  Comma severity RightBracket;

category: Category Equal strExpr;
subCategory: Subcategory Equal strExpr;
issueType: IssueType Equal strExpr;
cwe: CWE Equal strExpr;
severity: Severity Equal severityLabel;
severityLabel: Suggest | Normal | Critical | Fatal | Error | Warning;

/////////// ruleMsg ///////////
ruleMsg: comment* RuleMsgLabel LeftBracket description (Comma ruleId)? RightBracket
       | comment* RuleMsgLabel LeftBracket ruleId RightBracket;
description: ReportMsg Equal reportExpr;
ruleId: RuleId Equal strExpr;
reportExpr: (parameterizedWarningInfo | strExpr) (Plus (parameterizedWarningInfo | strExpr))*;
parameterizedWarningInfo: alias (Point singleNodeAttr)* (Point valueAttr)?;
valueAttr: NumAttr | ObjPropertyAttr | StrAttr | BoolAttr;

/////////// import ///////////
imprt: comment* ImportLabel LeftBracket strExpr RightBracket;

//////////// Condition //////////////
condExpr:  (AND | OR) LeftBracket comment* condExpr comment* (Comma comment* condExpr comment*)+ RightBracket
         | NOT LeftBracket comment* condExpr comment* RightBracket
         | condition
         ;

condition: directCondition
          | encapsulateCondition
          ;
          
directCondition: boolCondition
               | nodeCondition
               | nodeNullCondition
               | numCondition
               | objCondition
               | strCondition
               | boolCollectionCondition
               | nodeCollectionCondition
               | numCollectionCondition
               | objCollectionCondition
               | strCollectionCondition
               | groupCondition
               | hasCondition
               | isCondition
               | isAliasCondition
               | dfgCondition
               | dfgPathCondition
               ;
boolCondition: aliasHead? boolAttr boolOperator (boolExpr | aliasBoolAttr)
             | aliasHead? boolAttr
             | BooleanNot aliasHead? boolAttr;
nodeCondition: aliasHead? nodeAttrWithAlias Satisfy comment* condExpr comment*;
nodeNullCondition: aliasHead? nodeAttrWithAlias nullOperator nullExpr;
numCondition: originalNumCondition
            | numCalCondition;

originalNumCondition: aliasHead? numAttr numOperator numRightExpr;
numCalCondition: numLeftExpr numOperator numRightExpr;
numLeftExpr: prefixIntConst? aliasHead? numAttr suffixIntConst?;

objCondition: aliasHead? objAttr (numOperator numExpr
                                 | boolOperator boolExpr
                                 | strOperator (strExpr | aliasStrAttr | aliasObjAttr));
strCondition: strConditionEndInStr
            | strConditionEndInNum
            | strConditionEndInBool
            ;
boolCollectionCondition: aliasHead? collectionBoolAttr collectionOperator boolExpr;
objCollectionCondition: aliasHead? collectionObjAttr collectionOperator objExpr;
nodeCollectionCondition: (aliasHead? collectionNodeAttr | alias) collectionOperator alias Satisfy comment* condExpr comment*;
numCollectionCondition: aliasHead? collectionNumAttr collectionOperator numExpr;
strCollectionCondition: aliasHead? collectionStrAttr collectionOperator strExpr;
groupCondition: aliasHead? groupAttr numOperator numRightExpr;
hasCondition: (aliasHead? nodeAttrWithAlias | alias | This) hasOperator containedDesc;
isCondition: (aliasHead? nodeAttrWithAlias | alias | This) isOperator (Node | NodeAttr) (Satisfy comment* condExpr comment*)?;
isAliasCondition: (aliasHead? nonRecursiveNodeAttrWithAlias | alias | This) isOperator aliasNodeAttr;
dfgCondition: (aliasHead? nodeAttrWithAlias | alias | This) presence direction LeftBracket containedDesc (Comma Depth Equal INT)? RightBracket;
dfgPathCondition: (aliasHead? nodeAttrWithAlias | alias | This) presence direction LeftBracket containedDesc Until containedDesc (Comma Depth Equal INT)? RightBracket;

encapsulateCondition: Condition LeftBracket strExpr (Comma strExpr)* RightBracket
                    | Condition;

////////////// Expression //////////////

objExpr: comment* boolExpr comment*
       | comment* numExpr comment*
       | comment* strExpr comment*
       | comment* nullExpr comment*
       ;
       
boolExpr: True
        | False
        ;
         
numExpr: (Plus | Minus)? INT (Point INT)?;

nullExpr: NULL;

numRightExpr: numExpr | aliasNumAttr | aliasGroupAttr;

strExpr: ID | STRING;

strConditionEndInStr: leftStrOperandEndInStr strOperator rightStrOperandEndInStr;

strConditionEndInNum: leftStrOperandEndInNum numOperator rightStrOperandEndInNum;

strConditionEndInBool: leftStrOperandEndInBool boolOperator rightStrOperandEndInBool
                     | singleStrOperandEndInBool;

leftStrOperandEndInStr: strVariableEndInStr;

rightStrOperandEndInStr: strConstant | strVariableEndInStr;

strVariableEndInStr: prefixStrConst? (strAttr | aliasStrAttr | aliasObjAttr) strInvokeStrChain? suffixStrConst?;

strConstant: strExpr;

leftStrOperandEndInNum: strVariableEndInNum;

rightStrOperandEndInNum: numRightExpr | strVariableEndInNum;

strVariableEndInNum: prefixIntConst? aliasHead? strAttr strInvokeStrChain? strInvokeIntExpr suffixIntConst?;

strInvokeStrChain: (Point strUtilityStr)+;

strInvokeIntExpr: Point strUtilityInt;

leftStrOperandEndInBool: strVariableEndInBool;

rightStrOperandEndInBool: boolExpr | strVariableEndInBool;

singleStrOperandEndInBool: BooleanNot? strVariableEndInBool;

strVariableEndInBool: aliasHead? strAttr strInvokeStrChain? strInvokeBoolExpr;

strInvokeBoolExpr: Point strUtilityBool;

prefixStrConst: strExpr Plus;

suffixStrConst: Plus strExpr;

utilityOperator: Plus | Minus | Star | Divide;

prefixIntConst: numExpr utilityOperator;

suffixIntConst: utilityOperator numExpr;

////////////// Attribute //////////////
boolAttr: normalBoolAttr
        | indexBoolAttr
        ;
normalBoolAttr: (singleNodeAttr Point)* BoolAttr;
indexBoolAttr: collectionBoolAttr index;
aliasBoolAttr: aliasHead boolAttr;

nodeAttrWithAlias: nodeAttr (As alias | alias)?;
nonRecursiveNodeAttrWithAlias: nonRecursiveNodeAttr (As alias | alias)?;
nodeAttr: singleNodeAttr (Point singleNodeAttr)*
        | singleNodeAttr (Point singleNodeAttr)* Point recursiveNodeAttr
        | recursiveNodeAttr;
// repeatNodeAttr: fd.(functionCalls.function)*
nonRecursiveNodeAttr: singleNodeAttr (Point singleNodeAttr)*;
recursiveNodeAttr: singleNodeAttr Star
            | LeftBracket (singleNodeAttr) (Point singleNodeAttr)* RightBracket Star;

aliasNodeAttr: alias (Point singleNodeAttr)*;

numAttr:  normalNumAttr
        | indexNumAttr
        ;
normalNumAttr: (singleNodeAttr Point)* NumAttr;
indexNumAttr: collectionNumAttr index;
aliasNumAttr: aliasHead numAttr;

groupAttr: (boolAttr | nonRecursiveNodeAttr | numAttr | objAttr | strAttr | collectionAttr | alias) Point size;
aliasGroupAttr: aliasHead groupAttr;

objAttr: normalObjAttr
       | indexObjAttr
       ;
normalObjAttr: (singleNodeAttr Point)* (ObjPropertyAttr | ObjNodeAttr);
indexObjAttr: collectionObjAttr index;
aliasObjAttr: aliasHead objAttr;

strAttr:  normalStrAttr
        | indexStrAttr
        ;
normalStrAttr: (singleNodeAttr Point)* StrAttr;
indexStrAttr: collectionStrAttr index;  
aliasStrAttr: aliasHead strAttr;

collectionAttr: collectionBoolAttr
              | collectionNodeAttr
              | collectionNumAttr
              | collectionObjAttr
              | collectionStrAttr
              ;
collectionBoolAttr: (singleNodeAttr Point)* CollectionBoolAttr;
collectionNodeAttr: (singleNodeAttr Point)* CollectionNodeAttr;
collectionNumAttr: (singleNodeAttr Point)* CollectionNumAttr;
collectionObjAttr: (singleNodeAttr Point)* CollectionObjAttr;
collectionStrAttr: (singleNodeAttr Point)* CollectionStrAttr;

singleNodeAttr: compositeSingleNodeAttr
              | collectionSingleNodeAttr
              | simpleSingleNodeAttr
              ;
compositeSingleNodeAttr: CollectionNodeAttr index;
collectionSingleNodeAttr: CollectionNodeAttr;
simpleSingleNodeAttr: NodeAttr;

aliasHead: alias Point;

////////////// UtilityFunction ///////////
strUtilityStr: strUtilityStrNameWithoutParam LeftBracket RightBracket
            | strUtilityStrNameWithSingleIntParam LeftBracket allInt RightBracket
            | strUtilityStrNameWithDoubleIntParam LeftBracket allInt Comma allInt RightBracket
            | strUtilityStrNameWithSingleStringParam LeftBracket strExpr RightBracket
            | strUtilityStrNameWithDoubleStringParam LeftBracket strExpr Comma strExpr RightBracket
            | strUtilityStrNameWithSingleStringParamAndSingleIntParam LeftBracket strExpr Comma allInt RightBracket
            ;

strUtilityStrNameWithoutParam: ToLowerCase | ToUpperCase | Capitalize | ShortName | Trim;

strUtilityStrNameWithSingleIntParam: Substring;

strUtilityStrNameWithDoubleIntParam: Substring;

strUtilityStrNameWithSingleStringParam: Trim;

strUtilityStrNameWithDoubleStringParam: ReplaceAll;

strUtilityStrNameWithSingleStringParamAndSingleIntParam: SplitAndGet;

strUtilityInt: strUtilityIntNameWithoutParam LeftBracket RightBracket
            | strUtilityIntNameWithSingleStringParam LeftBracket strExpr RightBracket;

strUtilityIntNameWithoutParam: Len;

strUtilityIntNameWithSingleStringParam: IndexOf;

strUtilityBool: strUtiltiyBoolNameWithoutParam LeftBracket RightBracket;

strUtiltiyBoolNameWithoutParam: IsLowercase | IsUppercase;

////////////// Number ///////////
allInt: INT | Minus INT;

////////////// Operator //////////////
size: Size;

index: LeftMidBracket INT RightMidBracket;

boolOperator: Eq
            | Neq
            ;

numOperator: Gt
           | Lt
           | Gte
           | Lte
           | Eq
           | Neq
           ;

strOperator: Gt
           | Lt
           | Gte
           | Lte
           | Eq
           | Neq
           | StartWith
           | NotStartWith
           | EndWith
           | NotEndWith
           | Contain
           | NotContain
           | Match
           | NotMatch
           ;

collectionOperator: Contain
                  | NotContain
                  ;

hasOperator: Contain
           | NotContain
           | In
           | NotIn;

nullOperator: Eq
            | Neq
            ;

isOperator: Is
          | IsNot
          ;

////////////// Other //////////////
rootNodeAttr: (Node | NodeAttr) (Point NodeAttr)* (Point collectionNodeAttr)? (As alias | alias)?;
alias: ALIAS;
stepName: ALIAS;

comment: MultiLineComment
        | OneLineComment;

direction: PrevDfg
            | NextDfg
            | PrevCfg
            | NextCfg;

presence: Contain
        | NotContain;