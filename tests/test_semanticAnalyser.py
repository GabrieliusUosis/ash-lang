import pytest
from antlr4 import InputStream, CommonTokenStream
from grammar.AutomataLexer import AutomataLexer
from grammar.AutomataParser import AutomataParser
from src.SemanticAnalyser import SemanticAnalyser, SemanticError
from src.models import Transition
from antlr4.error.ErrorListener import ErrorListener

class StrictErrorListener(ErrorListener):
    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        raise SyntaxError(f"Syntax error at line {line}:{column} - {msg}")

def get_parse_tree(source_code: str):
    """Helper to generate a parse tree from a string snippet."""
    stream = InputStream(source_code)
    
    lexer = AutomataLexer(stream)
    lexer.removeErrorListeners()
    lexer.addErrorListener(StrictErrorListener())
    
    token_stream = CommonTokenStream(lexer)
    
    parser = AutomataParser(token_stream)
    parser.removeErrorListeners()
    parser.addErrorListener(StrictErrorListener())
    
    return parser.program()

def test_dfa_states_extraction():
    code = """
    dfa M1 { 
        states: q0, q1, q2 
        start: q0
    }
    """
    tree = get_parse_tree(code)
    analyzer = SemanticAnalyser()
    analyzer.visit(tree)

    assert "M1" in analyzer.machines
    machine = analyzer.machines["M1"]
    assert machine.machine_type == "DFA"
    assert machine.name == "M1"
    assert machine.states == ["q0", "q1", "q2"]

def test_dfa_full_properties_extraction():
    code = """
    dfa M2 { 
        states: q0, q1, q2 
        alphabet: "a", "b"
        start: q0
        accept: q2
    }
    """
    tree = get_parse_tree(code)
    analyzer = SemanticAnalyser()
    analyzer.visit(tree)

    machine = analyzer.machines["M2"]
    assert machine.states == ["q0", "q1", "q2"]
    assert machine.alphabet == ["a", "b"]
    assert machine.start == "q0"
    assert machine.accept == ["q2"]

def test_dfa_validation_invalid_start_state():
    code = """
    dfa M_Error { 
        states: q0, q1 
        start: q99
    }
    """
    tree = get_parse_tree(code)
    analyzer = SemanticAnalyser()
    
    with pytest.raises(SemanticError, match="Start state 'q99' is not declared"):
        analyzer.visit(tree)

def test_dfa_validation_invalid_transition_symbol():
    code = """
    dfa M_Error2 { 
        states: q0, q1 
        alphabet: "a"
        start: q0
        transitions: {
            q0 -> q1: "b"
        }
    }
    """
    tree = get_parse_tree(code)
    analyzer = SemanticAnalyser()
    
    with pytest.raises(SemanticError, match="Transition symbol 'b' is not in the declared alphabet"):
        analyzer.visit(tree)

def test_duplicate_machine_rejection():
    code = """
    dfa M1 { states: q0 \n start: q0 }
    dfa M1 { states: q1 \n start: q1 }
    """
    tree = get_parse_tree(code)
    analyzer = SemanticAnalyser()
    
    with pytest.raises(SemanticError, match="Duplicate machine declaration: 'M1'"):
        analyzer.visit(tree)

def test_dfa_transitions_extraction():
    code = """
    dfa M3 {
        states: q0, q1, q2
        alphabet: "a", "b"
        start: q0
        transitions: {
            q0 -> q1: "a"
            q1 -> q2: "b"
        }
    }
    """
    tree = get_parse_tree(code)
    analyzer = SemanticAnalyser()
    analyzer.visit(tree)

    machine = analyzer.machines["M3"]
    assert len(machine.transitions) == 2
    assert machine.transitions[0] == Transition(source="q0", symbol="a", target="q1")
    assert machine.transitions[1] == Transition(source="q1", symbol="b", target="q2")

def test_nfa_extraction_and_validation():
    code = """
    nfa N1 { 
        states: q0, q1
        alphabet: "a", "b"
        start: q0
        accept: q1
        transitions: {
            q0 -> q0: "a"
            q0 -> q1: "a"
        }
    }
    """
    tree = get_parse_tree(code)
    analyzer = SemanticAnalyser()
    analyzer.visit(tree)

    machine = analyzer.machines["N1"]
    assert machine.machine_type == "NFA"
    assert len(machine.transitions) == 2

