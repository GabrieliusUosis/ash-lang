import itertools
import pytest
from antlr4 import InputStream, CommonTokenStream
from antlr4.error.ErrorListener import ErrorListener
from grammar.AutomataLexer import AutomataLexer
from grammar.AutomataParser import AutomataParser
from src.semantic_analyser import SemanticAnalyser
from src.runtime.dfa import DFA

class _StrictErrorListener(ErrorListener):
    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        raise SyntaxError(f"Syntax error at line {line}:{column} - {msg}")

def compile_dfa(code: str, name: str) -> DFA:
    lexer = AutomataLexer(InputStream(code))
    lexer.removeErrorListeners()
    lexer.addErrorListener(_StrictErrorListener())
    parser = AutomataParser(CommonTokenStream(lexer))
    parser.removeErrorListeners()
    parser.addErrorListener(_StrictErrorListener())
    analyzer = SemanticAnalyser()
    analyzer.visit(parser.program())
    return DFA.from_machine_data(analyzer.machines[name])

def all_words(alphabet: str, max_len: int):
    for length in range(max_len + 1):
        for chars in itertools.product(alphabet, repeat=length):
            yield "".join(chars)

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

def make_divisible_by_three_dfa() -> DFA:
    return DFA(
        name="DivisibleByThree",
        states=["r0", "r1", "r2"],
        alphabet=["0", "1"],
        start="r0",
        accept=["r0"],
        transitions=[
            {"source": "r0", "symbol": "0", "target": "r0"},
            {"source": "r0", "symbol": "1", "target": "r1"},
            {"source": "r1", "symbol": "0", "target": "r2"},
            {"source": "r1", "symbol": "1", "target": "r0"},
            {"source": "r2", "symbol": "0", "target": "r1"},
            {"source": "r2", "symbol": "1", "target": "r2"},
        ],
    )

def test_dfa_step_lookup():
    dfa = make_ends_with_zero_dfa()
    assert dfa.step("s0", "0") == "s1"
    assert dfa.step("s0", "1") == "s0"
    assert dfa.step("s1", "9") is None
    assert dfa.step("nonexistent", "0") is None

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

@pytest.mark.parametrize("binary_str,expected", [
    ("", True),
    ("0", True),
    ("1", False),
    ("10", False),
    ("11", True),
    ("100", False),
    ("101", False),
    ("110", True),
    ("111", False),
    ("1001", True),
    ("1100", True),
    ("1111", True),
    ("10000", False),
])
def test_dfa_divisible_by_three_parametrized(binary_str, expected):
    dfa = make_divisible_by_three_dfa()
    assert dfa.simulate(binary_str) is expected

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

def test_dfa_empty_accept_set_rejects_everything():
    dfa = DFA(
        name="EmptyLanguage",
        states=["q0", "q1"],
        alphabet=["a", "b"],
        start="q0",
        accept=[],
        transitions=[
            {"source": "q0", "symbol": "a", "target": "q1"},
            {"source": "q0", "symbol": "b", "target": "q0"},
            {"source": "q1", "symbol": "a", "target": "q0"},
            {"source": "q1", "symbol": "b", "target": "q1"},
        ],
    )
    for word in ["", "a", "b", "ab", "ba", "aaabbb"]:
        assert dfa.simulate(word) is False

def test_dfa_universal_language_accepts_all_words():
    dfa = DFA(
        name="SigmaStar",
        states=["q0"],
        alphabet=["0", "1"],
        start="q0",
        accept=["q0"],
        transitions=[
            {"source": "q0", "symbol": "0", "target": "q0"},
            {"source": "q0", "symbol": "1", "target": "q0"},
        ],
    )
    for word in ["", "0", "1", "010101", "111000"]:
        assert dfa.simulate(word) is True

