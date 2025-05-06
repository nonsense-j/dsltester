lexer grammar HornLexer;

////////// Identifier ///////////
Point: '.';
Comma: ',';
Colon: ':';
Semicolon: ';';
Equal: '=';
LeftBracket:'(';
RightBracket:')';
LeftMidBracket:'[';
RightMidBracket:']';
LeftCurlyBracket: '{';
RightCurlyBracket: '}';
Satisfy: 'where' | 'if';
Remove: 'remove';
As: 'as';

True: 'true';
False: 'false';

Condition: 'validFunction';
////////// Operator ////////////
Gt: '>';
Gte: '>=';
Lt: '<';
Lte: '<=';
Eq: '==';
Neq: '!=';
Contain: 'contain';
NotContain: 'notContain';
Match: 'match';
NotMatch: 'notMatch';
StartWith: 'startWith';
NotStartWith: 'notStartWith';
EndWith: 'endWith';
NotEndWith: 'notEndWith';
In: 'in';
NotIn: 'notIn';
Is: 'is';
IsNot: 'isnot';
BooleanNot: '!';
Size: 'size()' | 'length()';
// TODO 支持节点.属性.exist()

OR: 'or';
AND: 'and';
NOT: 'not';

/////////// String-Utility-String ////////
ToUpperCase: 'toUpperCase';
ToLowerCase: 'toLowerCase';
Capitalize: 'capitalize';
Substring: 'substring';
ReplaceAll: 'replaceAll';
SplitAndGet: 'splitAndGet';
ShortName: 'shortName';
Trim: 'trim';

/////////// String-Utility-Int ////////
Len: 'len';
IndexOf: 'indexOf';

/////////// String-Utility-Boolean ////////
IsLowercase: 'isLowerCase';
IsUppercase: 'isUpperCase';

/////////// ConfigRule /////////
ConfigLabel: '@ConfigRule';
PreciseMatch: 'PreciseMatch';
Properties: 'Properties';
XpathMatchExpression: 'XpathMatchExpr';
FileName: 'FileName';
PropertyKey: 'PropertyName' | 'PropertiesName';
PropertyValue: 'PropertyValue' | 'PropertiesValue';

/////////// Taint Info /////////
SourceLabel: '@Source';
SinkLabel: '@Sink';
PassthroughLabel: '@Passthrough';
CleanseLabel: '@Cleanse';
Path: '@path';
InArgs: 'InArgs';
OutArgs: 'OutArgs';
Flag: 'TaintFlags';
Return: 'return';
This: 'this';
Plus: '+';
Star: '*';
Minus: '-';
Divide: '/';
Dollar: '$';
PrevDfg: 'prevDfg';
NextDfg: 'nextDfg';
PrevCfg: 'prevCfg';
NextCfg: 'nextCfg';
Until: 'until';
Depth: 'depth';

/////////// RuleMessageInfo //////////
RuleSetMessageLabel: '@RuleSetMessage';
RuleSetName: 'RuleSetName' | 'Checker';
Version: 'Version';
ReportMsg: 'ReportMsg' | 'Description';

Language: 'Language';
Java: 'JAVA' | 'Java';
Python: 'PYTHON' | 'Python';
CPP: 'CPP' | 'Cpp' | 'Cxx' | 'CXX';
C: 'C';
ArkTs: 'ARKTS' | 'ArkTs';
TypeScript: 'TYPESCRIPT' | 'Typescript';
JavaScript: 'JAVASCRIPT' | 'Javascript';

Type: 'Type';
Taint: 'Taint';
Structural: 'Structural';

Engine: 'Engine';
Cooddy: 'Cooddy' | 'COODDY';
CSA: 'CSA' | 'Csa';
Soot: 'SOOT' | 'Soot';
Cpg: 'CPG' | 'Cpg';

CustomInfo: 'CustomInfo';

RuleMsgLabel: '@RuleMsg';
RuleId: 'RuleId';

/////////// vulnerability //////////
VulnerabilityLabel: '@Vulnerability';
Category: 'Category';
Subcategory: 'Subcategory';
IssueType: 'IssueType';
CWE: 'CWE';
Severity: 'Severity';
Suggest: 'Suggest';
Normal: 'Normal';
Critical: 'Critical';
Fatal: 'Fatal';
Error: 'Error';
Warning: 'Warning';

ImportLabel: '@import';

/////////// Attribute //////////

