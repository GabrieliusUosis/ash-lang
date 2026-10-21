from antlr4 import InputStream
from grammar.AutomataLexer import AutomataLexer

def tokenize(text: str):
    stream = InputStream(text)
    lexer = AutomataLexer(stream)
    return [lexer.symbolicNames[token.type] for token in lexer.getAllTokens()]

def test_keywords_and_symbols():
    text = "dfa M1 { start: q0 }"
    tokens = tokenize(text)
    assert tokens == ["DFA", "ID", "LBRACE", "START", "COLON", "ID", "RBRACE"]

def test_transition_tokens():
    text = 'q0 -> q1 : "a"'
    tokens = tokenize(text)
    assert tokens == ["ID", "ARROW", "ID", "COLON", "STRING"]

def test_machine_properties_tokens():
    sample = """
    dfa M1 {
        states: q0, q1
        alphabet: "a", "b"
        accept: q1
    }
    """
    expected = [
        "DFA", "ID", "LBRACE",
        "STATES", "COLON", "ID", "COMMA", "ID",
        "ALPHABET", "COLON", "STRING", "COMMA", "STRING",
        "ACCEPT", "COLON", "ID",
        "RBRACE"
    ]
    assert tokenize(sample) == expected

def test_transitions_block_tokens():
    sample = """
    transitions: { 
        q0 -> q1: "a" 
    }
    """
    expected = [
        "TRANSITIONS", "COLON", "LBRACE",
        "ID", "ARROW", "ID", "COLON", "STRING",
        "RBRACE"
    ]
    assert tokenize(sample) == expected

def test_regex_declaration_tokens():
    sample = "regex R1 = (a|b)+"
    expected = [
        "REGEX", "ID", "ASSIGN", 
        "LPAREN", "ID", "PIPE", "ID", "RPAREN", "PLUS"
    ]
    assert tokenize(sample) == expected
    
def test_regex_quantifiers_tokens():
    sample = "regex R2 = a?*"
    expected = [
        "REGEX", "ID", "ASSIGN",
        "ID", "QUESTION", "STAR"
    ]
    assert tokenize(sample) == expected