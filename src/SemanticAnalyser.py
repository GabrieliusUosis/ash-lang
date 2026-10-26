from grammar.AutomataParserVisitor import AutomataParserVisitor

class SemanticError(Exception):
    """Raised when the parsed code is syntactically valid but logically flawed."""
    pass

class MachineData:
    def __init__(self, name, machine_type):
        self.name = name
        self.machine_type = machine_type
        self.states = []
        self.alphabet = []
        self.start = None
        self.accept = []
        self.transitions = []

class SemanticAnalyser(AutomataParserVisitor):
    def __init__(self):
        self.machines = {}
        self.current_machine = None

    def visitDfaDeclaration(self, ctx):
        # Extract the DFA name from the ID token defined in the grammar
        machine_name = ctx.ID().getText() 
        self.current_machine = MachineData(machine_name, "DFA")
        
        # Traverse the machineBody to populate the current_machine properties
        self.visit(ctx.machineBody())
        
        # Save the fully populated machine and clear the current context
        self.machines[machine_name] = self.current_machine
        self.current_machine = None
        
        return self.machines[machine_name]

    def visitStatesDecl(self, ctx):
        # Extract all state IDs from the idList context
        states = [node.getText() for node in ctx.idList().ID()]
        self.current_machine.states.extend(states)
        return states

    def visitAlphabetDecl(self, ctx):
        # Extract all alphabet symbols from the stringList, stripping the double quotes
        alphabet = [node.getText().strip('"') for node in ctx.stringList().STRING()]
        self.current_machine.alphabet.extend(alphabet)
        return alphabet

    def visitStartDecl(self, ctx):
        # Extract the single start state ID
        start_state = ctx.ID().getText()
        self.current_machine.start = start_state
        return start_state

    def visitAcceptDecl(self, ctx):
        # Extract all accept state IDs from the idList context
        accept_states = [node.getText() for node in ctx.idList().ID()]
        self.current_machine.accept.extend(accept_states)
        return accept_states

    def visitTransition(self, ctx):
        # Extract source ID, target ID, and the transition symbol
        source = ctx.ID(0).getText()
        target = ctx.ID(1).getText()
        symbol = ctx.STRING().getText().strip('"')
        
        transition_data = {
            "source": source,
            "symbol": symbol,
            "target": target
        }
        
        self.current_machine.transitions.append(transition_data)
        return transition_data

    def visitDfaDeclaration(self, ctx):
        machine_name = ctx.ID().getText()
        
        if machine_name in self.machines:
            raise SemanticError(f"Duplicate machine declaration: '{machine_name}' already exists.")
            
        self.current_machine = MachineData(machine_name, "DFA")
        self.visit(ctx.machineBody())
        
        # Run validation before saving
        self._validate_current_machine()
        
        self.machines[machine_name] = self.current_machine
        self.current_machine = None
        return self.machines[machine_name]

    def _validate_current_machine(self):
        machine = self.current_machine
        
        # Validate Start State
        if machine.start and machine.start not in machine.states:
            raise SemanticError(f"Start state '{machine.start}' is not declared in states list.")
            
        # Validate Accept States
        for state in machine.accept:
            if state not in machine.states:
                raise SemanticError(f"Accept state '{state}' is not declared in states list.")
                
        # Validate Transitions
        for t in machine.transitions:
            if t["source"] not in machine.states:
                raise SemanticError(f"Transition source '{t['source']}' is not declared in states list.")
            if t["target"] not in machine.states:
                raise SemanticError(f"Transition target '{t['target']}' is not declared in states list.")
            if t["symbol"] not in machine.alphabet:
                raise SemanticError(f"Transition symbol '{t['symbol']}' is not in the declared alphabet.")

    def visitNfaDeclaration(self, ctx):
        machine_name = ctx.ID().getText()
        
        if machine_name in self.machines:
            raise SemanticError(f"Duplicate machine declaration: '{machine_name}' already exists.")
            
        self.current_machine = MachineData(machine_name, "NFA")
        self.visit(ctx.machineBody())
        
        # Reuse the identical validation logic for NFAs
        self._validate_current_machine()
        
        self.machines[machine_name] = self.current_machine
        self.current_machine = None
        return self.machines[machine_name]

    def visitRegexDeclaration(self, ctx):
        regex_name = ctx.ID().getText()
        
        if regex_name in self.machines:
            raise SemanticError(f"Duplicate declaration: '{regex_name}' already exists.")
            
        # Extract the raw expression text from the regexExpr rule
        regex_expr = ctx.regexExpr().getText()
        
        # Store regex properties in the machines dictionary
        self.machines[regex_name] = {
            "type": "REGEX", 
            "name": regex_name, 
            "expression": regex_expr
        }
        return self.machines[regex_name]