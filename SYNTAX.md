# ash-lang Syntax & CLI Reference Guide

This document covers how to run `.ash` programs from the command line, inspect tokens and parse trees with ANTLR (`grun`), and write syntactically and semantically valid **DFAs**, **NFAs**, and **Regular Expressions**.

---

## 1. Command-Line Interface (CLI) Usage

Install the `ash` CLI command in editable mode and generate the ANTLR files (only needed once):

```powershell
cd ash-lang
pip install -e .
cd grammar
antlr4 -Dlanguage=Python3 -visitor AutomataLexer.g4 AutomataParser.g4
cd ..
```

*(Note: Every `ash ...` command below can also be run via `python main.py ...`)*

### 1.1 Validate an `.ash` File
To lex, parse, and run semantic analysis on an `.ash` file without simulating a specific machine:
```powershell
ash demo.ash
```
**Output:**
```text
Machines loaded:
 - [DFA] EndsWithZero
 - [DFA] StartsWithB
```

### 1.2 Execute / Simulate a DFA on Input Strings
Pass the `.ash` file path, the **DFA name**, and one or more **input strings** to simulate:
```powershell
ash demo.ash EndsWithZero "1010" "1011" "0"
```
**Output:**
```text
Simulating DFA 'EndsWithZero':
  Input "1010": ACCEPT | Trace: s0 --(1)--> s0 -> s0 --(0)--> s1 -> s1 --(1)--> s0 -> s0 --(0)--> s1
  Input "1011": REJECT | Trace: s0 --(1)--> s0 -> s0 --(0)--> s1 -> s1 --(1)--> s0 -> s0 --(1)--> s0
  Input "0": ACCEPT | Trace: s0 --(0)--> s1
```

To test the empty string ($\varepsilon$), pass `""`:
```powershell
ash demo.ash EndsWithZero "" "0"
```

### 1.3 View Source Code (`-code` / `--code`)
To view a specific machine's formatted `.ash` definition from the terminal:
```powershell
ash demo.ash EndsWithZero -code
```
To view the entire `.ash` file with line numbers:
```powershell
ash demo.ash -code
```

### 1.4 Show CLI Help
```powershell
ash --help
```

### 1.5 Run the Unit Test Suite
```powershell
pytest -v
```

---

## 2. Viewing Parse Trees & Tokens with ANTLR (`grun`)

`ash` includes built-in wrappers around ANTLR's TestRig (`grun` / `antlr4-parse`) so you can inspect how any `.ash` file is tokenized and parsed.

### 2.1 Visual Parse Tree GUI (`-gui` / `--gui`)
Opens an interactive graphical window displaying the complete parse tree diagram of your `.ash` file:
```powershell
ash demo.ash -gui
```

### 2.2 LISP-Style Text Parse Tree (`-tree` / `--tree`)
Prints the hierarchical parse tree directly in the terminal:
```powershell
ash demo.ash -tree
```

### 2.3 Lexer Token Stream (`-tokens` / `--tokens`)
Prints every token emitted by `AutomataLexer`, including token index, character offsets, literal text, token type, and `line:column` coordinates:
```powershell
ash demo.ash -tokens
```

### 2.4 Direct `antlr4-parse` & Regenerating Grammar Files
If you ever want to call `antlr4-parse` directly:
```powershell
antlr4-parse grammar/AutomataParser.g4 grammar/AutomataLexer.g4 program -gui demo.ash
```
If you modify `grammar/AutomataLexer.g4` or `grammar/AutomataParser.g4`, regenerate the Python lexer/parser/visitor files inside `grammar/`:
```powershell
cd grammar
antlr4 -Dlanguage=Python3 -visitor AutomataLexer.g4 AutomataParser.g4
```

---

## 3. Language Syntax & Format Specification

