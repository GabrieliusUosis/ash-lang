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

    def epsilon_closure(self, states: set[str]) -> set[str]:
        closure = set(states)
        stack = list(states)

        while stack:
            state = stack.pop()
            for next_state in self._transition_table.get((state, EPSILON), ()):
                if next_state not in closure:
                    closure.add(next_state)
                    stack.append(next_state)

        return closure

    def _validate_word(self, word: str):
        for symbol in word:
            if symbol not in self._alphabet_set:
                raise ValueError(f"Symbol '{symbol}' is not in the alphabet of NFA '{self.name}'.")

    def step(self, states: set[str], symbol: str) -> set[str]:
        next_states: set[str] = set()
        for state in states:
            next_states.update(self._transition_table.get((state, symbol), ()))
        return self.epsilon_closure(next_states)

    def simulate(self, word: str) -> bool:
        self._validate_word(word)
        current_states = self.epsilon_closure({self.start})

        for symbol in word:
            current_states = self.step(current_states, symbol)
            if not current_states:
                return False

        return bool(current_states & self.accept)

    def to_ash(self) -> str:
        return format_machine(self)