Node: 'annoMember'
    | 'anyType'
    | 'assertStatement'
    | 'asExpression' // only for Ts, a type of castExpression
    | 'sliceExpression'
    | 'annotation'
    | 'anonymousInnerClassExpression'
    | 'arrayAccess'
    | 'arrayCreationExpression'
    | 'arrayType'
    | 'assignExpression'
    | 'assignStatement'
    | 'binaryOperation'
    | 'boolLiteral'
    | 'regularExpressionLiteral'
    | 'caseStatement'
    | 'catchBlock'
    | 'handler'
    | 'castExpression'
    | 'charLiteral'
    | 'classObject'
    | 'thisExpression'
    | 'constructorDeclaration'
    | 'destructorDeclaration'
    | 'friendDeclaration'
    | 'compoundStatement'
    | 'localClassDeclarationStatement'
    | 'globalStatement'
    | 'gotoStatement'
    | 'labelStatement'
    | 'decorator'
    | 'decorMember'
    | 'defaultStatement'
    | 'packExpansionExpr'
    | 'deleteStatement'
    | 'doWhileBlock'
    | 'emptyStatement'
    | 'enumDeclaration'
    | 'enumConstantDeclaration'
    | 'exceptionBlock'
    | 'fieldAccess'
    | 'enumConstantAccess'
    | 'fieldDeclaration'
    | 'forBlock'
    | 'forEachBlock'
    | 'forOfBlock'  // only for ts
    | 'forInBlock'  // only for ts
    | 'formattedValue'
    | 'functionAccess'
    | 'functionCall'
    | 'memberCall'
    | 'functionDeclaration'
    | 'functionExpression' // only for ts
    | 'functionPointerType'
    | 'functionTemplateDeclaration'
    | 'methodTemplateDeclaration'
    | 'ifBlock'
    | 'importDeclaration'
    | 'initArrayExpression'
    | 'initObjectExpression' // only for Ts
    | 'comprehensionExpression'
    | 'comprehensionGenerator'
    | 'instanceofExpression'
    | 'joinedString'
    | 'keyValueType'
    | 'lambdaExpression'
    | 'literal'
    | 'loopBlock'
    | 'methodDeclaration'
    | 'methodReferenceExpression'
    | 'macroDefinition'
    | 'macroExpansion'
    | 'namespaceAlias'
    | 'namespaceDeclaration'
    | 'newExpression'
    | 'noneType'
    | 'nonLocalStatement'
    | 'nullLiteral'
    | 'numLiteral'
    | 'objectType'
    | 'objectCreationExpression'
    | 'paramDeclaration'
    | 'pointerType'
    | 'listType'
    | 'generatorType'
    | 'setType'
    | 'dictType'
    | 'recordDeclaration'
    | 'structDeclaration'
    | 'recordTemplateDeclaration'
    | 'recordAccess'
    | 'referenceType'
    | 'returnStatement'
    | 'raiseStatement'
    | 'breakStatement'
    | 'continueStatement'
    | 'staticBlock'
    | 'stringLiteral'
    | 'stringBlock'
    | 'switchBlock'
    | 'switchStatement'
    | 'switchExpression'
    | 'synchronizedBlock'
    | 'templateParamDeclaration'
    | 'ternaryOperation'
    | 'throwStatement'
    | 'typedefDeclaration'
    | 'typeAliasDeclaration'
    | 'typeLiteralDeclaration'
    | 'typeParamDeclaration'
    | 'typeofExpression'
    | 'typePatternExpression'
    | 'tryWithResources'
    | 'unaryOperation'
    | 'usingDirective'
    | 'valueAccess'
    | 'valueDeclaration'
    | 'variableAccess'
    | 'variableDeclaration'
    | 'variableDeclarationList' // TS node, contain one or more variable declarations, it could be: let v1, v2;
    | 'withStatement'
    | 'withItem'
    | 'whileBlock'
    | 'argument'
    | 'comment'
    | 'lineComment'
    | 'blockComment'
    | 'javadocComment'
    | 'yieldExpression'
    | 'patternExpression'
    | 'keyValueExpression'
    | 'templateLiteral' // Ts node, be like: `Hello, ${name}!`;
    | 'typeIdExpression' // C++ specific node
    | 'compositeType'   // Ts type, consists of tupleType, unionType, intersectionType
    | 'tupleType'       // Ts type such as: [type1, type2]
    | 'unionType'       // Ts type such as: type1 | type2
    | 'intersectionType'// Ts type such as: type1 & type2
    | 'jsDocComment'
    | 'parenthesisExpression'
    | 'exportExpression'
    | 'exportDefaultExpression'
    | 'awaitExpression'
    | 'generatorFunction'
    | 'classExpression' // Ts/Js-specific: let a = class{xxx}
    | 'moduleMember' // Ts/Js-specific: import/export {xx1, xx2, xx3}
    | 'moduleDeclaration' //Ts namespaceDeclaration and moduleDeclaration
    | 'docTag' // reference to docComment's tag, currently, just for js/ts/arkts'
    | 'debuggerStatement'
    | 'explicitConstructorCall'
    | 'thisCall'
    | 'superCall'
    ;

