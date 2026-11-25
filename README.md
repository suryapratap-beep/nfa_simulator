# NFA Studio: Interactive NFA & ε-NFA Simulator (Group ID: [Insert Group ID])

**CSET302 – Automata Theory and Computability**  
*School of Computer Science Engineering and Technology (SCSET), Bennett University*  
*Milestone-II: Final Simulator Demonstration & Evaluation*

---

## Overview: What does the simulator do?

**NFA Studio** is an interactive, browser-based simulation, design, and visualization platform for **Non-Deterministic Finite Automata (NFA)** and **$\epsilon$-NFAs**. 

Unlike standard deterministic finite automata (DFA), an NFA can branch into multiple simultaneous states on a single input symbol or transition without consuming any input ($\epsilon$-transitions). Static textbook diagrams and paper-and-pencil traces fail to convey this multi-path concurrency clearly. 

NFA Studio resolves this by providing:
- **Interactive Graph Canvas**: Direct visual representation of states and transitions powered by hardware-accelerated physics, enabling dragging, panning, zooming, and zero dependency on crashing external binaries.
- **Concurrent Step-by-Step Stepper**: A tape-head player that steps through an input string character by character, dynamically highlighting active branch states with an amber glow in real time.
- **Full $\epsilon$-NFA Capabilities**: Automatic, fixed-point calculation of $\epsilon$-closures ($\text{E-CLOSE}$) on initial states and intermediate transitions.
- **Visual Matrix Editor & Preset Benchmarks**: A live transition table matrix, 1-click test suites, and JSON import/export for saving and loading custom automata.

---

## Supported features: list implemented operations

1. **Formal 5-Tuple Definition**: Complete specification of $M = (Q, \Sigma, \delta, Q_0, F)$ with user-configurable states and alphabets.
2. **Non-Deterministic Transition Function**: Supports mapping $\delta: Q \times (\Sigma \cup \{\epsilon\}) \to \mathcal{P}(Q)$, allowing transitions to multiple destination states ($\{q_1, q_2\}$) or to no states ($\emptyset$, trap condition).
3. **Multi-State Initial and Final Sets**: Supports multiple starting states ($Q_0 \subseteq Q$) and multiple accepting states ($F \subseteq Q$).
4. **Iterative $\epsilon$-Closure Computation**: Implements a worklist graph traversal algorithm to compute complete reachable state closures over $\epsilon$ / lambda transitions.
5. **Interactive Step-by-Step Stepper**:
   - Navigation controls: **Start (`⏮️`)**, **Previous (`◀️`)**, **Next (`▶️`)**, **End (`⏭️`)**, and a scrub slider.
   - **Visual Tape Head**: Renders string cells with an animated pointer ($\downarrow$) tracking consumed vs. active characters.
   - **Real-Time Active Node Glow**: Visual graph nodes highlight dynamically at each step, distinguishing currently active branches from dormant states.
   - **Step History Trace**: Detailed tabular log showing step index, symbol read, active state subset, transition branches taken, and acceptance status.
6. **Embedded Interactive Visualization**:
   - In-browser Vis-network canvas with force-directed physics layout.
   - Node classification: Initial states marked with a green `START` pointer; final states styled with double emerald rings; active states pulsing in bright amber.
   - Zero dependence on external Graphviz `dot` binary installations.
7. **Transition Matrix & Direct Editor**:
   - Comprehensive $|Q| \times |\Sigma \cup \{\epsilon\}|$ matrix view.
   - Transition editor form allowing multi-selection of target states.
8. **Curated Preset Automata Library**:
   - Pre-loaded benchmark models (*Ends with '01'*, *Contains substring 'ab'*, *Second symbol from end is '1'*, *$\epsilon$-NFA for $0^*1^*2^*$*, *Even number of '0's*).
   - One-click sample test buttons for accepted and rejected test strings.
9. **Automaton Serialization**:
   - Export custom automata to formatted `.json`.
   - Import previously saved JSON configurations.

---

## Technology stack and dependencies: versions

