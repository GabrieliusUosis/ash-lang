import sys
from antlr4 import InputStream, FileStream, CommonTokenStream
from grammar.AutomataLexer import AutomataLexer
from grammar.AutomataParser import AutomataParser

def parse_code(source_code: str = None, file_path: str = None):
    if file_path:
        stream = FileStream(file_path, encoding='utf-8')
    else:
        stream = InputStream(source_code)
        
    lexer = AutomataLexer(stream)
    token_stream = CommonTokenStream(lexer)
    
    parser = AutomataParser(token_stream)
    tree = parser.program()
    
    print(tree.toStringTree(recog=parser))

if __name__ == "__main__":
    if len(sys.argv) > 1:
        parse_code(file_path=sys.argv[1])
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
        regex R1 = (a|b)*
        """
        parse_code(source_code=sample_code)