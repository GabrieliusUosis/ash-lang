import pytest
from src.models import EPSILON, Transition
from src.runtime.nfa import NFA
from tests.conftest import all_words, compile_nfa

def make_ends_with_01_nfa() -> NFA:
    return NFA(
        name="EndsWith01",
        states=["q0", "q1", "q2"],
        alphabet=["0", "1"],
        start="q0",
        accept=["q2"],
        transitions=[
            Transition("q0", "0", "q0"),
            Transition("q0", "1", "q0"),
            Transition("q0", "0", "q1"),
            Transition("q1", "1", "q2"),
        ],
    )

def test_nfa_epsilon_closure_without_epsilons():
    nfa = make_ends_with_01_nfa()
    assert nfa.epsilon_closure({"q0"}) == {"q0"}
    assert nfa.epsilon_closure({"q0", "q2"}) == {"q0", "q2"}
    assert nfa.epsilon_closure(set()) == set()

def test_nfa_epsilon_closure_multi_hop_chain():
    nfa = NFA(
        name="EpsChain",
        states=["q0", "q1", "q2", "q3"],
        alphabet=["a"],
        start="q0",
        accept=["q3"],
        transitions=[
            Transition("q0", EPSILON, "q1"),
            Transition("q1", EPSILON, "q2"),
            Transition("q2", "a", "q3"),
        ],
    )
    assert nfa.epsilon_closure({"q0"}) == {"q0", "q1", "q2"}
    assert nfa.epsilon_closure({"q1"}) == {"q1", "q2"}

def test_nfa_epsilon_closure_cycle_and_self_loop_terminate():
    nfa = NFA(
        name="EpsCycle",
        states=["q0", "q1", "q2"],
        alphabet=["a"],
        start="q0",
        accept=["q2"],
        transitions=[
            Transition("q0", EPSILON, "q0"),
            Transition("q0", EPSILON, "q1"),
            Transition("q1", EPSILON, "q0"),
            Transition("q1", EPSILON, "q2"),
            Transition("q2", EPSILON, "q0"),
        ],
    )
    assert nfa.epsilon_closure({"q0"}) == {"q0", "q1", "q2"}

def test_nfa_step_branching_and_post_epsilon_closure():
    nfa = NFA(
        name="PostEps",
        states=["q0", "q1", "q2", "q3"],
        alphabet=["a", "b"],
        start="q0",
        accept=["q3"],
        transitions=[
            Transition("q0", "a", "q1"),
            Transition("q0", "a", "q2"),
            Transition("q2", EPSILON, "q3"),
        ],
    )
    assert nfa.step({"q0"}, "a") == {"q1", "q2", "q3"}

def test_nfa_step_dead_branch_returns_empty_set():
    nfa = make_ends_with_01_nfa()
    assert nfa.step({"q2"}, "0") == set()
    assert nfa.step({"q1"}, "0") == set()

def test_nfa_simulate_non_deterministic_branching():
    nfa = make_ends_with_01_nfa()
    assert nfa.simulate("01") is True
    assert nfa.simulate("1001") is True
    assert nfa.simulate("") is False
    assert nfa.simulate("1") is False
    assert nfa.simulate("1010") is False

def test_nfa_simulate_empty_string_accepted_via_epsilon_chain():
    code = r"""
    nfa EpsStartToAccept {
        states: q0, q1, q2
        alphabet: "a"
        start: q0
        accept: q2
        transitions: {
            q0 -> q1: \e
            q1 -> q2: \e
            q2 -> q2: "a"
        }
    }
    """
    nfa = compile_nfa(code, "EpsStartToAccept")
    assert nfa.simulate("") is True
    assert nfa.simulate("aaa") is True

def test_nfa_simulate_all_branches_die_mid_word():
    code = """
    nfa OnlyAB {
        states: q0, q1, q2
        alphabet: "a", "b"
        start: q0
        accept: q2
        transitions: {
            q0 -> q1: "a"
            q1 -> q2: "b"
        }
    }
    """
    nfa = compile_nfa(code, "OnlyAB")
    assert nfa.simulate("ab") is True
    assert nfa.simulate("baaa") is False
    assert nfa.simulate("aba") is False

def test_nfa_simulate_invalid_symbol_raises_even_after_dead_end():
    code = """
    nfa OnlyA {
        states: q0, q1
        alphabet: "a", "b"
        start: q0
        accept: q1
        transitions: {
            q0 -> q1: "a"
        }
    }
    """
    nfa = compile_nfa(code, "OnlyA")
    with pytest.raises(ValueError, match="Symbol 'z' is not in the alphabet"):
        nfa.simulate("bz")
    with pytest.raises(ValueError, match="Symbol 'z' is not in the alphabet"):
        nfa.trace("bz")

def test_nfa_trace_records_active_state_sets():
    nfa = make_ends_with_01_nfa()
    accepted, path = nfa.trace("01")
    assert accepted is True
    assert path == [
        ({"q0"}, "0", {"q0", "q1"}),
        ({"q0", "q1"}, "1", {"q0", "q2"}),
    ]

    dead_nfa = NFA(
        name="OnlyA",
        states=["q0", "q1"],
        alphabet=["a", "b"],
        start="q0",
        accept=["q1"],
        transitions=[Transition("q0", "a", "q1")],
    )
    accepted_dead, dead_path = dead_nfa.trace("ab")
    assert accepted_dead is False
    assert dead_path == [({"q0"}, "a", {"q1"})]

def test_nfa_to_ash_round_trip_with_epsilon():
    code = r"""
    nfa EpsRoundTrip {
        states: q0, q1, q2
        alphabet: "a", "b"
        start: q0
        accept: q2
        transitions: {
            q0 -> q1: \e
            q1 -> q1: "a"
            q1 -> q2: "b"
        }
    }
    """
    original = compile_nfa(code, "EpsRoundTrip")
    emitted = original.to_ash()
    assert r"q0 -> q1: \e" in emitted
    recompiled = compile_nfa(emitted, "EpsRoundTrip")
    for word in all_words("ab", 5):
        assert recompiled.simulate(word) is original.simulate(word)