def test_dfa_explicit_trap_state():
    dfa = DFA(
        name="StartsWithA",
        states=["q_start", "q_ok", "q_trap"],
        alphabet=["a", "b"],
        start="q_start",
        accept=["q_ok"],
        transitions=[
            {"source": "q_start", "symbol": "a", "target": "q_ok"},
            {"source": "q_start", "symbol": "b", "target": "q_trap"},
            {"source": "q_ok", "symbol": "a", "target": "q_ok"},
            {"source": "q_ok", "symbol": "b", "target": "q_ok"},
            {"source": "q_trap", "symbol": "a", "target": "q_trap"},
            {"source": "q_trap", "symbol": "b", "target": "q_trap"},
        ],
    )
    assert dfa.simulate("a") is True
    assert dfa.simulate("abbb") is True
    assert dfa.simulate("b") is False
    assert dfa.simulate("baaa") is False

def test_dfa_unreachable_accept_state():
    dfa = DFA(
        name="UnreachableAccept",
        states=["q0", "q_isolated"],
        alphabet=["a"],
        start="q0",
        accept=["q_isolated"],
        transitions=[
            {"source": "q0", "symbol": "a", "target": "q0"},
        ],
    )
    assert dfa.simulate("") is False
    assert dfa.simulate("a") is False
    assert dfa.simulate("aaaa") is False

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
    assert dfa.simulate("aa") is False

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

def test_dfa_trace_empty_string():
    dfa_reject_empty = make_ends_with_zero_dfa()
    accepted, path = dfa_reject_empty.trace("")
    assert accepted is False
    assert path == []

    dfa_accept_empty = make_divisible_by_three_dfa()
    accepted, path = dfa_accept_empty.trace("")
    assert accepted is True
    assert path == []

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

def test_dfa_trace_invalid_symbol_raises():
    dfa = make_ends_with_zero_dfa()
    with pytest.raises(ValueError, match="Symbol 'x' is not in the alphabet"):
        dfa.trace("01x")

def test_dfa_long_input_stress():
    dfa = make_ends_with_zero_dfa()
    long_accepted = ("10" * 500) + "0"
    long_rejected = ("10" * 500) + "1"
    assert dfa.simulate(long_accepted) is True
    assert dfa.simulate(long_rejected) is False

def test_dfa_state_isolation_across_multiple_runs():
    dfa = make_ends_with_zero_dfa()
    assert dfa.simulate("0") is True
    assert dfa.simulate("1") is False
    with pytest.raises(ValueError):
        dfa.simulate("9")
    assert dfa.start == "s0"
    assert dfa.simulate("10") is True

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

def test_dfa_partial_dead_end_still_validates_remaining_alphabet():
    dfa = DFA(
        name="Partial",
        states=["q0", "q1"],
        alphabet=["a", "b"],
        start="q0",
        accept=["q1"],
        transitions=[{"source": "q0", "symbol": "a", "target": "q1"}],
    )
    with pytest.raises(ValueError, match="Symbol 'z' is not in the alphabet"):
        dfa.simulate("bz")
    with pytest.raises(ValueError, match="Symbol 'z' is not in the alphabet"):
        dfa.trace("bz")

def test_sipser_overlapping_substring_0101_exhaustive():
    code = """
    dfa Contains0101 {
        states: q_e, q_0, q_01, q_010, q_0101
        alphabet: "0", "1"
        start: q_e
        accept: q_0101
        transitions: {
            q_e -> q_0: "0"
            q_e -> q_e: "1"
            q_0 -> q_0: "0"
            q_0 -> q_01: "1"
            q_01 -> q_010: "0"
            q_01 -> q_e: "1"
            q_010 -> q_0: "0"
            q_010 -> q_0101: "1"
            q_0101 -> q_0101: "0"
            q_0101 -> q_0101: "1"
        }
    }
    """
    dfa = compile_dfa(code, "Contains0101")
    assert dfa.simulate("010101") is True
    assert dfa.simulate("0100101") is True
    assert dfa.simulate("010") is False
    for word in all_words("01", 8):
        assert dfa.simulate(word) is ("0101" in word), f"Mismatch on '{word}'"

