lexer grammar AutomataLexer;

//Keywords
DFA         : 'dfa';
NFA         : 'nfa';
REGEX       : 'regex';
ALPHABET    : 'alphabet';
STATES      : 'states';
START       : 'start';
ACCEPT      : 'accept';
TRANSITIONS : 'transitions';

ARROW       : '->';
COLON       : ':';
COMMA       : ',';
LBRACE      : '{';
RBRACE      : '}';
LPAREN      : '(';
RPAREN      : ')';
ASSIGN      : '=';
PIPE        : '|';
STAR        : '*';
PLUS        : '+';
QUESTION    : '?';

ID          : [a-zA-Z_][a-zA-Z0-9_]*;
STRING      : '"' (~["\r\n\\] | '\\' .)* '"';

WS          : [ \t\r\n]+ -> skip;
COMMENT     : '//' ~[\r\n]* -> skip;