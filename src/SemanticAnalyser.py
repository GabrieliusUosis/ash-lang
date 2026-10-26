from grammar.AutomataParserVisitor import AutomataParserVisitor

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