from typing import Set, Dict, List, Optional, Any
import json

EPSILON_SYMBOLS = {"ε", "e", "λ", "", "epsilon"}

class NFA:
    def __init__(self, states: Set[str], alphabet: Set[str], 
                 transitions: Dict[str, Dict[str, Set[str]]],
                 initial_states: Set[str], final_states: Set[str]):
        self.states = set(states)
        self.alphabet = set(alphabet)
        # Normalize transitions: {state: {symbol: set_of_states}}
        self.transitions: Dict[str, Dict[str, Set[str]]] = {}
        for state in self.states:
            self.transitions[state] = {}
        for state, sym_dict in transitions.items():
            if state not in self.transitions:
                self.transitions[state] = {}
            for sym, next_set in sym_dict.items():
                self.transitions[state][sym] = set(next_set)
        
        self.initial_states = set(initial_states)
        self.final_states = set(final_states)

    def is_epsilon(self, symbol: str) -> bool:
        return symbol in EPSILON_SYMBOLS

    def epsilon_closure(self, states: Set[str]) -> Set[str]:
        """Compute the epsilon closure for a given set of states."""
        closure = set(states)
        stack = list(states)
        while stack:
            current = stack.pop()
            if current in self.transitions:
                for sym, next_states in self.transitions[current].items():
                    if self.is_epsilon(sym):
                        for nxt in next_states:
                            if nxt not in closure:
                                closure.add(nxt)
                                stack.append(nxt)
        return closure

    def process_string(self, input_string: str) -> bool:
        """Evaluate whether the given string is accepted by the NFA."""
        current_states = self.epsilon_closure(self.initial_states)
        for symbol in input_string:
            next_states = set()
            for state in current_states:
                if state in self.transitions and symbol in self.transitions[state]:
                    next_states.update(self.transitions[state][symbol])
            current_states = self.epsilon_closure(next_states)
            if not current_states:
                return False
        return bool(current_states & self.final_states)

    def step_by_step_trace(self, input_string: str) -> List[Dict[str, Any]]:
        """
        Produce a step-by-step trace of the NFA execution.
        Returns a list of dicts for step 0 (initial) through step N.
        """
        steps = []
        
        # Step 0: start with initial states & epsilon closure
        init_closure = self.epsilon_closure(self.initial_states)
        steps.append({
            "step": 0,
            "symbol": None,
            "remaining_input": input_string,
            "consumed_input": "",
            "active_states": sorted(list(init_closure)),
            "transitions_taken": [],
            "is_accepted": bool(init_closure & self.final_states),
            "is_dead_end": len(init_closure) == 0,
            "description": f"Start at initial states: {', '.join(sorted(self.initial_states)) or 'None'}" +
                           (f" (ε-closure: {', '.join(sorted(init_closure))})" if init_closure != self.initial_states else "")
        })

        current_states = init_closure
        for i, symbol in enumerate(input_string):
            next_states_raw = set()
            transitions_taken = []
            
            for state in current_states:
                if state in self.transitions and symbol in self.transitions[state]:
                    targets = self.transitions[state][symbol]
                    for target in targets:
                        transitions_taken.append({"from": state, "symbol": symbol, "to": target})
                        next_states_raw.add(target)
            
            next_closure = self.epsilon_closure(next_states_raw)
            # Find any epsilon transitions taken during closure
            closure_transitions = []
            if next_closure != next_states_raw:
                for st in next_closure:
                    if st in self.transitions:
                        for sym, targets in self.transitions[st].items():
                            if self.is_epsilon(sym):
                                for target in targets:
                                    if target in next_closure:
                                        closure_transitions.append({"from": st, "symbol": "ε", "to": target})

            current_states = next_closure
            is_dead = len(current_states) == 0
            is_acc = bool(current_states & self.final_states)

            steps.append({
                "step": i + 1,
                "symbol": symbol,
                "consumed_input": input_string[:i+1],
                "remaining_input": input_string[i+1:],
                "active_states": sorted(list(current_states)),
                "transitions_taken": transitions_taken,
                "closure_transitions": closure_transitions,
                "is_accepted": is_acc,
                "is_dead_end": is_dead,
                "description": f"Read symbol '{symbol}' → Active states: {', '.join(sorted(current_states)) if current_states else 'Trap state (∅)'}"
            })

            if is_dead and i < len(input_string) - 1:
                # Still record the remaining steps as dead ends if user wants to see them
                for j in range(i + 1, len(input_string)):
                    sym_rem = input_string[j]
                    steps.append({
                        "step": j + 1,
                        "symbol": sym_rem,
                        "consumed_input": input_string[:j+1],
                        "remaining_input": input_string[j+1:],
                        "active_states": [],
                        "transitions_taken": [],
                        "closure_transitions": [],
                        "is_accepted": False,
                        "is_dead_end": True,
                        "description": f"Read symbol '{sym_rem}' from dead end → Active states: ∅"
                    })
                break

        return steps

    def to_dict(self) -> Dict[str, Any]:
        """Serialize NFA to dictionary."""
        serialized_trans = {}
        for state, sym_map in self.transitions.items():
            serialized_trans[state] = {}
            for sym, targets in sym_map.items():
                serialized_trans[state][sym] = sorted(list(targets))
        return {
            "states": sorted(list(self.states)),
            "alphabet": sorted(list(self.alphabet)),
            "transitions": serialized_trans,
            "initial_states": sorted(list(self.initial_states)),
            "final_states": sorted(list(self.final_states))
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "NFA":
        """Reconstruct NFA from dictionary."""
        states = set(data.get("states", []))
        alphabet = set(data.get("alphabet", []))
        initial_states = set(data.get("initial_states", []))
        final_states = set(data.get("final_states", []))
        transitions: Dict[str, Dict[str, Set[str]]] = {}
        for st, sym_map in data.get("transitions", {}).items():
            transitions[st] = {}
            for sym, targets in sym_map.items():
                transitions[st][sym] = set(targets)
        return cls(states, alphabet, transitions, initial_states, final_states)

    def get_graph_data(self, active_states: Optional[Set[str]] = None, active_transitions: Optional[List[Dict[str, str]]] = None) -> Dict[str, Any]:
        """
        Produce node and edge data suitable for vis-network / cytoscape visualization.
        """
        active_states = active_states or set()
        active_trans_set = set()
        if active_transitions:
            for t in active_transitions:
                active_trans_set.add((t["from"], t["symbol"], t["to"]))

        nodes = []
        for state in sorted(list(self.states)):
            is_initial = state in self.initial_states
            is_final = state in self.final_states
            is_active = state in active_states

            label_parts = [state]
            if is_initial:
                label_parts.append("(Start)")
            if is_final:
                label_parts.append("(Accept)")

            node_def = {
                "id": state,
                "label": state,
                "title": f"State {state}" + (" [Initial]" if is_initial else "") + (" [Final]" if is_final else ""),
                "is_initial": is_initial,
                "is_final": is_final,
                "is_active": is_active,
            }
            nodes.append(node_def)

        edges = []
        edge_map: Dict[tuple, List[str]] = {}
        for from_state, sym_map in self.transitions.items():
            for sym, to_states in sym_map.items():
                for to_state in to_states:
                    key = (from_state, to_state)
                    if key not in edge_map:
                        edge_map[key] = []
                    edge_map[key].append(sym)

        for (u, v), symbols in edge_map.items():
            sym_label = ", ".join(sorted(symbols))
            is_edge_active = any((u, s, v) in active_trans_set for s in symbols)
            edges.append({
                "from": u,
                "to": v,
                "label": sym_label,
                "symbols": symbols,
                "is_active": is_edge_active
            })

        return {"nodes": nodes, "edges": edges}

    def visualize(self):
        """Optional Graphviz visualization for backward compatibility."""
        try:
            import importlib
            graphviz = importlib.import_module("graphviz")
            dot = graphviz.Digraph(format="png")
            dot.attr(rankdir='LR')
            dot.node('', shape='none')
            for state in self.initial_states:
                dot.edge('', state)
            for state in self.states:
                if state in self.final_states:
                    dot.node(state, shape='doublecircle')
                else:
                    dot.node(state, shape='circle')
            for from_state, symbol_dict in self.transitions.items():
                for symbol, to_states in symbol_dict.items():
                    for to_state in to_states:
                        dot.edge(from_state, to_state, label=symbol)
            return dot
        except (ImportError, Exception):
            return None
