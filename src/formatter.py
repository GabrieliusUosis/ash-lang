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

def format_transition_label(symbol: str) -> str:
    if symbol == EPSILON:
        return r"\e"
    return f'"{escape_symbol(symbol)}"'

def format_machine(machine) -> str:
    if isinstance(machine, RegexSpec) or getattr(machine, "machine_type", None) == "REGEX":
        return f"regex {machine.name} = {machine.expression}"

    keyword = machine.machine_type.lower()
    accept_list = getattr(machine, "_accept_order", machine.accept)
    lines = [f"{keyword} {machine.name} {{"]
    lines.append(f"    states: {', '.join(machine.states)}")
    if machine.alphabet:
        formatted_alpha = ", ".join(f'"{escape_symbol(s)}"' for s in machine.alphabet)
        lines.append(f"    alphabet: {formatted_alpha}")
    lines.append(f"    start: {machine.start}")
    if accept_list:
        lines.append(f"    accept: {', '.join(accept_list)}")
    if machine.transitions:
        lines.append("    transitions: {")
        for t in machine.transitions:
            lines.append(f"        {t.source} -> {t.target}: {format_transition_label(t.symbol)}")
        lines.append("    }")
    lines.append("}")
    return "\n".join(lines)
