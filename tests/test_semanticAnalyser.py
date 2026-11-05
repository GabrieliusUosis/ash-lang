import pytest
from antlr4 import InputStream, CommonTokenStream
from grammar.AutomataLexer import AutomataLexer
from grammar.AutomataParser import AutomataParser
from src.SemanticAnalyser import SemanticAnalyser, SemanticError
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
    assert machine.transitions[0] == {"source": "q0", "symbol": "a", "target": "q1"}
    assert machine.transitions[1] == {"source": "q1", "symbol": "b", "target": "q2"}

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
    assert regex_data["type"] == "REGEX"
    assert regex_data["expression"] == "(a|b)*"

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
