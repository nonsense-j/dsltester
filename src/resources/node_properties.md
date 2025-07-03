### Explanations of DSL nodes and corresponding properties to better understand checkers in DSL formats

#### 基础节点

- annotation: 注解. 2 supported properties: name(名称, value type is 字符串), annoMembers(注解的注解项, value type is annomember节点集合).
- annoMember: 注解项. 2 supported properties: name(名称, value type is 字符串), annoValue(注解项的具体值, value type is literal、enumConstantAccess、fieldAcccess节点).
- recordDeclaration: 类/接口声明. 8 supported properties: name(类名，包含包名, value type is 字符串), comments(注释, value type is comment节点集合), kind(类类型，可能是interface或class, value type is 字符串), superTypes(所有直接和间接集成的父类和接口, value type is recordDeclartion节点集合), directSuperTypes(直接集成的父类和接口, value type is recordDeclartion节点集合), definedFields(类中定义的所有字段, value type is fieldDeclaration节点集合), definedConstructors(类中定义的所有构造方法, value type is functionCall节点集合), definedMethods(类中定义的所有方法, value type is functionCall节点集合).
- anonymousInnerClassExpression: 匿名内部类表达式. 2 supported properties: name(, value type is 字符串), anonymousClassBody(, value type is 任意节点集合).
- arrayAccess: 数组访问表达式. 4 supported properties: arrayIndex(, value type is literal、任意access类节点、functionCall节点等), base(, value type is variableAccess等任意access类节点、functionCall节点等), rootBase(, value type is variableAccess等任意access类节点、functionCall节点等), type(, value type is objectType节点).
- arrayCreationExpression: 数组创建表达式. 4 supported properties: dimensions(数组的维度集合, value type is 节点集合), dimensions[](数组的维度, value type is numLiteral、access类节点、functionCall节点等), initArray(数组创建的初始化值, value type is initArrayExpression), type(数组创建的类型, value type is objectType节点).
- initArrayExpression: 初始化数组表达式. 2 supported properties: elements(数组初始化包含的元素集合, value type is 节点集合), elements[](数组初始化的元素, value type is literal类节点、变量类).
- functionDeclaration: 方法声明. 17 supported properties: name(方法名, value type is 字符串), isConstructor(是否构造函数, value type is 布尔值), hasBody(是否有方法体, value type is 布尔值), comments(方法的注释, value type is comments节点), type(返回值的类型, value type is objectType节点), functionUsages(调用了该方法的位置, value type is functionCall节点集合), callers(调用了该方法的位置所在方法声明, value type is functionDeclaration节点集合), assignStatements(方法体中的所有assignStatement节点, value type is assignStatement节点集合), fieldAccesses(方法体中的所有fieldAccesses节点, value type is fieldAccesses节点集合), functionCalls(方法体中的所有functionCall节点, value type is functionCall节点集合), ifBlocks(方法体中的所有ifBlock节点, value type is ifBlock节点集合), loopBlocks(方法体中的所有loopBlock节点, value type is loopBlock节点集合), parameters(方法体中的所有parameterDeclaration节点, value type is parameterDeclaration节点集合), returnStatements(方法体中的所有returnStatement节点, value type is returnStatement节点集合), variableAccesses(方法体中的所有variableAccess节点, value type is variableAccess节点集合), subMethods(所有重写了该方法的子类方法, value type is functionDecalration节点集合), superMethods(该方法重写的父类方法, value type is functionDecalration节点集合).
- paramDeclaration: 参数声明，方法定义中的参数定义. 2 supported properties: name(参数的名字, value type is 字符串), type(参数的类型, value type is objectType节点).
- functionCall: 方法调用. 7 supported properties: name(方法名, value type is 字符串), function(调用的方法, value type is functionDeclaration节点), possibleFunctions(调用的方法及其重写与被重写的方法，用于多态类创建对象时，声明类型为父类，实例化类型为子类型，调用对象方法时function属性应定位到子类的方法中，但实际会定位到父类方法中，用此属性规避这种问题导致的漏报, value type is functionDeclaration节点), base(直接调用者, value type is valueAccess类节点、functionCall节点等), rootBase(根调用者, value type is valueAccess类节点、functionCall节点等), arguments(入参集合, value type is valueAccess类节点、functionCall节点等的集合), arguments[n](第n个入参, value type is valueAccess类节点、functionCall节点等的集合).
- argument: 函数入参. 3 supported properties: name(参数名, value type is 字符串), argumentIndex(参数的index, value type is 数值), argumentHolder(使用该参数的方法调用, value type is functionCall节点).
- methodReferenceExpression: 方法引用表达式. 3 supported properties: name(方法名, value type is 字符串), function(调用的方法, value type is functionDeclaration节点), type(方法返回值类型, value type is objectType节点).
- objectCreationExpression: 对象创建表达式. 5 supported properties: name(方法名, value type is 字符串), type(返回值类型, value type is objectType节点), function(调用的构造方法, value type is functionDeclaration节点), arguments(入参集合, value type is valueAccess类节点、functionCall节点等的集合), arguments[n](第n个入参, value type is valueAccess类节点、functionCall节点等的集合).
- assignStatement: 赋值语句，同时也是二元表达式. 2 supported properties: lhs(赋值语句的左值, value type is valueAccess类节点), rhs(赋值语句的右值, value type is literal类节点、valueAccess类节点、functionCall类节点).
- binaryOperation: 二元表达式，包括 +、-、*、/运算、=赋值运算等. 4 supported properties: lhs(二元表达式的左值, value type is literal类节点、valueAccess类节点、functionCall类节点), operator(二元表达式的操作符, value type is 字符串), rhs(二元表达式的右值, value type is literal类节点、valueAccess类节点、functionCall类节点), operands(二元表达的操作对象（左值和右值）, value type is 节点集合).
- castExpression: 强制类型转换. 2 supported properties: castType(目标类型, value type is node), operand(操作对象, value type is node).
- fieldDeclaration: 字段定义（声明）. 4 supported properties: name(字段名, value type is 字符串), comments(注释, value type is comment节点集合), initializer(初始化值, value type is 任意节点), valueUsages(使用该字段的节点, value type is valueAccess类节点、functionCall节点等).
- fieldAccess: 字段（成员变量）访问. 3 supported properties: name(字段名, value type is 字符串), field(字段定义, value type is fieldDeclaration节点), base(访问者, value type is 任意节点).
- enumDeclaration: 枚举类声明. 4 supported properties: name(枚举全类名, value type is 字符串), definedFields(定义的所有字段, value type is fieldDeclaration节点集合), definedMethods(定义的所有方法, value type is functionDeclaration节点集合), enumConstants(定义的所有枚举常量, value type is enumConstant节点集合).
- enumConstantDeclaration: 枚举常量声明， 枚举类中用逗号分隔的常量. 4 supported properties: name(枚举常量名, value type is 字符串), definedEnumConstantFields(枚举常量中定义的所有字段, value type is fieldDeclaration节点的集合), definedEnumConstantMethods(枚举常量中定义的所有方法, value type is functionDeclaration节点的集合), enumConstantArguments(枚举常量中的入参, value type is literal节点、valueAccess类节点、functionCall节点等的集合).
- enumConstantAccess: 枚举常量访问. 3 supported properties: name(枚举常量名, value type is 字符串), enumConstant(访问的枚举常量所在声明, value type is enumConstant节点), base(访问者, value type is 任意节点).
- exceptionBlock: 异常捕捉代码块，包括tryBlock、catchBlock、finallyBlock. 3 supported properties: tryBlock(try语句块, value type is tryBlock节点), catchBlocks(所有的catch语句块, value type is catchBlock节点的集合), finallyBlock(finally语句块, value type is finallyBlock节点).
- tryBlock: try语句块.
- catchBlock: catch语句块. 1 supported properties: parameters(, value type is node list).
- finallyBlock: finally代码块.
- tryWithResources: tryWithResources异常捕捉代码块. 4 supported properties: tryBlock(try语句块, value type is tryBlock节点), catchBlocks(所有的catch语句块, value type is catchBlock节点的集合), finallyBlock(finally语句块, value type is finallyBlock节点), resources(任意节点, value type is 若干statements节点的集合).
- throwStatement: throw语句，异常抛出语句. 1 supported properties: operand(, value type is node).
- forBlock: for循环代码块. 4 supported properties: initialization(变量初始化, value type is variableDeclaration、 variableAccess节点), condition(循环条件, value type is binaryOperation), iteration(迭代操作, value type is unaryOperation节点), body(循环体, value type is body语句块).
- forEachBlock: forEach循环代码块. 3 supported properties: variable(循环变量, value type is variableDeclaration节点), iterable(被循环的变量, value type is 任意节点), body(循环体, value type is body语句块).
- whileBlock: while循环语句块. 2 supported properties: condition(循环条件, value type is 任意节点), body(循环体, value type is body语句块).
- doWhileBlock: do…while语句块. 2 supported properties: condition(循环条件, value type is 任意节点), body(循环体, value type is body语句块).
- loopBlock: 循环语句块，包括forBlock, forEachBlock, doWhileBlock, whileBlock. 2 supported properties: body(循环体, value type is body语句块), condition(循环条件, value type is 任意节点).
- ifBlock: if语句块. 3 supported properties: condition(if条件, value type is binaryOperation节点), thenBlock(if条件为true执行的语句, value type is block语句块), elseBlock(if条件为false执行的语句, value type is block语句块).
- thenBlock: then语句块，if 条件成立后执行.
- elseBlock: else语句块.
- importDeclaration: import声明. 2 supported properties: name(import的类名, value type is 字符串), isStatic(import是否为静态, value type is 布尔值).
- instanceofExpression: 类型判断表达式. 2 supported properties: lhs(左值, value type is 任意节点), rhs(右值，类型值, value type is 全类名常量).
- lambdaExpression: lambda表达式. 2 supported properties: parameters(参数, value type is paramDeclaration节点), body(方法体, value type is block语句块).
- literal: 常量，包括字符串、布尔、数字常量. 1 supported properties: value(常量值, value type is 字符串、数值、布尔值等).
- stringLiteral: 字符串常量. 2 supported properties: length(字符串长度, value type is 数值), value(字符串值, value type is 字符串).
- boolLiteral: 布尔常量. 1 supported properties: value(布尔值, value type is 布尔值).
- numLiteral: 数字常量. 1 supported properties: value(数值, value type is 数值).
- returnStatement: return语句. 1 supported properties: returnValue(返回值, value type is 任意节点).
- breakStatement: break语句.
- continueStatement: continue语句.
- staticBlock: 静态语句块.
- switchBlock: Switch语句块. 1 supported properties: selector(switch语句的判断条件, value type is 任意节点).
- caseStatement: case语句块.
- defaultStatement: default语句块.
- synchronizedBlock: 同步代码块. 2 supported properties: lock(锁, value type is 任意节点), body(执行语句, value type is block语句块).
- ternaryOperation: 条件表达式/三目运算. 3 supported properties: condition(三目运算的判断条件, value type is binaryOperation), thenExpression(三目运算条件为真的操作, value type is 任意节点), elseExpression(三目运算条件为假的操作, value type is 任意节点).
- unaryOperation: 一元表达式. 3 supported properties: isPrefix(是否运算符前置, value type is 布尔值), operand(操作对象, value type is 任意节点), operator(运算符, value type is 字符串).
- variableAccess: 变量访问. 2 supported properties: name(变量名, value type is 字符串), variable(被访问的变量的定义, value type is variableDeclaration).
- variableDeclaration: 变量声明. 3 supported properties: name(变量名, value type is 字符串), initializer(初始化值, value type is 任意节点), valueUsages(使用该变量的所有位置, value type is 任意节点).
- comment: 注释，包括行注释、块注释、javaDoc注释. 2 supported properties: content(注释的内容, value type is 字符串), commentedNode(被注释的节点, value type is 节点).
- lineComment: 行注释. 2 supported properties: content(注释的内容, value type is 字符串), commentedNode(被注释的节点, value type is 节点).
- blockComment: 块注释. 2 supported properties: content(注释的内容, value type is 字符串), commentedNode(被注释的节点, value type is 节点).
- javadocComment: javadoc注释. 2 supported properties: content(注释的内容, value type is 字符串), commentedNode(被注释的节点, value type is 节点).

#### 类型节点

- type: 类型节点，是AST节点的通用属性，表示一个变量、字段、方法返回值等的类型，变量声明的类型按”=“左边的声明类型算类型. 3 supported properties: name(类型的名称（包含包名的全类型）
int
String, value type is 字符串), definition(类型的定义, value type is recordDeclaration节点), superTypes(类型的父类型, value type is type节点).
- arrayType: 数组类型，继承于type节点. 3 supported properties: name(数组类型的名称, value type is 字符串), dimension(数组的维度大小, value type is 数字), baseType(数组类型的基础类型, value type is objectType节点).
- objectType: 对象类型，包括类、接口类、枚举类、泛型类，继承与objectType节点. 7 supported properties: name(类型的名称（包含包名的全类型）, value type is 名称), isBounded(泛型类型是否 extends/super 了另一个类, 仅对泛型类型生效, value type is 布尔值), boundedOperator(泛型类型绑定符号是"extends" 或 "super", 仅对泛型类型生效, value type is 字符串), genericBoundedType(泛型类型绑定的类型, value type is type节点), generics(类型的直接泛型类, value type is type节点集合), allGenerics(类型的所有直接+间接泛型类, value type is type节点集合), terminalGenerics(类型的末端泛型类, value type is node list).

