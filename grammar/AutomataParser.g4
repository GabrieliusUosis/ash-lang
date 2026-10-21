parser grammar AutomataParser;
options { tokenVocab=AutomataLexer; }

program : statement* EOF ;

// Support for all three machine types outlined in the lexer
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

// Map directly to the ALPHABET, STATES, START, and ACCEPT tokens
alphabetDecl : ALPHABET COLON stringList ;
statesDecl : STATES COLON idList ;
startDecl : START COLON ID ;
acceptDecl : ACCEPT COLON idList ;

transitionsBlock : TRANSITIONS COLON LBRACE transition* RBRACE ;
transition : ID ARROW ID COLON STRING ;

// Helper rules for the COMMA token
idList : ID (COMMA ID)* ;
stringList : STRING (COMMA STRING)* ;

// Map to the REGEX and ASSIGN ('=') tokens
regexDeclaration : REGEX ID ASSIGN regexExpr ;

// Regex expression logic utilizing the PLUS, STAR, QUESTION, and PIPE tokens
regexExpr : regexExpr (STAR | PLUS | QUESTION)  
          | regexExpr regexExpr                 
          | regexExpr PIPE regexExpr            
          | LPAREN regexExpr RPAREN
          | STRING                             
          | ID ;                                