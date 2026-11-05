import subprocess
import sys
from antlr4 import InputStream, FileStream, CommonTokenStream
from antlr4.error.ErrorListener import ErrorListener
from grammar.AutomataLexer import AutomataLexer
from grammar.AutomataParser import AutomataParser
from src.SemanticAnalyser import SemanticAnalyser, SemanticError
from src.runtime.dfa import DFA

class StrictErrorListener(ErrorListener):
    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        raise SyntaxError(f"Syntax error at line {line}:{column} - {msg}")

def run_grun(file_path: str, flag: str = "-tree"):
    """Invokes ANTLR's TestRig (grun / antlr4-parse) on the given .ash file."""
    cmd = [
        "antlr4-parse",
        "grammar/AutomataParser.g4",
        "grammar/AutomataLexer.g4",
        "program",
        flag,
        file_path,
    ]
    subprocess.run(cmd, check=True)

def parse_code(source_code: str = None, file_path: str = None) -> dict:
    stream = FileStream(file_path, encoding='utf-8') if file_path else InputStream(source_code)
        
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
    print("Semantic analysis complete. Valid machines loaded:")
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

if __name__ == "__main__":
    if len(sys.argv) > 1:
        file_arg = sys.argv[1]
        if len(sys.argv) == 3 and sys.argv[2] in ("-tree", "-tokens", "-gui"):
            run_grun(file_arg, sys.argv[2])
            sys.exit(0)

        machines = parse_code(file_path=file_arg)
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
    else:
        sample_code = """
        dfa M1 { 
            states: q0, q1
            alphabet: "a", "b"
            start: q0
            accept: q1
            transitions: {
                q0 -> q1: "a"
            }
        }
        """
        machines = parse_code(source_code=sample_code)
        run_simulation(machines["M1"], ["a", "b"])
