# ash-lang

**ash-lang** is a declarative Domain-Specific Language (DSL) and workbench for defining, validating, simulating, and transforming formal models of computation (**DFAs**, **NFAs**, **Regular Expressions**, and **Regular Grammars**).

---

## Current Status

| Feature | Status | Notes |
| :--- | :---: | :--- |
| **ANTLR4 Lexer & Parser** | Implemented | Supports `dfa`, `nfa`, `regex`, and unquoted `\e` epsilon tokens (`grammar/`). |
| **Semantic Analyser** | Implemented | Enforces unique names, declared states, single-character alphabets, `\e` rules, and DFA determinism (`src/semantic_analyser.py`). |
| **DFA Runtime Engine** | Implemented | $O(1)$ transition table, `simulate()`, `trace()`, and `.to_ash()` round-trip serialization (`src/runtime/dfa.py`). |
| **CLI & ANTLR Inspection** | Implemented | `ash` CLI command with `-code`, `-tree`, `-tokens`, and `-gui` flags (`src/cli.py`). |
| **NFA Runtime Engine** | In Progress | `NFA` model stub created (`src/runtime/nfa.py`); $\varepsilon$-closure and simulation next. |
| **Regex AST & Algorithms** | Planned | Thompson's Construction, Subset Construction, Brzozowski Derivatives, Hopcroft Minimization, Regular Grammars, Equivalence Checking, and Graphviz/LaTeX export. |

---

## Fresh Clone Setup

Generated ANTLR Python parser files (`grammar/Automata*.py`) are excluded by `.gitignore` and must be generated once after cloning:

```powershell
# 1. Install runtime dependencies and register the `ash` CLI command
cd ash-lang
pip install -r requirements.txt
pip install -e .

# 2. Generate the ANTLR4 lexer, parser, and visitor inside grammar/
cd grammar
antlr4 -Dlanguage=Python3 -visitor AutomataLexer.g4 AutomataParser.g4
cd ..
```

---

## Quick Start

```powershell
# Validate and list machines in a file
ash demo.ash

# Simulate a DFA on input words with full transition traces
ash demo.ash EndsWithZero "1010" "1011" "0"

# Print formatted source for one machine or the whole file
ash demo.ash EndsWithZero -code
ash demo.ash -code

# Inspect tokens or parse tree via ANTLR TestRig
ash demo.ash -tokens
ash demo.ash -tree
ash demo.ash -gui

# Run the unit test suite
pytest -v
```

For the full grammar and CLI specification, see [SYNTAX.md](SYNTAX.md).
