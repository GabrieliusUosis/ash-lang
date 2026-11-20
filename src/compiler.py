import os
from antlr4 import CommonTokenStream, InputStream
from antlr4.error.ErrorListener import ErrorListener
from grammar.AutomataLexer import AutomataLexer
from grammar.AutomataParser import AutomataParser
from src.runtime.dfa import DFA
from src.runtime.nfa import NFA
from src.semantic_analyser import SemanticAnalyser

class StrictErrorListener(ErrorListener):
    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        raise SyntaxError(f"Syntax error at line {line}:{column} - {msg}")

def tokenize_source(source_code: str, strict: bool = False) -> list[tuple[str, str]]:
    lexer = AutomataLexer(InputStream(source_code))
    if strict:
        lexer.removeErrorListeners()
        lexer.addErrorListener(StrictErrorListener())
    return [(lexer.symbolicNames[t.type], t.text) for t in lexer.getAllTokens()]

def parse_source(source_code: str):
    lexer = AutomataLexer(InputStream(source_code))
    lexer.removeErrorListeners()
    lexer.addErrorListener(StrictErrorListener())

    parser = AutomataParser(CommonTokenStream(lexer))
    parser.removeErrorListeners()
    parser.addErrorListener(StrictErrorListener())
    return parser.program()

def compile_source(source_code: str) -> dict:
    tree = parse_source(source_code)
    analyzer = SemanticAnalyser()
    analyzer.visit(tree)

    runtime_machines = {}
    for name, spec in analyzer.machines.items():
        if spec.machine_type == "DFA":
            runtime_machines[name] = DFA.from_spec(spec)
        elif spec.machine_type == "NFA":
            runtime_machines[name] = NFA.from_spec(spec)
        else:
            runtime_machines[name] = spec
    return runtime_machines

def compile_file(file_path: str) -> dict:
    if not os.path.isfile(file_path):
        raise FileNotFoundError(file_path)
    with open(file_path, encoding="utf-8") as f:
        return compile_source(f.read())
