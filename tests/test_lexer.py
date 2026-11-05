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

def test_nfa_declaration_tokens():
    sample = "nfa N_1 { states: s_0, s_1 start: s_0 }"
    expected = [
        "NFA", "ID", "LBRACE",
        "STATES", "COLON", "ID", "COMMA", "ID",
        "START", "COLON", "ID",
        "RBRACE"
    ]
    assert tokenize(sample) == expected

def test_comments_and_whitespace_skipped():
    sample = """
    // Full line comment
    dfa M1 { // Inline comment
        start: q0
    }
    """
    expected = ["DFA", "ID", "LBRACE", "START", "COLON", "ID", "RBRACE"]
    assert tokenize(sample) == expected

def test_escaped_string_tokens():
    sample = r'alphabet: "\"", "\\"'
    expected = ["ALPHABET", "COLON", "STRING", "COMMA", "STRING"]
    assert tokenize(sample) == expected

def test_complex_regex_with_string_literals():
    sample = 'regex HasOddOnes = ("0"* "1")+ | "0"?'
    expected = [
        "REGEX", "ID", "ASSIGN",
        "LPAREN", "STRING", "STAR", "STRING", "RPAREN", "PLUS",
        "PIPE", "STRING", "QUESTION"
    ]
    assert tokenize(sample) == expected
