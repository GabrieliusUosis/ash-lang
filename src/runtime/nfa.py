def _escape_symbol(symbol: str) -> str:
    escapes = {"\\": "\\\\", '"': '\\"', "\n": "\\n", "\t": "\\t", "\r": "\\r"}
    return "".join(escapes.get(ch, ch) for ch in symbol)

class NFA:
    def __init__(self, name: str, start: str, accept: set[str], transitions: list[dict]):
        self.name = name
        self.start = start
        self.accept = accept
        self.transitions = transitions

    def __str__(self):
        lines = [f"NFA {self.name} {{"]
        lines.append(f"    start: {self.start}")
        if self.accept:
            lines.append(f"    accept: {', '.join(self.accept)}")
        if self.transitions:
            lines.append("    transitions: {")
            for t in self.transitions:
                lines.append(f'        {t["source"]} -> {t["target"]}: "{_escape_symbol(t["symbol"])}"')
            lines.append("    }")
        lines.append("}")
        return "\n".join(lines)