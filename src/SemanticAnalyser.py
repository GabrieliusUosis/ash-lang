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