def test_sipser_all_except_11_and_111_exhaustive():
    code = """
    dfa Except11And111 {
        states: q_start, q_1, q_11, q_111, q_ok
        alphabet: "0", "1"
        start: q_start
        accept: q_start, q_1, q_ok
        transitions: {
            q_start -> q_ok: "0"
            q_start -> q_1: "1"
            q_1 -> q_ok: "0"
            q_1 -> q_11: "1"
            q_11 -> q_ok: "0"
            q_11 -> q_111: "1"
            q_111 -> q_ok: "0"
            q_111 -> q_ok: "1"
            q_ok -> q_ok: "0"
            q_ok -> q_ok: "1"
        }
    }
    """
    dfa = compile_dfa(code, "Except11And111")
    assert dfa.simulate("11") is False
    assert dfa.simulate("111") is False
    assert dfa.simulate("1111") is True
    for word in all_words("01", 8):
        assert dfa.simulate(word) is (word not in ("11", "111")), f"Mismatch on '{word}'"

def test_sipser_ex1_12_even_a_odd_b_no_ab_exhaustive():
    code = """
    dfa EvenAOddBNoAB {
        states: q_bEven, q_bOdd, q_aOdd, q_aEven, q_trap
        alphabet: "a", "b"
        start: q_bEven
        accept: q_bOdd, q_aEven
        transitions: {
            q_bEven -> q_bOdd: "b"
            q_bEven -> q_trap: "a"
            q_bOdd -> q_bEven: "b"
            q_bOdd -> q_aOdd: "a"
            q_aOdd -> q_aEven: "a"
            q_aOdd -> q_trap: "b"
            q_aEven -> q_aOdd: "a"
            q_aEven -> q_trap: "b"
            q_trap -> q_trap: "a"
            q_trap -> q_trap: "b"
        }
    }
    """
    dfa = compile_dfa(code, "EvenAOddBNoAB")
    for word in all_words("ab", 8):
        expected = (word.count("a") % 2 == 0) and (word.count("b") % 2 == 1) and ("ab" not in word)
        assert dfa.simulate(word) is expected, f"Mismatch on '{word}'"

def test_sipser_ex1_13_no_ones_odd_distance_exhaustive():
    code = """
    dfa NoOddGapOnes {
        states: E_00, O_00, E_10, O_10, E_01, O_01, E_11, O_11, q_trap
        alphabet: "0", "1"
        start: E_00
        accept: E_00, O_00, E_10, O_10, E_01, O_01, E_11, O_11
        transitions: {
            E_00 -> O_00: "0"
            E_00 -> O_10: "1"
            O_00 -> E_00: "0"
            O_00 -> E_01: "1"
            E_10 -> O_10: "0"
            E_10 -> q_trap: "1"
            O_10 -> E_10: "0"
            O_10 -> E_11: "1"
            E_01 -> O_01: "0"
            E_01 -> O_11: "1"
            O_01 -> E_01: "0"
            O_01 -> q_trap: "1"
            E_11 -> O_11: "0"
            E_11 -> q_trap: "1"
            O_11 -> E_11: "0"
            O_11 -> q_trap: "1"
            q_trap -> q_trap: "0"
            q_trap -> q_trap: "1"
        }
    }
    """
    dfa = compile_dfa(code, "NoOddGapOnes")
    for word in all_words("01", 8):
        ones = [i for i, ch in enumerate(word) if ch == "1"]
        expected = all((j - i - 1) % 2 == 0 for idx, i in enumerate(ones) for j in ones[idx + 1:])
        assert dfa.simulate(word) is expected, f"Mismatch on '{word}'"

def test_binary_divisible_by_five_exhaustive():
    code = """
    dfa DivisibleByFive {
        states: r0, r1, r2, r3, r4
        alphabet: "0", "1"
        start: r0
        accept: r0
        transitions: {
            r0 -> r0: "0"
            r0 -> r1: "1"
            r1 -> r2: "0"
            r1 -> r3: "1"
            r2 -> r4: "0"
            r2 -> r0: "1"
            r3 -> r1: "0"
            r3 -> r2: "1"
            r4 -> r3: "0"
            r4 -> r4: "1"
        }
    }
    """
    dfa = compile_dfa(code, "DivisibleByFive")
    for word in all_words("01", 8):
        expected = True if word == "" else (int(word, 2) % 5 == 0)
        assert dfa.simulate(word) is expected, f"Mismatch on '{word}'"