- **Language**: Python 3.8+ (Tested on Python 3.13)
- **Web Application Framework**: [Streamlit](https://streamlit.io/) (`>= 1.30.0`, verified with `1.51.0`)
- **Data Manipulation**: [Pandas](https://pandas.pydata.org/) (`>= 2.0.0`)
- **Interactive Graph Renderer**: [Vis-network](https://visjs.github.io/vis-network/standalone/) (`v9.1.2`, loaded via `streamlit.components.v1.html`)
- **Diagram Fallback**: [Graphviz Python](https://pypi.org/project/graphviz/) (`0.21`, dynamically loaded fallback)
- **Standard Library Components**: `json`, `typing`, `subprocess`, `sys`, `os`

---

## Installation: numbered setup commands

1. **Clone or navigate to the project directory**:
   ```bash
   cd /Users/suryapratapsingh/aiml/nfa_simulator-main
   ```

2. **(Optional but recommended) Create and activate a Python virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install the required dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
   *(Note: Unlike legacy simulators, you do **not** need to install external OS packages like `brew install graphviz`, as graph rendering runs natively in your web browser).*

---

## How to run: exact command and entry point

To launch the full interactive web application:

```bash
python3 main.py
```
*Alternatively, you can run Streamlit directly:*
```bash
streamlit run app.py
```

Once executed, your default browser will open automatically at:
```text
http://localhost:8501
```

---

## Example: sample automaton definition, input and output

### 1. Automaton Formal Definition
- **Language**: Binary strings ending with `'01'`
- **Formal 5-Tuple**: $M = (Q, \Sigma, \delta, Q_0, F)$
  - $Q = \{q0, q1, q2\}$
  - $\Sigma = \{0, 1\}$
  - $Q_0 = \{q0\}$
  - $F = \{q2\}$
  - Transition Function $\delta$:
    - $\delta(q0, 0) = \{q0, q1\}, \quad \delta(q0, 1) = \{q0\}$
    - $\delta(q1, 0) = \emptyset, \quad \delta(q1, 1) = \{q2\}$
    - $\delta(q2, 0) = \emptyset, \quad \delta(q2, 1) = \emptyset$

### 2. Test Input 1: Accepted String (`"1001"`)
- **Execution Step Trace**:
  - **Step 0 (Initial)**: Consumed: `""` | Active States: `{'q0'}` | Verdict: Processing
  - **Step 1 (Read '1')**: Consumed: `"1"` | Active States: `{'q0'}` | Verdict: Processing
  - **Step 2 (Read '0')**: Consumed: `"10"` | Active States: `{'q0', 'q1'}` (Non-deterministic branch!) | Verdict: Processing
  - **Step 3 (Read '0')**: Consumed: `"100"` | Active States: `{'q0', 'q1'}` | Verdict: Processing
  - **Step 4 (Read '1')**: Consumed: `"1001"` | Active States: `{'q0', 'q2'}` | Verdict: **ACCEPTED**
- **Outcome**: **ACCEPTED** (Since $\{q0, q2\} \cap F = \{q2\} \neq \emptyset$).

### 3. Test Input 2: Rejected String (`"1010"`)
- **Final Active States**: `{'q0', 'q1'}`
- **Outcome**: **REJECTED** (Since $\{q0, q1\} \cap \{q2\} = \emptyset$).

---

## Project structure: modules and responsibilities

```text
nfa_simulator/
├── app.py             # Main Streamlit web application: handles UI layout, tape stepper, tabs, and session state.
├── nfa.py             # Core mathematical NFA engine: ε-closure computation, step-by-step state tracing, serialization.
├── visualizer.py      # Interactive graph visualizer: builds standalone HTML/JS with Vis-network, node styling, and active glow.
├── presets.py         # Curated library of benchmark automata definitions with verified test cases.
├── main.py            # Primary CLI entry point that launches the Streamlit application server.
├── requirements.txt   # Manifest specifying required Python packages and versions.
├── gui.py             # Legacy PySimpleGUI interface (retained for backward reference).
└── README.md          # Comprehensive technical and project documentation.
```

---

## Testing: command, test data and expected behavior

### 1. Automated Test Suite Execution
Execute the automated validation suite directly from your terminal:
```bash
python3 -c "
from presets import PRESETS
from nfa import NFA

print('--- Running Automated NFA Test Suite ---')
for name, p in PRESETS.items():
    automaton = NFA.from_dict(p)
    for s in p.get('sample_accepted', []):
        assert automaton.process_string(s) is True, f'Failed accepted test for {name} on {s}'
    for s in p.get('sample_rejected', []):
        assert automaton.process_string(s) is False, f'Failed rejected test for {name} on {s}'
    print(f'✓ Preset: {name} passed all accepted & rejected test cases.')
print('All test cases passed successfully!')
"
```

### 2. Comprehensive Test Cases Table

| Test ID | Feature / Input Case | Automaton Tested | Input String | Expected Result | Observed Result | Status |
| :---: | :--- | :--- | :---: | :---: | :---: | :---: |
| **T01** | Standard Accepted String | Ends with '01' | `"1001"` | Accept (Ends in $\{q0, q2\}$) | Accept | **Pass** |
| **T02** | Standard Rejected String | Ends with '01' | `"1010"` | Reject (Ends in $\{q0, q1\}$) | Reject | **Pass** |
| **T03** | Empty String ($\epsilon$) | Starts in Accept State | `""` | Accept if $Q_0 \cap F \neq \emptyset$ | Accept | **Pass** |
| **T04** | Missing Transition (Trap) | Second from end '1' | `"000"` | Reject ($\emptyset$ / Dead-end) | Reject | **Pass** |
| **T05** | Multi-Branch Non-determinism | Contains 'ab' | `"babb"` | Accept (Concurrent paths) | Accept | **Pass** |
| **T06** | Multi-Stage $\epsilon$-Transitions | $0^* 1^* 2^*$ $\epsilon$-NFA | `"012"` | Accept ($\epsilon$-closure reachability) | Accept | **Pass** |

---

## Known limitations and troubleshooting

### Known Limitations
1. **Extreme String Length**: Strings exceeding $5,000$ characters may increase DOM render times for the interactive input tape.
2. **Regex Parsing**: Version 1.0 supports direct state-machine definition; automated Regular Expression to $\epsilon$-NFA conversion (Thompson's construction) is slated for Milestone-III.

### Troubleshooting
- **Port Already in Use (`8501`)**:
  If port 8501 is occupied, launch Streamlit on an alternate port:
  ```bash
  streamlit run app.py --server.port 8502
  ```
- **Module Not Found Errors**:
  Ensure you installed the project dependencies in your active Python environment:
  ```bash
  pip install -r requirements.txt
  ```
- **Static Import Warnings (`graphviz`)**:
  The new web interface uses in-browser HTML5 canvas rendering via Vis-network. Any static linter warnings regarding `graphviz` in legacy methods are resolved via dynamic module loading in `nfa.py`.

---

## Team contributions and acknowledgements

### Team Contributions (Group ID: [Insert Group ID])

| Member Name | Enrollment / Student ID | Assigned Modules | Specific Technical Contributions |
| :--- | :--- | :--- | :--- |
| **Surya Pratap Singh** | *[Insert ID]* | Core Engine & Simulation | Implemented `nfa.py`, $\epsilon$-closure algorithm, step-by-step multi-branch trace generator, and test suite. |
| **[Member Name 2]** | *[Insert ID]* | Web UI & Frontend | Developed `app.py`, Streamlit layout, input tape head, and live transition matrix tab. |
| **[Member Name 3]** | *[Insert ID]* | Visualization & Benchmarks | Engineered `visualizer.py` (Vis-network canvas), active state glow effects, and `presets.py`. |

### Acknowledgements
We express our sincere gratitude to:
- **Faculty & Instructors**, Department of Computer Science & Engineering, **Bennett University**, for their guidance in course **CSET302 – Automata Theory and Computability**.
- The open-source communities behind **Streamlit**, **Vis.js**, and **Pandas** for providing foundational visualization and UI tooling.