### 3.1 Lexical Rules
| Construct | Rule | Examples |
| :--- | :--- | :--- |
| **Comments** | Single-line or inline comments starting with `//` | `// This is a comment` |
| **Identifiers (`ID`)** | Starts with a letter or `_`, followed by letters, digits, or `_` | `s0`, `q_even`, `EndsWithZero` |
| **Strings (`STRING`)** | Double-quoted single-character symbols (supports `\` escapes) | `"0"`, `"a"`, `"\""`, `"\\"` |
| **Epsilon (`EPSILON`)** | Unquoted `\e` representing the empty string $\varepsilon$ | `q0 -> q1: \e`, `"0" \| \e` |
| **Whitespace** | Spaces, tabs, and newlines are ignored between tokens | — |

---

### 3.2 Declaring a DFA (`dfa`)

A Deterministic Finite Automaton is declared with the `dfa` keyword, an identifier name, and a block `{ ... }` containing its properties:

```ash
dfa EndsWithZero {
    states: s0, s1
    alphabet: "0", "1"
    start: s0
    accept: s1
    transitions: {
        s0 -> s1: "0"
        s0 -> s0: "1"
        s1 -> s1: "0"
        s1 -> s0: "1"
    }
}
```

#### Property Breakdown:
- **`states:`** Comma-separated list of state identifiers (`ID`).
- **`alphabet:`** Comma-separated list of double-quoted single-character symbols (`STRING`).
- **`start:`** A single state identifier (`ID`) representing the initial state $q_0$.
- **`accept:`** *(Optional)* Comma-separated list of accepting state identifiers ($F$). If omitted, the machine has $F = \emptyset$.
- **`transitions:`** *(Optional)* A block `{ ... }` of transition rules, each formatted as:
  ```ash
  <source_state> -> <target_state>: "<symbol>"
  ```
- **Flexible Ordering:** Properties inside `{ ... }` can be written in any order (e.g., `transitions:` can appear before `states:`).

---

### 3.3 Declaring an NFA (`nfa`)

A Non-deterministic Finite Automaton uses the identical block structure with the `nfa` keyword, permits multiple outgoing transitions from the same state on the same symbol, and supports `\e` ($\varepsilon$) transitions:

```ash
nfa EndsWithAA {
    states: q0, q1, q2, q3
    alphabet: "a", "b"
    start: q0
    accept: q3
    transitions: {
        q0 -> q0: "a"
        q0 -> q0: "b"
        q0 -> q1: \e
        q1 -> q2: "a"
        q2 -> q3: "a"
    }
}
```

---

### 3.4 Declaring a Regular Expression (`regex`)

Regular expressions are declared with the `regex` keyword, an identifier, `=`, and a regex expression:

```ash
regex HasOddOnes = ("0"* "1" "0"* "1" "0"*)* "0"* "1" "0"*
regex OptionalBit = ("0" | "1") | \e
```

#### Supported Regex Operators (Highest to Lowest Precedence):
1. **Grouping:** `( expr )`
2. **Quantifiers (Postfix):**
   - `expr*` — Kleene star (0 or more repetitions)
   - `expr+` — Plus (1 or more repetitions)
   - `expr?` — Optional (0 or 1 occurrence)
3. **Concatenation:** `expr1 expr2` (written adjacent to each other)
4. **Alternation (Union):** `expr1 | expr2`

---

## 4. Semantic & Runtime Rules Enforced

### Compile-Time Rules (`SemanticAnalyser`)
If any of the following rules are violated, compilation halts with a `SemanticError`:
1. **Unique Machine Names:** No two machines (`dfa`, `nfa`, or `regex`) may share the same identifier.
2. **Non-Empty States:** Every DFA/NFA must declare at least one state in `states:`.
3. **No Duplicate Declarations:**
   - No duplicate state names in `states:`.
   - No duplicate symbols in `alphabet:`.
   - No duplicate state names in `accept:`.
   - At most one `start:` state may be declared.
4. **Single-Character Alphabet Symbols:** Every symbol declared in `alphabet:` must be a single character (`len == 1`).
5. **State Referential Integrity:**
   - The `start` state must exist in `states:`.
   - Every state in `accept:` must exist in `states:`.
   - Every transition's `source` and `target` state must exist in `states:`.
6. **Transition Labels & Epsilon Rules:**
   - Every non-epsilon transition's `symbol` must be declared in `alphabet:`.
   - `\e` transitions are permitted in `nfa` declarations and rejected in `dfa` declarations.
7. **DFA Determinism:** A `dfa` cannot have two transitions with the same `(source, symbol)` pair.

### Runtime Execution Rules (`DFA`)
1. **Partial DFAs (Implicit Dead State):** You do not have to write transitions for every possible `(state, symbol)` pair. If a simulation encounters a `(state, symbol)` with no defined transition, the DFA immediately rejects (`REJECT`) the input string.
2. **Empty String ($\varepsilon$) Acceptance:** Passing `""` to a DFA returns `ACCEPT` if and only if the `start` state is also in `accept:`.
3. **Alphabet Guard:** Passing an input string containing a character not declared in the DFA's `alphabet:` raises a `ValueError`.
