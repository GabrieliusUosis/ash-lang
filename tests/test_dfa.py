import pytest
from antlr4 import InputStream, CommonTokenStream
from grammar.AutomataLexer import AutomataLexer
from grammar.AutomataParser import AutomataParser
from src.SemanticAnalyser import SemanticAnalyser
from src.runtime.dfa import DFA

def make_ends_with_zero_dfa() -> DFA:
    return DFA(
        name="EndsWithZero",
        states=["s0", "s1"],
        alphabet=["0", "1"],
        start="s0",
        accept=["s1"],
        transitions=[
            {"source": "s0", "symbol": "0", "target": "s1"},
            {"source": "s0", "symbol": "1", "target": "s0"},
            {"source": "s1", "symbol": "0", "target": "s1"},
            {"source": "s1", "symbol": "1", "target": "s0"},
        ],
    )

def test_dfa_step_lookup():
    dfa = make_ends_with_zero_dfa()
    assert dfa.step("s0", "0") == "s1"
    assert dfa.step("s0", "1") == "s0"
    assert dfa.step("s1", "9") is None

def test_dfa_simulate_accepts_valid_words():
    dfa = make_ends_with_zero_dfa()
    assert dfa.simulate("0") is True
    assert dfa.simulate("10") is True
    assert dfa.simulate("110100") is True

def test_dfa_simulate_rejects_invalid_words():
    dfa = make_ends_with_zero_dfa()
    assert dfa.simulate("") is False
    assert dfa.simulate("1") is False
    assert dfa.simulate("0101") is False

def test_dfa_simulate_empty_string_when_start_is_accept():
    dfa = DFA(
        name="AcceptEmpty",
        states=["q0"],
        alphabet=["a"],
        start="q0",
        accept=["q0"],
        transitions=[],
    )
    assert dfa.simulate("") is True
    assert dfa.simulate("a") is False

def test_dfa_partial_transitions_implicit_dead_state():
    dfa = DFA(
        name="OnlyA",
        states=["q0", "q1"],
        alphabet=["a", "b"],
        start="q0",
        accept=["q1"],
        transitions=[
            {"source": "q0", "symbol": "a", "target": "q1"},
        ],
    )
    assert dfa.simulate("a") is True
    assert dfa.simulate("b") is False
    assert dfa.simulate("ab") is False

def test_dfa_simulate_invalid_alphabet_symbol_raises():
    dfa = make_ends_with_zero_dfa()
    with pytest.raises(ValueError, match="Symbol '2' is not in the alphabet"):
        dfa.simulate("102")

def test_dfa_trace_accepted_path():
    dfa = make_ends_with_zero_dfa()
    accepted, path = dfa.trace("10")
    assert accepted is True
    assert path == [
        ("s0", "1", "s0"),
        ("s0", "0", "s1"),
    ]

def test_dfa_trace_partial_dead_end():
    dfa = DFA(
        name="Partial",
        states=["q0", "q1"],
        alphabet=["a", "b"],
        start="q0",
        accept=["q1"],
        transitions=[
            {"source": "q0", "symbol": "a", "target": "q1"},
        ],
    )
    accepted, path = dfa.trace("ab")
    assert accepted is False
    assert path == [("q0", "a", "q1")]

def test_dfa_from_machine_data_integration():
    code = """
    dfa EndsWithB {
        states: q0, q1
        alphabet: "a", "b"
        start: q0
        accept: q1
        transitions: {
            q0 -> q0: "a"
            q0 -> q1: "b"
            q1 -> q0: "a"
            q1 -> q1: "b"
        }
    }
    """
    lexer = AutomataLexer(InputStream(code))
    parser = AutomataParser(CommonTokenStream(lexer))
    analyzer = SemanticAnalyser()
    analyzer.visit(parser.program())

    dfa = DFA.from_machine_data(analyzer.machines["EndsWithB"])
    assert dfa.simulate("aab") is True
    assert dfa.simulate("aba") is False
