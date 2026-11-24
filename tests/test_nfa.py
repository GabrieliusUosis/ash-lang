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

def test_sipser_nfa_third_from_last_is_one_exhaustive():
    code = """
    nfa ThirdFromLastOne {
        states: q1, q2, q3, q4
        alphabet: "0", "1"
        start: q1
        accept: q4
        transitions: {
            q1 -> q1: "0"
            q1 -> q1: "1"
            q1 -> q2: "1"
            q2 -> q3: "0"
            q2 -> q3: "1"
            q3 -> q4: "0"
            q3 -> q4: "1"
        }
    }
    """
    nfa = compile_nfa(code, "ThirdFromLastOne")
    for word in all_words("01", 8):
        expected = len(word) >= 3 and word[-3] == "1"
        assert nfa.simulate(word) is expected, f"Mismatch on '{word}'"

def test_sipser_nfa_epsilon_union_even_zeros_or_even_ones_exhaustive():
    code = r"""
    nfa EvenZerosOrEvenOnes {
        states: q_start, z_even, z_odd, o_even, o_odd
        alphabet: "0", "1"
        start: q_start
        accept: z_even, o_even
        transitions: {
            q_start -> z_even: \e
            q_start -> o_even: \e
            z_even -> z_odd: "0"
            z_even -> z_even: "1"
            z_odd -> z_even: "0"
            z_odd -> z_odd: "1"
            o_even -> o_odd: "1"
            o_even -> o_even: "0"
            o_odd -> o_even: "1"
            o_odd -> o_odd: "0"
        }
    }
    """
    nfa = compile_nfa(code, "EvenZerosOrEvenOnes")
    for word in all_words("01", 8):
        expected = (word.count("0") % 2 == 0) or (word.count("1") % 2 == 0)
        assert nfa.simulate(word) is expected, f"Mismatch on '{word}'"

def test_sipser_nfa_contains_101_or_11_exhaustive():
    code = """
    nfa Contains101Or11 {
        states: q1, q2, q3, q4
        alphabet: "0", "1"
        start: q1
        accept: q4
        transitions: {
            q1 -> q1: "0"
            q1 -> q1: "1"
            q1 -> q2: "1"
            q2 -> q3: "0"
            q2 -> q4: "1"
            q3 -> q4: "1"
            q4 -> q4: "0"
            q4 -> q4: "1"
        }
    }
    """
    nfa = compile_nfa(code, "Contains101Or11")
    for word in all_words("01", 8):
        expected = ("101" in word) or ("11" in word)
        assert nfa.simulate(word) is expected, f"Mismatch on '{word}'"

def test_nfa_empty_accept_set_rejects_everything():
    code = r"""
    nfa EmptyLang {
        states: q0, q1
        alphabet: "0", "1"
        start: q0
        transitions: {
            q0 -> q1: \e
            q0 -> q0: "0"
            q1 -> q0: "1"
        }
    }
    """
    nfa = compile_nfa(code, "EmptyLang")
    for word in ["", "0", "1", "01", "10", "0101"]:
        assert nfa.simulate(word) is False

def test_nfa_unreachable_accept_state():
    code = r"""
    nfa Unreachable {
        states: q0, q1, q_isolated
        alphabet: "a"
        start: q0
        accept: q_isolated
        transitions: {
            q0 -> q1: \e
            q1 -> q0: "a"
        }
    }
    """
    nfa = compile_nfa(code, "Unreachable")
    assert nfa.simulate("") is False
    assert nfa.simulate("a") is False
    assert nfa.simulate("aaa") is False

def test_nfa_epsilon_only_machine_and_empty_word_trace():
    code = r"""
    nfa EpsOnly {
        states: q0, q1
        start: q0
        accept: q1
        transitions: {
            q0 -> q1: \e
        }
    }
    """
    nfa = compile_nfa(code, "EpsOnly")
    accepted, path = nfa.trace("")
    assert accepted is True
    assert path == []
    with pytest.raises(ValueError, match="Symbol 'a' is not in the alphabet"):
        nfa.simulate("a")

def test_nfa_dict_transitions_and_duplicate_deduplication():
    nfa = NFA(
        name="DictInit",
        states=["q0", "q1"],
        alphabet=["a"],
        start="q0",
        accept=["q1"],
        transitions=[
            {"source": "q0", "symbol": "a", "target": "q1"},
            {"source": "q0", "symbol": "a", "target": "q1"},
            {"source": "q0", "symbol": EPSILON, "target": "q0"},
        ],
    )
    assert nfa.step({"q0"}, "a") == {"q1"}
    assert nfa.simulate("a") is True
    assert nfa.simulate("") is False

def test_nfa_immutability_and_state_isolation_between_runs():
    nfa = make_ends_with_01_nfa()
    seed = {"q0"}
    closure = nfa.epsilon_closure(seed)
    closure.add("mutated")
    assert seed == {"q0"}

    accepted, path = nfa.trace("01")
    assert accepted is True
    path[0][2].add("mutated")

    assert nfa.simulate("01") is True
    assert nfa.simulate("10") is False
    with pytest.raises(ValueError):
        nfa.simulate("2")
    assert nfa.start == "q0"
    assert nfa.simulate("1001") is True

def test_nfa_escaped_special_chars_mixed_with_epsilon():
    code = r"""
    nfa EscapedNFA {
        states: q0, q1, q2
        alphabet: "\"", "\\", " "
        start: q0
        accept: q2
        transitions: {
            q0 -> q1: \e
            q0 -> q1: "\""
            q1 -> q1: " "
            q1 -> q2: "\\"
        }
    }
    """
    nfa = compile_nfa(code, "EscapedNFA")
    assert nfa.simulate("\\") is True
    assert nfa.simulate('"  \\') is True
    assert nfa.simulate('" ') is False
    recompiled = compile_nfa(nfa.to_ash(), "EscapedNFA")
    assert recompiled.simulate('" \\') is True
    assert recompiled.simulate('"') is False
