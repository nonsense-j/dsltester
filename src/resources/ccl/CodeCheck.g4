grammar CodeCheck;

/*
================================================================================
Parser Rules
- These rules define the structure (syntax) of your DSL.
- They start with a lowercase letter.
================================================================================
*/

// The entry point of the grammar. A complete check must be a single condition.
check: condition EOF;

// A condition can be any of the logical expressions or a simple atomic one.
// We also allow parentheses for explicit grouping and precedence.
condition
    : logicalExpr
    | LPAREN condition RPAREN
    | atomicCondition
    ;

// Groups all the complex logical structures.
logicalExpr
    : andExpr
    | orExpr
    | notExpr
    | existsExpr
    | forallExpr
    ;

// Matches an 'AND' expression with a list of one or more conditions.
andExpr: AND LBRACE conditionList RBRACE;

// Matches an 'OR' expression with a list of one or more conditions.
orExpr: OR LBRACE conditionList RBRACE;

// Matches a 'NOT' expression with a single nested condition.
notExpr: NOT LBRACE LPAREN condition RPAREN RBRACE;

// Matches an 'EXIST' quantifier with a single-quoted description and a single condition.
existsExpr: EXIST LPAREN DESCRIPTION RPAREN LBRACE LPAREN condition RPAREN RBRACE;

// Matches a 'FORALL' quantifier with a single-quoted description and a single condition.
forallExpr: FORALL LPAREN DESCRIPTION RPAREN LBRACE LPAREN condition RPAREN RBRACE;

/*
--------------------------------------------------------------------------------
Helper Parser Rules
- These rules are used by the main rules above to define recurring patterns.
--------------------------------------------------------------------------------
*/

// Defines a list of one or more parenthesized conditions, separated by commas.
// Example: (cond1), (cond2)
conditionList: LPAREN condition RPAREN (COMMA LPAREN condition RPAREN)*;

// An atomic condition is simply represented by the DESCRIPTION token.
atomicCondition: DESCRIPTION;


/*
================================================================================
Lexer Rules (Tokens)
- These rules define the basic building blocks (keywords, symbols, etc.).
- They start with an uppercase letter.
================================================================================
*/

// Keywords
AND:    'AND';
OR:     'OR';
NOT:    'NOT';
EXIST:  'EXIST';
FORALL: 'FORALL';

// Symbols
LPAREN: '(';
RPAREN: ')';
LBRACE: '{';
RBRACE: '}';
COMMA:  ',';

// This token captures any natural language description inside single quotes.
// It is used for both atomic conditions and quantifier descriptions.
// It also correctly handles escaped single quotes (e.g., 'user\'s input').
DESCRIPTION
    : SQUOTE ( '\\' . | ~['\\] )* SQUOTE
    ;

// This is a helper rule for the lexer and does not create a token on its own.
// It makes the DESCRIPTION rule cleaner.
fragment SQUOTE: '\''; 

// This rule tells the lexer to ignore whitespace (spaces, tabs, newlines).
WS: [ \t\r\n]+ -> skip;