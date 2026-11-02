# 🔀 NFA Simulator & Visualizer

A clean, interactive desktop application built in Python to construct, simulate, and visualize **Non-Deterministic Finite Automata (NFA)**. 

Define custom states and alphabets, configure transitions in an intuitive table editor, test input strings with instant acceptance feedback, and generate visual state-machine diagrams using Graphviz.

---

## ✨ Features

- **Interactive GUI**: User-friendly desktop interface powered by PySimpleGUI.
- **Dynamic Automaton Setup**: Specify any number of states ($q_0, q_1, \dots, q_n$) and custom alphabet symbols.
- **Visual Transition Table**: Clickable table cells to easily define transitions to multiple states (supporting non-determinism).
- **Multiple Start & Accept States**: Flexible checkbox toggles for both initial ($Q_0$) and final ($F$) states.
- **Instant Simulation**: Test input strings to see if they are **ACCEPTED** or **REJECTED** by the automaton.
- **Automaton Visualization**: Export and view publication-quality state diagrams rendered in PNG format with Graphviz.

---

## 📁 Project Structure

```text
nfa-simulator/
├── main.py          # Entry point that launches the application
├── gui.py           # PySimpleGUI interface and user interaction logic
├── nfa.py           # Core NFA logic: transition handling, string evaluation & Graphviz graph builder
├── .gitignore       # Git ignore rules for Python bytecode, cache, and exports
└── README.md        # Project documentation
```

---

## 🛠️ Prerequisites & Installation

### 1. Python 3.8+
Make sure you have Python 3 installed:
```bash
python3 --version
```

### 2. Python Dependencies
Install the required Python libraries using `pip`:
```bash
pip3 install PySimpleGUI graphviz
```

### 3. Graphviz System Tool *(Required for diagram generation)*
Graphviz requires a system-level executable (`dot`) to render visual graphs:
- **macOS** (Homebrew):
  ```bash
  brew install graphviz
  ```
- **Ubuntu / Debian**:
  ```bash
  sudo apt update && sudo apt install graphviz
  ```
- **Windows**:
  Download and install from the [official Graphviz website](https://graphviz.org/download/), and ensure it is added to your system `PATH`.

---

## 🚀 How to Run

1. Clone or download this repository:
   ```bash
   git clone <your-repository-url>
   cd nfa-simulator
   ```

2. Run the application:
   ```bash
   python3 main.py
   ```

---

## 📖 Step-by-Step Usage Guide

### 1. Setup States and Alphabet
When you launch the app, enter:
- **Number of states:** e.g., `3` (automatically creates states `q0`, `q1`, `q2`).
- **Alphabet:** Comma-separated symbols, e.g., `0, 1` or `a, b`.
- Click **Set States and Alphabet**.

### 2. Populate the Transition Table
- In the main window, click on any row in the **Transition Table**.
- Select the column/symbol you want to edit.
- In the popup, enter destination state(s) separated by commas (e.g. `q0, q1` or leave blank for $\emptyset$).
- The table will update with your configured transitions.

### 3. Designate Initial and Final States
- Use the checkboxes below the table to mark one or more states as:
  - **(Initial)**: Starting state(s) for string processing.
  - **(Final)**: Accept state(s). Double circles will be used in the visual graph.

### 4. Test Strings & Generate Diagrams
- **Simulate String**: Enter an input string (e.g. `0101`) in the input box and click **Simulate** to check whether it leads to an accepting state.
- **Generate NFA**: Click **Generate NFA** to generate `nfa_graph.png` and view the diagram automatically in your default image viewer.

---

## 🧮 Theoretical Background

A Non-Deterministic Finite Automaton (NFA) is formally represented as a 5-tuple:

$$M = (Q, \Sigma, \delta, Q_0, F)$$

Where:
- $Q$ is the finite set of states (e.g., $\{q_0, q_1, q_2\}$).
- $\Sigma$ is the finite alphabet of input symbols (e.g., $\{0, 1\}$).
- $\delta: Q \times \Sigma \to \mathcal{P}(Q)$ is the transition function mapping a state and symbol to a set of next states.
- $Q_0 \subseteq Q$ is the set of initial states.
- $F \subseteq Q$ is the set of final / accepting states.

A string $w$ is **accepted** if there exists at least one computation path from an initial state in $Q_0$ that ends in an accept state $q \in F$.

---

## 🔍 Troubleshooting

- **`ModuleNotFoundError: No module named 'PySimpleGUI'` or `'graphviz'`**:
  Make sure you ran `pip3 install PySimpleGUI graphviz` in your active Python environment.
- **`graphviz.backend.execute.ExecutableNotFound: failed to execute 'dot'`**:
  Graphviz's system package is missing. On macOS, run `brew install graphviz`.
- **Parse or Syntax Error on startup**:
  Ensure shell commands like `!pip install ...` are run in your terminal, not kept inside `.py` source files.

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