def test_regex_extraction():
    code = "regex R1 = (a|b)*"
    tree = get_parse_tree(code)
    analyzer = SemanticAnalyser()
    analyzer.visit(tree)

    regex_data = analyzer.machines["R1"]
    assert regex_data.machine_type == "REGEX"
    assert regex_data.expression == "(a|b)*"

def test_dfa_duplicate_state_rejection():
    code = """
    dfa M_DupState { 
        states: q0, q1, q0
    }
    """
    tree = get_parse_tree(code)
    analyzer = SemanticAnalyser()
    with pytest.raises(SemanticError, match="Duplicate state declared: 'q0'"):
        analyzer.visit(tree)

def test_dfa_determinism_violation():
    code = """
    dfa M_NonDet { 
        states: q0, q1, q2
        alphabet: "a"
        start: q0
        transitions: {
            q0 -> q1: "a"
            q0 -> q2: "a"
        }
    }
    """
    tree = get_parse_tree(code)
    analyzer = SemanticAnalyser()
    with pytest.raises(SemanticError, match="DFA determinism violation"):
        analyzer.visit(tree)

def test_dfa_missing_start_state():
    code = """
    dfa M_NoStart { 
        states: q0
        alphabet: "a"
    }
    """
    tree = get_parse_tree(code)
    analyzer = SemanticAnalyser()
    with pytest.raises(SemanticError, match="Machine is missing a start state"):
        analyzer.visit(tree)

def test_dfa_missing_states_rejection():
    code = """
    dfa M_NoStates {
        alphabet: "a"
        start: q0
    }
    """
    tree = get_parse_tree(code)
    analyzer = SemanticAnalyser()
    with pytest.raises(SemanticError, match="Machine must declare at least one state"):
        analyzer.visit(tree)

def test_duplicate_alphabet_symbol_rejection():
    code = """
    dfa M_DupAlpha {
        states: q0
        alphabet: "a", "b", "a"
        start: q0
    }
    """
    tree = get_parse_tree(code)
    analyzer = SemanticAnalyser()
    with pytest.raises(SemanticError, match="Duplicate alphabet symbol declared: 'a'"):
        analyzer.visit(tree)

def test_multiple_start_states_rejection():
    code = """
    dfa M_MultiStart {
        states: q0, q1
        start: q0
        start: q1
    }
    """
    tree = get_parse_tree(code)
    analyzer = SemanticAnalyser()
    with pytest.raises(SemanticError, match="Multiple start states declared"):
        analyzer.visit(tree)

def test_duplicate_accept_state_rejection():
    code = """
    dfa M_DupAccept {
        states: q0, q1
        start: q0
        accept: q1, q1
    }
    """
    tree = get_parse_tree(code)
    analyzer = SemanticAnalyser()
    with pytest.raises(SemanticError, match="Duplicate accept state declared: 'q1'"):
        analyzer.visit(tree)

def test_undeclared_accept_state_rejection():
    code = """
    dfa M_BadAccept {
        states: q0, q1
        start: q0
        accept: q2
    }
    """
    tree = get_parse_tree(code)
    analyzer = SemanticAnalyser()
    with pytest.raises(SemanticError, match="Accept state 'q2' is not declared in states list"):
        analyzer.visit(tree)

def test_undeclared_transition_source_rejection():
    code = """
    dfa M_BadSource {
        states: q0, q1
        alphabet: "a"
        start: q0
        transitions: {
            q9 -> q1: "a"
        }
    }
    """
    tree = get_parse_tree(code)
    analyzer = SemanticAnalyser()
    with pytest.raises(SemanticError, match="Transition source 'q9' is not declared in states list"):
        analyzer.visit(tree)

def test_undeclared_transition_target_rejection():
    code = """
    dfa M_BadTarget {
        states: q0, q1
        alphabet: "a"
        start: q0
        transitions: {
            q0 -> q9: "a"
        }
    }
    """
    tree = get_parse_tree(code)
    analyzer = SemanticAnalyser()
    with pytest.raises(SemanticError, match="Transition target 'q9' is not declared in states list"):
        analyzer.visit(tree)

