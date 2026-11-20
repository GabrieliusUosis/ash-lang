import pytest
from antlr4 import InputStream
from antlr4.error.ErrorListener import ErrorListener
from grammar.AutomataLexer import AutomataLexer

class _StrictLexerErrorListener(ErrorListener):
    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        raise SyntaxError(f"Lexer error at {line}:{column} - {msg}")

def tokenize_strict(text: str):
    stream = InputStream(text)
    lexer = AutomataLexer(stream)
    lexer.removeErrorListeners()
    lexer.addErrorListener(_StrictLexerErrorListener())
    return [(lexer.symbolicNames[t.type], t.text) for t in lexer.getAllTokens()]

def tokenize(text: str):
    stream = InputStream(text)
    lexer = AutomataLexer(stream)
    return [lexer.symbolicNames[token.type] for token in lexer.getAllTokens()]

def tokenize_pairs(text: str):
    stream = InputStream(text)
    lexer = AutomataLexer(stream)
    return [(lexer.symbolicNames[t.type], t.text) for t in lexer.getAllTokens()]

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

@pytest.mark.parametrize("identifier", [
    "dfa_1",
    "nfaMachine",
    "regexPattern",
    "states_list",
    "alphabetSet",
    "startState",
    "accept_node",
    "transitionsTable",
    "_leading_underscore",
    "q0_to_q1_99",
    "DFA",
    "NFA",
])
def test_keyword_prefixed_and_cased_identifiers_are_id_tokens(identifier):
    assert tokenize_pairs(identifier) == [("ID", identifier)]

def test_compact_syntax_without_spaces():
    sample = 'dfa M{states:a,b alphabet:"0","1" start:a accept:b transitions:{a->b:"0"}}'
    expected = [
        "DFA", "ID", "LBRACE",
        "STATES", "COLON", "ID", "COMMA", "ID",
        "ALPHABET", "COLON", "STRING", "COMMA", "STRING",
        "START", "COLON", "ID",
        "ACCEPT", "COLON", "ID",
        "TRANSITIONS", "COLON", "LBRACE",
        "ID", "ARROW", "ID", "COLON", "STRING",
        "RBRACE", "RBRACE"
    ]
    assert tokenize(sample) == expected

def test_empty_string_literal_token():
    sample = 'q0 -> q1: ""'
    assert tokenize_pairs(sample) == [
        ("ID", "q0"),
        ("ARROW", "->"),
        ("ID", "q1"),
        ("COLON", ":"),
        ("STRING", '""'),
    ]

def test_strings_containing_keywords_and_operators():
    sample = '"dfa -> states: { | * + ? }"'
    assert tokenize_pairs(sample) == [("STRING", '"dfa -> states: { | * + ? }"')]

def test_deeply_nested_regex_parentheses():
    sample = "regex Deep = (((a|b)*)+)?"
    expected = [
        "REGEX", "ID", "ASSIGN",
        "LPAREN", "LPAREN", "LPAREN",
        "ID", "PIPE", "ID",
        "RPAREN", "STAR",
        "RPAREN", "PLUS",
        "RPAREN", "QUESTION",
    ]
    assert tokenize(sample) == expected

def test_empty_and_whitespace_only_inputs():
    assert tokenize("") == []
    assert tokenize("   \t\r\n  \n ") == []
    assert tokenize("// only a comment with no newline") == []
    assert tokenize("// comment 1\r\n// comment 2\n") == []

@pytest.mark.parametrize("keyword,token_name", [
    ("dfa", "DFA"),
    ("nfa", "NFA"),
    ("regex", "REGEX"),
    ("alphabet", "ALPHABET"),
    ("states", "STATES"),
    ("start", "START"),
    ("accept", "ACCEPT"),
    ("transitions", "TRANSITIONS"),
])
def test_all_reserved_keywords_exact_match(keyword, token_name):
    assert tokenize_pairs(keyword) == [(token_name, keyword)]

def test_unicode_and_whitespace_string_literals():
    sample = 'alphabet: " ", "\\t", "\\n", "α", "β"'
    assert tokenize_pairs(sample) == [
        ("ALPHABET", "alphabet"),
        ("COLON", ":"),
        ("STRING", '" "'),
        ("COMMA", ","),
        ("STRING", r'"\t"'),
        ("COMMA", ","),
        ("STRING", r'"\n"'),
        ("COMMA", ","),
        ("STRING", '"α"'),
        ("COMMA", ","),
        ("STRING", '"β"'),
    ]

@pytest.mark.parametrize("invalid_lexeme", [
    '"unterminated string',
    '"raw\nnewline"',
    'dfa M @ { start: q0 }',
    'dfa M { states: 0q }',
    'dfa M { states: q0; }',
    '$',
])
def test_lexer_rejects_invalid_tokens_and_unterminated_strings(invalid_lexeme):
    with pytest.raises(SyntaxError):
        tokenize_strict(invalid_lexeme)

def test_mixed_regex_ids_strings_and_quantifiers():
    sample = 'regex R = ("0"+ | sub_expr)? "1"*'
    assert tokenize(sample) == [
        "REGEX", "ID", "ASSIGN",
        "LPAREN", "STRING", "PLUS", "PIPE", "ID", "RPAREN", "QUESTION",
        "STRING", "STAR",
    ]

def test_epsilon_token_in_transitions_and_regex():
    assert tokenize_pairs(r"q0 -> q1: \e") == [
        ("ID", "q0"),
        ("ARROW", "->"),
        ("ID", "q1"),
        ("COLON", ":"),
        ("EPSILON", r"\e"),
    ]
    assert tokenize_pairs(r'regex R = "0" | \e') == [
        ("REGEX", "regex"),
        ("ID", "R"),
        ("ASSIGN", "="),
        ("STRING", '"0"'),
        ("PIPE", "|"),
        ("EPSILON", r"\e"),
    ]
