parser grammar AutomataParser;
options { tokenVocab=AutomataLexer; }
program : statement* EOF ;

statement : dfaDeclaration ;
dfaDeclaration : DFA ID LBRACE startDecl RBRACE ;

startDecl : START COLON ID ;
transition : ID ARROW ID COLON STRING ;