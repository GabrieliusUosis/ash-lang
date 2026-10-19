from antlr4 import InputStream, CommonTokenStream
from grammar.AutomataLexer import AutomataLexer
from grammar.AutomataParser import AutomataParser

def parse_code(source_code: str):
    #Lexical Analysis stage
    stream = InputStream(source_code)
    lexer = AutomataLexer(stream)
    token_stream = CommonTokenStream(lexer)
    
    #Syntax Analysis (Parsing) stage
    parser = AutomataParser(token_stream)
    tree = parser.program()
    
    print(tree.toStringTree(recog=parser))

if __name__ == "__main__":
    sample_code = "dfa M1 { start: q0 }"
    parse_code(sample_code)