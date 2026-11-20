from dataclasses import dataclass

EPSILON = ""

@dataclass(frozen=True, slots=True)
class Transition:
    source: str
    symbol: str
    target: str
