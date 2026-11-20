import argparse
import os
import subprocess
import sys
from src.compiler import compile_file
from src.formatter import format_machine
from src.runtime.dfa import DFA
from src.runtime.nfa import NFA
from src.semantic_analyser import SemanticError

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def run_grun(file_path: str, flag: str = "-tree"):
    if not os.path.isfile(file_path):
        raise FileNotFoundError(file_path)
    cmd = [
        "antlr4-parse",
        os.path.join(BASE_DIR, "grammar", "AutomataParser.g4"),
        os.path.join(BASE_DIR, "grammar", "AutomataLexer.g4"),
        "program",
        flag,
        file_path,
    ]
    subprocess.run(cmd, check=True)

def print_file_code(file_path: str):
    if not os.path.isfile(file_path):
        raise FileNotFoundError(file_path)
    with open(file_path, encoding="utf-8") as f:
        for idx, line in enumerate(f, start=1):
            print(f"{idx:3d} | {line.rstrip()}")

def _format_state(node: str | set[str]) -> str:
    if isinstance(node, set):
        return "{" + ", ".join(sorted(node)) + "}"
    return node

def run_simulation(machine: DFA | NFA, words: list[str]):
    print(f"\nSimulating {machine.machine_type} '{machine.name}':")
    for word in words:
        try:
            accepted, path = machine.trace(word)
            status = "ACCEPT" if accepted else "REJECT"
            initial = machine.epsilon_closure({machine.start}) if isinstance(machine, NFA) else machine.start
            steps = " -> ".join([f"{_format_state(src)} --({sym})--> {_format_state(tgt)}" for src, sym, tgt in path]) or f"{_format_state(initial)} (no transitions)"
            print(f'  Input "{word}": {status} | Trace: {steps}')
        except ValueError as e:
            print(f'  Input "{word}": ERROR ({e})')

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ash",
        description="Declarative automata workbench CLI",
        allow_abbrev=False,
    )
    parser.add_argument("file", nargs="?", help="Path to the .ash source file")
    parser.add_argument("machine", nargs="?", help="Machine name to inspect or simulate")
    parser.add_argument("words", nargs="*", help="Input strings to simulate")
    parser.add_argument("-code", "--code", action="store_true", help="Print file or machine source code")
    parser.add_argument("-tree", "--tree", action="store_true", help="Print ANTLR parse tree")
    parser.add_argument("-tokens", "--tokens", action="store_true", help="Print ANTLR lexer tokens")
    parser.add_argument("-gui", "--gui", action="store_true", help="Open ANTLR visual parse tree GUI")
    return parser

def main(argv: list[str] | None = None):
    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.file:
        parser.print_help()
        return

    try:
        for flag_name, grun_flag in (("tree", "-tree"), ("tokens", "-tokens"), ("gui", "-gui")):
            if getattr(args, flag_name):
                run_grun(args.file, grun_flag)
                return

        if args.code and not args.machine:
            print_file_code(args.file)
            return

        machines = compile_file(args.file)
        print("Machines loaded:")
        for name, machine in machines.items():
            print(f" - [{machine.machine_type}] {name}")

        if args.code:
            if args.machine not in machines:
                print(f"Error: Machine '{args.machine}' not found.", file=sys.stderr)
                sys.exit(1)
            print(f"\n{format_machine(machines[args.machine])}")
            return

        if args.machine:
            if args.machine not in machines:
                print(f"Error: Machine '{args.machine}' not found.", file=sys.stderr)
                sys.exit(1)
            target = machines[args.machine]
            if not isinstance(target, (DFA, NFA)):
                print(f"Error: Machine '{args.machine}' is not a runnable DFA or NFA.", file=sys.stderr)
                sys.exit(1)
            if args.words:
                run_simulation(target, args.words)

    except FileNotFoundError:
        print(f"Error: File '{args.file}' not found.", file=sys.stderr)
        sys.exit(1)
    except SyntaxError as e:
        print(f"Compilation aborted: {e}", file=sys.stderr)
        sys.exit(1)
    except SemanticError as e:
        print(f"Compiler Error: {e}", file=sys.stderr)
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"ANTLR tool failed with exit code {e.returncode}.", file=sys.stderr)
        sys.exit(e.returncode)
