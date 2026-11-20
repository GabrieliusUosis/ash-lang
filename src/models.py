from dataclasses import dataclass, field
from typing import Literal

EPSILON = ""

@dataclass(frozen=True, slots=True)
class Transition:
    source: str
    symbol: str
    target: str

@dataclass
class MachineSpec:
    name: str
    machine_type: Literal["DFA", "NFA"]
    states: list[str] = field(default_factory=list)
    alphabet: list[str] = field(default_factory=list)
    start: str | None = None
    accept: list[str] = field(default_factory=list)
    transitions: list[Transition] = field(default_factory=list)

@dataclass
class RegexSpec:
    name: str
    expression: str
    machine_type: str = "REGEX"

Spec = MachineSpec | RegexSpec
