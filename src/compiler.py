from antlr4 import InputStream
from antlr4.error.ErrorListener import ErrorListener
from grammar.AutomataLexer import AutomataLexer

class StrictErrorListener(ErrorListener):
    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        raise SyntaxError(f"Syntax error at line {line}:{column} - {msg}")

def tokenize_source(source_code: str, strict: bool = False) -> list[tuple[str, str]]:
    lexer = AutomataLexer(InputStream(source_code))
    if strict:
        lexer.removeErrorListeners()
        lexer.addErrorListener(StrictErrorListener())
    return [(lexer.symbolicNames[t.type], t.text) for t in lexer.getAllTokens()]