BoolAttr:  'hasBody'
         | 'isAbstract'
         | 'isArray'
         | 'isAuto'
         | 'isAsync'
         | 'isAwait'
         | 'isBounded'
         | 'isConst'
         | 'isConstExpression'
         | 'isConstructor'
         | 'isConversionMethod'
         | 'isDefault'
         | 'isDefinition'
         | 'isExtern'
         | 'isFinal'
         | 'isImplicit'
         | 'isInline'
         | 'isInterface'
         | 'isMutable'
         | 'isNative'
         | 'isNonTypeTemplateParameter'
         | 'isPartialSpecialization'
         | 'isPostfix'
         | 'isBlock'
         | 'isPrefix'
         | 'isPrivate'
         | 'isProtected'
         | 'isPublic'
         | 'isPureVirtual'
         | 'isRegister'
         | 'isSourceCode'
         | 'isStatic'
         | 'isStarred'
         | 'isSynchronized'
         | 'isTransient'
         | 'isIndirectGoto'
         | 'isGlobal'
         | 'isUnscopedEnum'
         | 'isVirtual'
         | 'isVolatile'
         | 'isConstant'
         | 'isVariadic'
         | 'isOrphan'
         | 'hasInitializer'  // If true for valueDeclaration, indicates it has an initializer
         | 'isExport'
         | 'hasAliasName'
         | 'hasAsterisk'
         | 'hasDefaultKeyword'
         | 'isNamespace'
         | 'isModlue'
         | 'hasEmptyParenthesis'
         | 'hasUnknownTag'
         | 'hasCheckedNull'
         | 'isAllNum'
         ;

NodeAttr: 'addressedBy'
        | 'annoValue'
        | 'arrayIndex'
        | 'anonymousClassBody'
        | 'lower'
        | 'upper'
        | 'step'
        | 'base'
        | 'baseType'
        | 'body'
        | 'typeLiteral'
        | 'fieldDeclarationList'
        | 'nodeList'
        | 'boundedType'
        | 'caseExpression'
        | 'castType'
        | 'cause'
        | 'condition'
        | 'constructor'
        | 'context'
        | 'friendFunction'
        | 'friendRecordRef'
        | 'decorValue'
        | 'decoratorFunctionCall' // Ts only
        | 'definedMemberReference'
        | 'definedNamespace'
        | 'definedType'
        | 'definition'
        | 'elementContainer'
        | 'elseBlock'
        | 'packExpansionPattern'
        | 'elseExpression'
        | 'elt'
        | 'enclosingClass'
        | 'enclosingFunction'
        | 'enclosingNamespace'
        | 'enclosingFor'
        | 'enclosingForEach'
        | 'enclosingWhile'
        | 'enclosingTry'
        | 'enclosingCatch'
        | 'enclosingIf'
        | 'enclosingCompilationUnit'
        | 'enclosingFile'
        | 'enumBaseType'
        | 'exception'
        | 'field'
        | 'formatValue'
        | 'formatSpec'
        | 'localClass'
        | 'enumConstant'
        | 'finallyBlock'
        | 'firstStatement'
        | 'function'
        | 'correspondFunction'
        | 'import'
        | 'initArray'
        | 'initialization'
        | 'initializer'
        | 'iter'
        | 'iterable'
        | 'iteration'
        | 'keyType'
        | 'kv_key'
        | 'kv_value'
        | 'lastStatement'
        | 'lhs'
        | 'lock'
        | 'memberType'
        | 'message'
        | 'operand'
        | 'optional'
        | 'pointTo'
        | 'returnType'
        | 'returnValue'
        | 'yieldValue'
        | 'receiverVariable'
        | 'rhs'
        | 'rootBase'
        | 'selector'
        | 'singleDeclaration'
        | 'target'
        | 'thenBlock'
        | 'thenExpression'
        | 'tryBlock'
        | 'type'
        | 'valueType'
        | 'variable'
        | 'argumentHolder'
        | 'defaultValue'
        | 'gotoLabel'
        | 'labelSubStatement'
        | 'superTypesVarargs'
        | 'commentedNode'
        | 'guard'  // python node statement - condition in case
        | 'pattern'  // python node statement - the match pattern in case
        | 'asName'  // python node declaration - the right part of the ast.matchAs
        | 'aliasType'
        | 'scope'
        | 'definedBy'
        | 'definesScope'
        | 'optimalScope' // The node which presents minimal affordable scope
        ;

