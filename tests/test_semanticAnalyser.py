import pytest
from antlr4 import InputStream, CommonTokenStream
from grammar.AutomataLexer import AutomataLexer
from grammar.AutomataParser import AutomataParser
from src.SemanticAnalyser import SemanticAnalyser

def get_parse_tree(source_code: str):
    """Helper to generate a parse tree from a string snippet."""
    stream = InputStream(source_code)
    lexer = AutomataLexer(stream)
    token_stream = CommonTokenStream(lexer)
    parser = AutomataParser(token_stream)
    # Target the program rule as the entry point
    return parser.program() 

def test_dfa_states_extraction():
    # Arrange
    code = """
    dfa M1 { 
        states: q0, q1, q2 
    }
    """
    tree = get_parse_tree(code)
    analyzer = SemanticAnalyser()

    # Act
    analyzer.visit(tree)

    # Assert
    assert "M1" in analyzer.machines
    machine = analyzer.machines["M1"]
    
    assert machine.machine_type == "DFA"
    assert machine.name == "M1"
    assert machine.states == ["q0", "q1", "q2"]

def test_dfa_full_properties_extraction():
    # Arrange
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

    # Act
    analyzer.visit(tree)

    # Assert
    machine = analyzer.machines["M2"]
    assert machine.states == ["q0", "q1", "q2"]
    assert machine.alphabet == ["a", "b"]
    assert machine.start == "q0"
    assert machine.accept == ["q2"]