def test_forbidden_substring_110_exhaustive():
    code = """
    dfa DoesNotContain110 {
        states: q0, q1, q11, q_trap
        alphabet: "0", "1"
        start: q0
        accept: q0, q1, q11
        transitions: {
            q0 -> q0: "0"
            q0 -> q1: "1"
            q1 -> q0: "0"
            q1 -> q11: "1"
            q11 -> q_trap: "0"
            q11 -> q11: "1"
            q_trap -> q_trap: "0"
            q_trap -> q_trap: "1"
        }
    }
    """
    dfa = compile_dfa(code, "DoesNotContain110")
    for word in all_words("01", 8):
        assert dfa.simulate(word) is ("110" not in word), f"Mismatch on '{word}'"

def test_cartesian_product_mod3_a_and_mod2_b_exhaustive():
    code = """
    dfa Mod3AMod2B {
        states: q00, q01, q10, q11, q20, q21
        alphabet: "a", "b"
        start: q00
        accept: q00
        transitions: {
            q00 -> q10: "a"
            q00 -> q01: "b"
            q01 -> q11: "a"
            q01 -> q00: "b"
            q10 -> q20: "a"
            q10 -> q11: "b"
            q11 -> q21: "a"
            q11 -> q10: "b"
            q20 -> q00: "a"
            q20 -> q21: "b"
            q21 -> q01: "a"
            q21 -> q20: "b"
        }
    }
    """
    dfa = compile_dfa(code, "Mod3AMod2B")
    for word in all_words("ab", 8):
        expected = (word.count("a") % 3 == 0) and (word.count("b") % 2 == 0)
        assert dfa.simulate(word) is expected, f"Mismatch on '{word}'"

def test_decimal_divisible_by_three_large_alphabet():
    transitions = "\n".join(
        f'            r{r} -> r{(10 * r + d) % 3}: "{d}"'
        for r in range(3)
        for d in range(10)
    )
    digits = ", ".join(f'"{d}"' for d in range(10))
    code = f"""
    dfa DecimalMod3 {{
        states: r0, r1, r2
        alphabet: {digits}
        start: r0
        accept: r0
        transitions: {{
{transitions}
        }}
    }}
    """
    dfa = compile_dfa(code, "DecimalMod3")
    for n in range(250):
        assert dfa.simulate(str(n)) is (n % 3 == 0)
    assert dfa.simulate("003") is True
    assert dfa.simulate("0014") is False

def test_compiler_lexer_signed_decimal_literal_dfa():
    code = """
    dfa SignedDecimal {
        states: start_s, sign_s, int_s, dot_s, frac_s, trap_s
        alphabet: "+", "-", "0", "1", "."
        start: start_s
        accept: int_s, frac_s
        transitions: {
            start_s -> sign_s: "+"
            start_s -> sign_s: "-"
            start_s -> int_s: "0"
            start_s -> int_s: "1"
            start_s -> trap_s: "."

            sign_s -> int_s: "0"
            sign_s -> int_s: "1"
            sign_s -> trap_s: "+"
            sign_s -> trap_s: "-"
            sign_s -> trap_s: "."

            int_s -> int_s: "0"
            int_s -> int_s: "1"
            int_s -> dot_s: "."
            int_s -> trap_s: "+"
            int_s -> trap_s: "-"

            dot_s -> frac_s: "0"
            dot_s -> frac_s: "1"
            dot_s -> trap_s: "."
            dot_s -> trap_s: "+"
            dot_s -> trap_s: "-"

            frac_s -> frac_s: "0"
            frac_s -> frac_s: "1"
            frac_s -> trap_s: "."
            frac_s -> trap_s: "+"
            frac_s -> trap_s: "-"

            trap_s -> trap_s: "+"
            trap_s -> trap_s: "-"
            trap_s -> trap_s: "0"
            trap_s -> trap_s: "1"
            trap_s -> trap_s: "."
        }
    }
    """
    dfa = compile_dfa(code, "SignedDecimal")
    for valid in ["0", "1", "+0", "-101", "10.01", "+0.1", "-1.000"]:
        assert dfa.simulate(valid) is True, f"Expected accept for '{valid}'"
    for invalid in ["", "+", "-", ".", ".0", "1.", "+.0", "1..0", "1.0.1", "+-1", "1+0"]:
        assert dfa.simulate(invalid) is False, f"Expected reject for '{invalid}'"

