from src.models import EPSILON, RegexSpec

def escape_symbol(symbol: str) -> str:
    escapes = {"\\": "\\\\", '"': '\\"', "\n": "\\n", "\t": "\\t", "\r": "\\r"}
    return "".join(escapes.get(ch, ch) for ch in symbol)