NumAttr:  'dimension'
        | 'endColumn'
        | 'endLine'
        | 'startColumn'
        | 'startLine'
        | 'length'
        | 'argumentIndex'
        | 'formatConversion'
        | 'level'
        | 'scopeLevel'
        ;

StrAttr:  'boundedOperator'
        | 'captureBy'
        | 'captureDefault'
        | 'cause'
        | 'code'
        | 'content'
        | 'kind'
        | 'name'
        | 'namespace'
        | 'operator'
        | 'enclosingFunctionName'
        | 'enclosingFunctionSignature'
        | 'enclosingClassName'
        | 'enclosingNamespaceName'
        | 'constantValue'
        | 'keyword'
        | 'declareKeyword'  // TS variable declaration key word
        | 'alias'
        | 'packageName'
        | 'passBy'
        | 'aliasName'
        | 'orderIndex'
        | 'hash'
        ;

ObjPropertyAttr: 'value';

ObjNodeAttr: ;

CollectionBoolAttr:;

CollectionNumAttr:;

CollectionNodeAttr: 'arguments'
                  | 'assignStatements'
                  | 'enumConstantArguments'
                  | 'allGenerics'
                  | 'annotations'
                  | 'annoMembers'
                  | 'callers'
                  | 'captures'
                  | 'catchBlocks'
                  | 'handlers'
                  | 'resources'
                  | 'declarations'
                  | 'decorators'
                  | 'definedConstructors'
                  | 'definedFields'
                  | 'definedFriends'
                  | 'definedMethods'
                  | 'definedEnumConstantFields'
                  | 'definedEnumConstantMethods'
                  | 'dimensions'
                  | 'dimensionValues'
                  | 'directSuperTypes'
                  | 'elements'
                  | 'elementTypes'
                  | 'exceptionTypes'
                  | 'fieldAccesses'
                  | 'functionCalls'
                  | 'functionUsages'
                  | 'generators'
                  | 'genericParams'
                  | 'memberInitializers'
                  | 'generics'
                  | 'ifBlocks'
                  | 'ifs'
                  | 'loopBlocks'
                  | 'operands'
                  | 'parameters'
                  | 'possibleFuncs'
                  | 'realizations'
                  | 'returnStatements'
                  | 'statements'
                  | 'subMethods'
                  | 'superMethods'
                  | 'superTypes'
                  | 'targets'
                  | 'templateParams'
                  | 'terminalGenerics'
                  | 'typeParams'
                  | 'enumConstants'
                  | 'valueUsages'
                  | 'variableAccesses'
                  | 'variables'
                  | 'comments'
                  | 'keywords'
                  | 'imports'
                  | 'records'
                  | 'members'
                  | 'docTags'  // reference to docComment's tag, currently, just for js/ts/arkts
                  ;

CollectionObjAttr:;

CollectionStrAttr: 'modifiers'
                  ;

WarningNode: 'alarmPoint';

NULL: 'null';

WS: [ \t\r\n]+ -> skip;

MultiLineComment: ('/*' .*? '*/') ;
OneLineComment: ('//' .*? '\n')
              | ('//' .*? EOF);

ALIAS: ([a-zA-Z_])+([0-9])*;

STRING: '"'([a-zA-Z0-9]
            | '\\'
            | '\''
            | '\\"'
            | ' '
            | ')'
            | '('
            | CommonChar
            | ChineseWords
            )*'"';

ID: '"'([a-zA-Z0-9]
        | '\\'
        | '\''
        | '"'
        | CommonChar
        )*'"';

CommonChar: '.'
          | '?'
          | '*'
          | '_'
          | '['
          | ']'
          | '|'
          | '{'
          | '%'
          | '@'
          | '}'
          | '+'
          | ';'
          | '$'
          | ','
          | '<'
          | '>'
          | '='
          | '!'
          | '&'
          | '^'
          | '-'
          | '/'
          | '#'
          | '~'
          | ':';

INT: [0] | [1-9][0-9]*;

ChineseWords: '，'
           | '。'
           | '？'
           | '：'
           | '“'
           | '‘'
           | '、'
           | '￥'
           | '；'
           | '……'
           | '！'
           | '【'
           | '】'
           | [\u4E00-\u9FFF]
           ;