def test_flexible_property_ordering():
    code = """
    dfa M_Reordered {
        transitions: {
            q0 -> q1: "a"
        }
        accept: q1
        start: q0
        alphabet: "a"
        states: q0, q1
    }
    """
    tree = get_parse_tree(code)
    analyzer = SemanticAnalyser()
    analyzer.visit(tree)

    machine = analyzer.machines["M_Reordered"]
    assert machine.start == "q0"
    assert machine.accept == ["q1"]
    assert len(machine.transitions) == 1

def test_multi_machine_program_loading():
    code = """
    dfa D1 {
        states: s0, s1
        alphabet: "0"
        start: s0
        accept: s1
        transitions: { s0 -> s1: "0" }
    }
    nfa N1 {
        states: q0, q1
        alphabet: "a"
        start: q0
        accept: q1
        transitions: {
            q0 -> q0: "a"
            q0 -> q1: "a"
        }
    }
    regex R1 = "0"* "1"+
    """
    tree = get_parse_tree(code)
    analyzer = SemanticAnalyser()
    analyzer.visit(tree)

    assert set(analyzer.machines.keys()) == {"D1", "N1", "R1"}
    assert analyzer.machines["D1"].machine_type == "DFA"
    assert analyzer.machines["N1"].machine_type == "NFA"
    assert analyzer.machines["R1"].machine_type == "REGEX"

def test_cross_type_duplicate_name_rejection():
    code_dfa_nfa = """
    dfa SharedName { states: q0 start: q0 }
    nfa SharedName { states: q1 start: q1 }
    """
    with pytest.raises(SemanticError, match="Duplicate machine declaration: 'SharedName'"):
        SemanticAnalyser().visit(get_parse_tree(code_dfa_nfa))

    code_dfa_regex = """
    dfa SharedName { states: q0 start: q0 }
    regex SharedName = a*
    """
    with pytest.raises(SemanticError, match="Duplicate declaration: 'SharedName'"):
        SemanticAnalyser().visit(get_parse_tree(code_dfa_regex))

    code_regex_dfa = """
    regex SharedName = a*
    dfa SharedName { states: q0 start: q0 }
    """
    with pytest.raises(SemanticError, match="Duplicate machine declaration: 'SharedName'"):
        SemanticAnalyser().visit(get_parse_tree(code_regex_dfa))

def test_dfa_converging_and_multi_symbol_transitions_allowed():
    code = """
    dfa Converging {
        states: q0, q1, q2
        alphabet: "a", "b"
        start: q0
        accept: q2
        transitions: {
            q0 -> q2: "a"
            q0 -> q2: "b"
            q1 -> q2: "a"
        }
    }
    """
    tree = get_parse_tree(code)
    analyzer = SemanticAnalyser()
    analyzer.visit(tree)
    assert len(analyzer.machines["Converging"].transitions) == 3

def test_dfa_self_loop_and_branch_same_symbol_violation():
    code = """
    dfa BadSelfLoop {
        states: q0, q1
        alphabet: "a"
        start: q0
        transitions: {
            q0 -> q0: "a"
            q0 -> q1: "a"
        }
    }
    """
    with pytest.raises(SemanticError, match="DFA determinism violation"):
        SemanticAnalyser().visit(get_parse_tree(code))

def test_nfa_enforces_state_and_alphabet_integrity():
    bad_nfa_state = """
    nfa BadNFA1 {
        states: q0
        alphabet: "a"
        start: q0
        transitions: { q0 -> q_missing: "a" }
    }
    """
    with pytest.raises(SemanticError, match="Transition target 'q_missing' is not declared"):
        SemanticAnalyser().visit(get_parse_tree(bad_nfa_state))

    bad_nfa_symbol = """
    nfa BadNFA2 {
        states: q0, q1
        alphabet: "a"
        start: q0
        transitions: { q0 -> q1: "z" }
    }
    """
    with pytest.raises(SemanticError, match="Transition symbol 'z' is not in the declared alphabet"):
        SemanticAnalyser().visit(get_parse_tree(bad_nfa_symbol))

