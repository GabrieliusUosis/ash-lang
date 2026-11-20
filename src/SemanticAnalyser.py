from grammar.AutomataParserVisitor import AutomataParserVisitor
from src.formatter import unescape_string
from src.models import MachineSpec, RegexSpec, Transition

class SemanticError(Exception):
    """Raised when the parsed code is syntactically valid but logically flawed."""
    pass

class SemanticAnalyser(AutomataParserVisitor):
    def __init__(self):
        self.machines = {}
        self.current_machine = None

    def visitStatesDecl(self, ctx):
        states = [node.getText() for node in ctx.idList().ID()]
        for state in states:
            if state in self.current_machine.states:
                raise SemanticError(f"Duplicate state declared: '{state}'")
            self.current_machine.states.append(state)
        return states

    def visitAlphabetDecl(self, ctx):
        alphabet = [unescape_string(node.getText()) for node in ctx.stringList().STRING()]
        for symbol in alphabet:
            if symbol in self.current_machine.alphabet:
                raise SemanticError(f"Duplicate alphabet symbol declared: '{symbol}'")
            self.current_machine.alphabet.append(symbol)
        return alphabet

    def visitStartDecl(self, ctx):
        if getattr(self.current_machine, 'start', None) is not None:
            raise SemanticError("Multiple start states declared.")
        start_state = ctx.ID().getText()
        self.current_machine.start = start_state
        return start_state

    def visitAcceptDecl(self, ctx):
        accept_states = [node.getText() for node in ctx.idList().ID()]
        for state in accept_states:
            if state in self.current_machine.accept:
                raise SemanticError(f"Duplicate accept state declared: '{state}'")
            self.current_machine.accept.append(state)
        return accept_states

    def visitTransition(self, ctx):
        source = ctx.ID(0).getText()
        target = ctx.ID(1).getText()
        symbol = unescape_string(ctx.STRING().getText())

        transition_data = Transition(source=source, symbol=symbol, target=target)
        self.current_machine.transitions.append(transition_data)
        return transition_data

    def visitDfaDeclaration(self, ctx):
        machine_name = ctx.ID().getText()

        if machine_name in self.machines:
            raise SemanticError(f"Duplicate machine declaration: '{machine_name}' already exists.")

        self.current_machine = MachineSpec(machine_name, "DFA")
        try:
            self.visit(ctx.machineBody())
            self._validate_current_machine()
            self.machines[machine_name] = self.current_machine
            return self.machines[machine_name]
        finally:
            self.current_machine = None

    def _validate_current_machine(self):
        machine = self.current_machine

        if not machine.states:
            raise SemanticError("Machine must declare at least one state.")
        if not machine.start:
            raise SemanticError("Machine is missing a start state.")
        if machine.start not in machine.states:
            raise SemanticError(f"Start state '{machine.start}' is not declared in states list.")

        for state in machine.accept:
            if state not in machine.states:
                raise SemanticError(f"Accept state '{state}' is not declared in states list.")

        seen_transitions = set()
        for t in machine.transitions:
            if t.source not in machine.states:
                raise SemanticError(f"Transition source '{t.source}' is not declared in states list.")
            if t.target not in machine.states:
                raise SemanticError(f"Transition target '{t.target}' is not declared in states list.")
            if t.symbol not in machine.alphabet:
                raise SemanticError(f"Transition symbol '{t.symbol}' is not in the declared alphabet.")

            if machine.machine_type == "DFA":
                trans_key = (t.source, t.symbol)
                if trans_key in seen_transitions:
                    raise SemanticError(f"DFA determinism violation: State '{t.source}' has multiple transitions for symbol '{t.symbol}'.")
                seen_transitions.add(trans_key)

    def visitNfaDeclaration(self, ctx):
        machine_name = ctx.ID().getText()

        if machine_name in self.machines:
            raise SemanticError(f"Duplicate machine declaration: '{machine_name}' already exists.")

        self.current_machine = MachineSpec(machine_name, "NFA")
        try:
            self.visit(ctx.machineBody())
            self._validate_current_machine()
            self.machines[machine_name] = self.current_machine
            return self.machines[machine_name]
        finally:
            self.current_machine = None

    def visitRegexDeclaration(self, ctx):
        regex_name = ctx.ID().getText()

        if regex_name in self.machines:
            raise SemanticError(f"Duplicate declaration: '{regex_name}' already exists.")

        regex_expr = ctx.regexExpr().getText()
        self.machines[regex_name] = RegexSpec(name=regex_name, expression=regex_expr)
        return self.machines[regex_name]
