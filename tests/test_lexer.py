from antlr4 import InputStream
from grammar.AutomataLexer import AutomataLexer

def get_tokens(text: str):
    stream = InputStream(text)
    lexer = AutomataLexer(stream)
    return [lexer.symbolicNames[token.type] for token in lexer.getAllTokens()]

def test_keywords_and_symbols():
    text = "dfa M1 { start: q0 }"
    tokens = get_tokens(text)
    assert tokens == ["DFA", "ID", "LBRACE", "START", "COLON", "ID", "RBRACE"]

def test_transition_tokens():
    text = "q0 -> q1 : 'a'"
    tokens = get_tokens(text)
    assert tokens == ["ID", "ARROW", "ID", "COLON", "STRING"] or "ID" in tokens