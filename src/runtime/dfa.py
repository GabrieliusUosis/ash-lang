from src.models import MachineSpec, Transition

def _escape_symbol(symbol: str) -> str:
    escapes = {"\\": "\\\\", '"': '\\"', "\n": "\\n", "\t": "\\t", "\r": "\\r"}
    return "".join(escapes.get(ch, ch) for ch in symbol)

class DFA:
    """Formal representation of a Deterministic Finite Automaton: (Q, Σ, δ, q0, F)."""

    def __init__(self, name: str, states: list[str], alphabet: list[str], start: str, accept: list[str], transitions: list[Transition | dict]):
        self.name = name
        self.machine_type = "DFA"
        self.states = list(states)
        self.alphabet = list(alphabet)
        self._alphabet_set = set(alphabet)
        self.start = start
        self._accept_order = list(accept)
        self.accept = set(accept)
        self.transitions = [
            t if isinstance(t, Transition) else Transition(t["source"], t["symbol"], t["target"])
            for t in transitions
        ]

        # δ(q, σ) -> q' mapped as {(source, symbol): target} for O(1) lookup
        self._transition_table = {
            (t.source, t.symbol): t.target
            for t in self.transitions
        }

    @classmethod
    def from_spec(cls, spec: MachineSpec):
        return cls(
            name=spec.name,
            states=spec.states,
            alphabet=spec.alphabet,
            start=spec.start,
            accept=spec.accept,
            transitions=spec.transitions,
        )

    from_machine_data = from_spec

    def step(self, state: str, symbol: str) -> str | None:
        return self._transition_table.get((state, symbol))

    def _validate_word(self, word: str):
        for symbol in word:
            if symbol not in self._alphabet_set:
                raise ValueError(f"Symbol '{symbol}' is not in the alphabet of DFA '{self.name}'.")

    def simulate(self, word: str) -> bool:
        self._validate_word(word)
        current_state = self.start

        for symbol in word:
            current_state = self.step(current_state, symbol)
            if current_state is None:
                return False

        return current_state in self.accept

    def trace(self, word: str) -> tuple[bool, list[tuple[str, str, str]]]:
        self._validate_word(word)
        current_state = self.start
        path = []

        for symbol in word:
            next_state = self.step(current_state, symbol)
            if next_state is None:
                return False, path

            path.append((current_state, symbol, next_state))
            current_state = next_state

        return current_state in self.accept, path

    def to_ash(self) -> str:
        lines = [f"dfa {self.name} {{"]
        lines.append(f"    states: {', '.join(self.states)}")
        if self.alphabet:
            formatted_alpha = ", ".join(f'"{_escape_symbol(s)}"' for s in self.alphabet)
            lines.append(f"    alphabet: {formatted_alpha}")
        lines.append(f"    start: {self.start}")
        if self._accept_order:
            lines.append(f"    accept: {', '.join(self._accept_order)}")
        if self.transitions:
            lines.append("    transitions: {")
            for t in self.transitions:
                lines.append(f'        {t.source} -> {t.target}: "{_escape_symbol(t.symbol)}"')
            lines.append("    }")
        lines.append("}")
        return "\n".join(lines)
