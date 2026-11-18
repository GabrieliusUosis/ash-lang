import os
import subprocess
import sys
from antlr4 import InputStream, FileStream, CommonTokenStream
from antlr4.error.ErrorListener import ErrorListener
from grammar.AutomataLexer import AutomataLexer
from grammar.AutomataParser import AutomataParser
from src.SemanticAnalyser import SemanticAnalyser, SemanticError
from src.runtime.dfa import DFA, _escape_symbol

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class StrictErrorListener(ErrorListener):
    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        raise SyntaxError(f"Syntax error at line {line}:{column} - {msg}")

def ensure_file_exists(file_path: str) -> str:
    if not os.path.isfile(file_path):
        print(f"Error: File '{file_path}' not found.")
        sys.exit(1)
    return file_path

def run_grun(file_path: str, flag: str = "-tree"):
    """Invokes ANTLR's TestRig (grun / antlr4-parse) on the given .ash file."""
    cmd = [
        "antlr4-parse",
        os.path.join(BASE_DIR, "grammar", "AutomataParser.g4"),
        os.path.join(BASE_DIR, "grammar", "AutomataLexer.g4"),
        "program",
        flag,
        ensure_file_exists(file_path),
    ]
    subprocess.run(cmd, check=True)

def print_file_code(file_path: str):
    valid_path = ensure_file_exists(file_path)
    with open(valid_path, encoding="utf-8") as f:
        for idx, line in enumerate(f, start=1):
            print(f"{idx:3d} | {line.rstrip()}")

def format_machine_code(machine) -> str:
    if hasattr(machine, "to_ash"):
        return machine.to_ash()
    if isinstance(machine, dict) and machine.get("type") == "REGEX":
        return f"regex {machine['name']} = {machine['expression']}"
    keyword = getattr(machine, "machine_type", "nfa").lower()
    lines = [f"{keyword} {machine.name} {{"]
    lines.append(f"    states: {', '.join(machine.states)}")
    if machine.alphabet:
        formatted_alpha = ", ".join(f'"{_escape_symbol(s)}"' for s in machine.alphabet)
        lines.append(f"    alphabet: {formatted_alpha}")
    lines.append(f"    start: {machine.start}")
    if machine.accept:
        lines.append(f"    accept: {', '.join(machine.accept)}")
    if machine.transitions:
        lines.append("    transitions: {")
        for t in machine.transitions:
            lines.append(f'        {t["source"]} -> {t["target"]}: "{_escape_symbol(t["symbol"])}"')
        lines.append("    }")
    lines.append("}")
    return "\n".join(lines)

def parse_code(source_code: str = None, file_path: str = None) -> dict:
    stream = FileStream(ensure_file_exists(file_path), encoding='utf-8') if file_path else InputStream(source_code)
        
    lexer = AutomataLexer(stream)
    lexer.removeErrorListeners()
    lexer.addErrorListener(StrictErrorListener())
    
    token_stream = CommonTokenStream(lexer)
    
    parser = AutomataParser(token_stream)
    parser.removeErrorListeners()
    parser.addErrorListener(StrictErrorListener())
    
    try:
        tree = parser.program()
    except SyntaxError as e:
        print(f"Compilation aborted: {e}")
        sys.exit(1)
        
    analyzer = SemanticAnalyser()
    try:
        analyzer.visit(tree)
    except SemanticError as e:
        print(f"Compiler Error: {e}")
        sys.exit(1)

    runtime_machines = {}
    print("Machines loaded:")
    for name, machine in analyzer.machines.items():
        m_type = getattr(machine, "machine_type", machine.get("type") if isinstance(machine, dict) else "UNKNOWN")
        if m_type == "DFA":
            runtime_machines[name] = DFA.from_machine_data(machine)
        else:
            runtime_machines[name] = machine
        print(f" - [{m_type}] {name}")

    return runtime_machines

def run_simulation(machine: DFA, words: list[str]):
    print(f"\nSimulating DFA '{machine.name}':")
    for word in words:
        try:
            accepted, path = machine.trace(word)
            status = "ACCEPT" if accepted else "REJECT"
            steps = " -> ".join([f"{src} --({sym})--> {tgt}" for src, sym, tgt in path]) or f"{machine.start} (no transitions)"
            print(f'  Input "{word}": {status} | Trace: {steps}')
        except ValueError as e:
            print(f'  Input "{word}": ERROR ({e})')

#def run_simulation(machine: NFA, words: list[str]):
    #print(f"\nSimulating NFA '{machine.name}':")
    #pass

def main():
    if len(sys.argv) > 1:
        file_arg = sys.argv[1]
        if len(sys.argv) == 3 and sys.argv[2] in ("-tree", "-tokens", "-gui"):
            run_grun(file_arg, sys.argv[2])
            sys.exit(0)
        if len(sys.argv) == 3 and sys.argv[2] == "-code":
            print_file_code(file_arg)
            sys.exit(0)

        machines = parse_code(file_path=file_arg)
        if len(sys.argv) == 4 and sys.argv[3] == "-code":
            target_name = sys.argv[2]
            if target_name not in machines:
                print(f"Error: Machine '{target_name}' not found.")
                sys.exit(1)
            print(f"\n{format_machine_code(machines[target_name])}")
            sys.exit(0)

        if len(sys.argv) >= 4:
            target_name = sys.argv[2]
            test_words = sys.argv[3:]
            if target_name not in machines:
                print(f"Error: Machine '{target_name}' not found.")
                sys.exit(1)
            target_machine = machines[target_name]
            if not isinstance(target_machine, DFA):
                print(f"Error: Machine '{target_name}' is not a DFA.")
                sys.exit(1)
            run_simulation(target_machine, test_words)

if __name__ == "__main__":
    main()