@pytest.mark.parametrize("malformed_code", [
    "dfa MissingBrace { states: q0 start: q0",
    "dfa BadArrow { states: q0, q1 alphabet: \"a\" start: q0 transitions: { q0 => q1: \"a\" } }",
    "dfa MissingColon { states q0 start: q0 }",
    "regex UnclosedParen = (a | b",
    "dfa TrailingCommaStates { states: q0, q1, start: q0 }",
    "dfa TrailingCommaAlphabet { states: q0 alphabet: \"a\", start: q0 }",
    "dfa EmptyStatesList { states: start: q0 }",
    "dfa EmptyAcceptList { states: q0 start: q0 accept: }",
    "dfa KeywordAsState { states: start, q1 start: q1 }",
    "dfa KeywordAsName states { states: q0 start: q0 }",
    "dfa states { states: q0 start: q0 }",
])
def test_strict_syntax_error_listener_rejects_malformed_code(malformed_code):
    with pytest.raises(SyntaxError):
        get_parse_tree(malformed_code)

def test_empty_and_comment_only_program_loads_zero_machines():
    for code in ["", "   \n\t  ", "// empty program\n// just comments"]:
        analyzer = SemanticAnalyser()
        analyzer.visit(get_parse_tree(code))
        assert analyzer.machines == {}

def test_minimal_dfa_without_accept_or_transitions():
    code = """
    dfa Minimal {
        states: q0
        start: q0
    }
    """
    analyzer = SemanticAnalyser()
    analyzer.visit(get_parse_tree(code))
    machine = analyzer.machines["Minimal"]
    assert machine.states == ["q0"]
    assert machine.alphabet == []
    assert machine.accept == []
    assert machine.transitions == []

def test_empty_transitions_block_is_valid():
    code = """
    dfa NoEdges {
        states: q0, q1
        alphabet: "0", "1"
        start: q0
        accept: q1
        transitions: { }
    }
    """
    analyzer = SemanticAnalyser()
    analyzer.visit(get_parse_tree(code))
    assert analyzer.machines["NoEdges"].transitions == []

def test_dfa_duplicate_identical_transition_rejected():
    code = """
    dfa DupTransition {
        states: q0, q1
        alphabet: "a"
        start: q0
        transitions: {
            q0 -> q1: "a"
            q0 -> q1: "a"
        }
    }
    """
    with pytest.raises(SemanticError, match="DFA determinism violation"):
        SemanticAnalyser().visit(get_parse_tree(code))

def test_escaped_alphabet_and_transition_symbols_unescaped_properly():
    code = r"""
    dfa Escapes {
        states: q0, q1, q2
        alphabet: "\"", "\\", "\n"
        start: q0
        accept: q2
        transitions: {
            q0 -> q1: "\""
            q1 -> q2: "\\"
            q2 -> q2: "\n"
        }
    }
    """
    analyzer = SemanticAnalyser()
    analyzer.visit(get_parse_tree(code))
    machine = analyzer.machines["Escapes"]
    assert machine.alphabet == ['"', '\\', '\n']
    assert machine.transitions[0].symbol == '"'
    assert machine.transitions[1].symbol == '\\'
    assert machine.transitions[2].symbol == '\n'

def test_regex_operator_precedence_in_parse_tree():
    tree = get_parse_tree("regex R = a | b c*")
    parser = AutomataParser(CommonTokenStream(AutomataLexer(InputStream("regex R = a | b c*"))))
    lisp_tree = tree.toStringTree(recog=parser)
    assert "(regexExpr (regexExpr a) | (regexExpr (regexExpr b) (regexExpr (regexExpr c) *)))" in lisp_tree

def test_semantic_analyser_cleans_up_current_machine_on_error():
    bad_code = """
    dfa Broken {
        states: q0
        start: missing
    }
    """
    analyzer = SemanticAnalyser()
    with pytest.raises(SemanticError):
        analyzer.visit(get_parse_tree(bad_code))
    assert analyzer.current_machine is None

    good_code = """
    dfa Healthy {
        states: q0
        start: q0
    }
    """
    analyzer.visit(get_parse_tree(good_code))
    assert "Healthy" in analyzer.machines
    assert "Broken" not in analyzer.machines