def test_dfa_escaped_and_special_character_alphabets():
    code = r"""
    dfa SpecialChars {
        states: q0, q1, q2
        alphabet: "\"", "\\", " ", "α"
        start: q0
        accept: q2
        transitions: {
            q0 -> q1: "\""
            q1 -> q1: " "
            q1 -> q1: "\\"
            q1 -> q2: "α"
        }
    }
    """
    dfa = compile_dfa(code, "SpecialChars")
    assert dfa.simulate('" α') is True
    assert dfa.simulate('"\\ α') is True
    assert dfa.simulate('"') is False
    assert dfa.simulate('α') is False

def test_dfa_to_ash_exact_output():
    dfa = make_ends_with_zero_dfa()
    expected = (
        "dfa EndsWithZero {\n"
        "    states: s0, s1\n"
        '    alphabet: "0", "1"\n'
        "    start: s0\n"
        "    accept: s1\n"
        "    transitions: {\n"
        '        s0 -> s1: "0"\n'
        '        s0 -> s0: "1"\n'
        '        s1 -> s1: "0"\n'
        '        s1 -> s0: "1"\n'
        "    }\n"
        "}"
    )
    assert dfa.to_ash() == expected

def test_dfa_to_ash_round_trip_compilation():
    original = make_divisible_by_three_dfa()
    emitted_code = original.to_ash()
    recompiled = compile_dfa(emitted_code, "DivisibleByThree")
    for word in all_words("01", 6):
        assert recompiled.simulate(word) is original.simulate(word)

def test_dfa_to_ash_escaped_symbols_round_trip():
    dfa = DFA(
        name="EscapedDFA",
        states=["q0", "q1"],
        alphabet=['"', "\\", "\n"],
        start="q0",
        accept=["q1"],
        transitions=[
            {"source": "q0", "symbol": '"', "target": "q1"},
            {"source": "q1", "symbol": "\\", "target": "q1"},
            {"source": "q1", "symbol": "\n", "target": "q0"},
        ],
    )
    recompiled = compile_dfa(dfa.to_ash(), "EscapedDFA")
    assert recompiled.simulate('"\\') is True
    assert recompiled.simulate('"\n') is False

def test_dfa_to_ash_minimal_machine_omits_empty_sections():
    dfa = DFA(
        name="Minimal",
        states=["q0"],
        alphabet=[],
        start="q0",
        accept=[],
        transitions=[],
    )
    assert dfa.to_ash() == "dfa Minimal {\n    states: q0\n    start: q0\n}"
    recompiled = compile_dfa(dfa.to_ash(), "Minimal")
    assert recompiled.simulate("") is False

def test_cli_format_machine_code_for_dfa_nfa_and_regex():
    from main import format_machine_code, parse_code
    code = """
    dfa D1 { states: s0, s1 alphabet: "0" start: s0 accept: s1 transitions: { s0 -> s1: "0" } }
    nfa N1 { states: q0, q1 alphabet: "a" start: q0 accept: q1 transitions: { q0 -> q1: "a" } }
    regex R1 = (a|b)*
    """
    machines = parse_code(source_code=code)
    assert "dfa D1 {" in format_machine_code(machines["D1"])
    assert "nfa N1 {" in format_machine_code(machines["N1"])
    assert format_machine_code(machines["R1"]) == "regex R1 = (a|b)*"
