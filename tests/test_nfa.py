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
