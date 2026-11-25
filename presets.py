"""Preset NFA definitions for quick experimentation."""

PRESETS = {
    "Ends with '01'": {
        "description": "Accepts any binary string that terminates with '01'.",
        "states": ["q0", "q1", "q2"],
        "alphabet": ["0", "1"],
        "initial_states": ["q0"],
        "final_states": ["q2"],
        "transitions": {
            "q0": {"0": ["q0", "q1"], "1": ["q0"]},
            "q1": {"0": [], "1": ["q2"]},
            "q2": {"0": [], "1": []}
        },
        "sample_accepted": ["01", "001", "1101", "10101"],
        "sample_rejected": ["", "0", "1", "10", "0110"]
    },
    "Contains substring 'ab'": {
        "description": "Accepts strings containing at least one occurrence of 'ab'.",
        "states": ["q0", "q1", "q2"],
        "alphabet": ["a", "b"],
        "initial_states": ["q0"],
        "final_states": ["q2"],
        "transitions": {
            "q0": {"a": ["q0", "q1"], "b": ["q0"]},
            "q1": {"a": [], "b": ["q2"]},
            "q2": {"a": ["q2"], "b": ["q2"]}
        },
        "sample_accepted": ["ab", "aab", "babb", "baab"],
        "sample_rejected": ["", "a", "b", "ba", "bbba"]
    },
    "Second symbol from end is '1'": {
        "description": "Accepts binary strings where the second symbol from the right is '1'.",
        "states": ["q0", "q1", "q2"],
        "alphabet": ["0", "1"],
        "initial_states": ["q0"],
        "final_states": ["q2"],
        "transitions": {
            "q0": {"0": ["q0"], "1": ["q0", "q1"]},
            "q1": {"0": ["q2"], "1": ["q2"]},
            "q2": {"0": [], "1": []}
        },
        "sample_accepted": ["10", "11", "010", "1110"],
        "sample_rejected": ["", "0", "1", "01", "100", "1101"]
    },
    "ε-NFA: Language 0* 1* 2*": {
        "description": "Accepts strings of form 0* 1* 2* using ε-transitions between stages.",
        "states": ["q0", "q1", "q2"],
        "alphabet": ["0", "1", "2", "ε"],
        "initial_states": ["q0"],
        "final_states": ["q2"],
        "transitions": {
            "q0": {"0": ["q0"], "ε": ["q1"], "1": [], "2": []},
            "q1": {"1": ["q1"], "ε": ["q2"], "0": [], "2": []},
            "q2": {"2": ["q2"], "0": [], "1": [], "ε": []}
        },
        "sample_accepted": ["", "0", "1", "2", "012", "001122", "122"],
        "sample_rejected": ["210", "10", "20", "021"]
    },
    "Even number of '0's (DFA/NFA)": {
        "description": "Accepts binary strings containing an even count of '0's (including 0).",
        "states": ["q_even", "q_odd"],
        "alphabet": ["0", "1"],
        "initial_states": ["q_even"],
        "final_states": ["q_even"],
        "transitions": {
            "q_even": {"0": ["q_odd"], "1": ["q_even"]},
            "q_odd": {"0": ["q_even"], "1": ["q_odd"]}
        },
        "sample_accepted": ["", "1", "00", "1001", "0101"],
        "sample_rejected": ["0", "01", "000", "1011"]
    }
}
