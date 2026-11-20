from src.models import EPSILON, RegexSpec

def escape_symbol(symbol: str) -> str:
    escapes = {"\\": "\\\\", '"': '\\"', "\n": "\\n", "\t": "\\t", "\r": "\\r"}
    return "".join(escapes.get(ch, ch) for ch in symbol)

def unescape_string(token_text: str) -> str:
    inner = token_text[1:-1]
    escapes = {"n": "\n", "t": "\t", "r": "\r", "\\": "\\", '"': '"'}
    out = []
    i = 0
    while i < len(inner):
        if inner[i] == "\\" and i + 1 < len(inner):
            out.append(escapes.get(inner[i + 1], inner[i + 1]))
            i += 2
        else:
            out.append(inner[i])
            i += 1
    return "".join(out)
