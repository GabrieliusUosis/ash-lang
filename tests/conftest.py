import itertools
from src.compiler import compile_source, parse_source, tokenize_source
from src.runtime.dfa import DFA
from src.runtime.nfa import NFA

def tokenize(text: str, strict: bool = False) -> list[str]:
    return [token_type for token_type, _ in tokenize_source(text, strict=strict)]

def tokenize_pairs(text: str, strict: bool = False) -> list[tuple[str, str]]:
    return tokenize_source(text, strict=strict)

def get_parse_tree(source_code: str):
    return parse_source(source_code)

def compile_dfa(code: str, name: str) -> DFA:
    return compile_source(code)[name]

def compile_nfa(code: str, name: str) -> NFA:
    return compile_source(code)[name]

def all_words(alphabet: str, max_len: int):
    for length in range(max_len + 1):
        for chars in itertools.product(alphabet, repeat=length):
            yield "".join(chars)
