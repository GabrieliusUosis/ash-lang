class DFA:
    """Formal representation of a Deterministic Finite Automaton: (Q, Σ, δ, q0, F)."""

    def __init__(self, name: str, states: list[str], alphabet: list[str], start: str, accept: list[str], transitions: list[dict]):
        self.name = name
        self.machine_type = "DFA"
        self.states = list(states)
        self.alphabet = list(alphabet)
        self.start = start
        self.accept = set(accept)
        self.transitions = list(transitions)

        # δ(q, σ) -> q' mapped as {(source, symbol): target} for O(1) lookup
        self._transition_table = {
            (t["source"], t["symbol"]): t["target"]
            for t in self.transitions
        }

    @classmethod
    def from_machine_data(cls, machine_data):
        return cls(
            name=machine_data.name,
            states=machine_data.states,
            alphabet=machine_data.alphabet,
            start=machine_data.start,
            accept=machine_data.accept,
            transitions=machine_data.transitions,
        )

    def step(self, state: str, symbol: str) -> str | None:
        return self._transition_table.get((state, symbol))

    def simulate(self, word: str) -> bool:
        current_state = self.start

        for symbol in word:
            if symbol not in self.alphabet:
                raise ValueError(f"Symbol '{symbol}' is not in the alphabet of DFA '{self.name}'.")

            current_state = self.step(current_state, symbol)
            if current_state is None:
                return False

        return current_state in self.accept

    def trace(self, word: str) -> tuple[bool, list[tuple[str, str, str]]]:
        current_state = self.start
        path = []

        for symbol in word:
            if symbol not in self.alphabet:
                raise ValueError(f"Symbol '{symbol}' is not in the alphabet of DFA '{self.name}'.")

            next_state = self.step(current_state, symbol)
            if next_state is None:
                return False, path

            path.append((current_state, symbol, next_state))
            current_state = next_state

        return current_state in self.accept, path
