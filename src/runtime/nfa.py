from src.formatter import format_machine
from src.models import EPSILON, MachineSpec, Transition

class NFA:
    """Formal representation of a Non-deterministic Finite Automaton: (Q, Σ, δ, q0, F)."""

    def __init__(self, name: str, states: list[str], alphabet: list[str], start: str, accept: list[str], transitions: list[Transition | dict]):
        self.name = name
        self.machine_type = "NFA"
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

        # δ(q, σ) -> P(Q) mapped as {(source, symbol): set[target]}
        self._transition_table: dict[tuple[str, str], set[str]] = {}
        for t in self.transitions:
            self._transition_table.setdefault((t.source, t.symbol), set()).add(t.target)

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

    def to_ash(self) -> str:
        return format_machine(self)
