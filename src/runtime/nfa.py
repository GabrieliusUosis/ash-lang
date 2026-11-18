def _escape_symbol(symbol: str) -> str:
    escapes = {"\\": "\\\\", '"': '\\"', "\n": "\\n", "\t": "\\t", "\r": "\\r"}
    return "".join(escapes.get(ch, ch) for ch in symbol)

class NFA:
    def __init__(self, name: str, states: list[str], alphabet: list[str], start: str, accept: list[str], transitions: list[dict]):
        self.name = name
        self.machine_type = "NFA"
        self.states = list(states)
        self.alphabet = list(alphabet)
        self.start = start
        self.accept = set(accept)
        self.transitions = list(transitions)

