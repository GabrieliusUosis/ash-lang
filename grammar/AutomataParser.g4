parser grammar AutomataParser;
options { tokenVocab=AutomataLexer; }

program : statement* EOF ;

// Support for all three machine types outlined in your lexer
statement : dfaDeclaration | nfaDeclaration | regexDeclaration ;

dfaDeclaration : DFA ID LBRACE machineBody RBRACE ;
nfaDeclaration : NFA ID LBRACE machineBody RBRACE ;

// Allow machine properties to be declared in any flexible order
machineBody : property* ;

property : alphabetDecl
         | statesDecl
         | startDecl
         | acceptDecl
         | transitionsBlock ;

// Map directly to your ALPHABET, STATES, START, and ACCEPT tokens
alphabetDecl : ALPHABET COLON stringList ;
statesDecl : STATES COLON idList ;
startDecl : START COLON ID ;
acceptDecl : ACCEPT COLON idList ;

// Group transitions cleanly utilizing your TRANSITIONS token
transitionsBlock : TRANSITIONS COLON LBRACE transition* RBRACE ;
transition : ID ARROW ID COLON STRING ;

// Helper rules for the COMMA token
idList : ID (COMMA ID)* ;
stringList : STRING (COMMA STRING)* ;

// Map to your REGEX and ASSIGN ('=') tokens
regexDeclaration : REGEX ID ASSIGN regexExpr ;

// Regex expression logic utilizing your PLUS, STAR, QUESTION, and PIPE tokens
regexExpr : regexExpr (STAR | PLUS | QUESTION)  // Quantifiers
          | regexExpr regexExpr                 // Concatenation
          | regexExpr PIPE regexExpr            // Alternation
          | LPAREN regexExpr RPAREN             // Grouping
          | STRING                              // Literal matching
          | ID ;                                // Reference to another regex/machine