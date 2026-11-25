import streamlit as st
import streamlit.components.v1 as components
import json
import pandas as pd
from nfa import NFA, EPSILON_SYMBOLS
from presets import PRESETS
from visualizer import generate_vis_network_html

# Page configuration
st.set_page_config(
    page_title="NFA Studio & Visualizer",
    page_icon="🔀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS styling for a modern, sleek interface
st.markdown("""
<style>
    /* Metric / card styles */
    .stMetric {
        background-color: #1e293b;
        padding: 12px;
        border-radius: 8px;
        border: 1px solid #334155;
    }
    .tape-container {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 6px;
        margin: 16px 0;
        overflow-x: auto;
        padding: 10px;
    }
    .tape-cell {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        min-width: 44px;
        height: 52px;
        font-family: monospace;
        font-size: 20px;
        font-weight: 700;
        border: 2px solid #475569;
        border-radius: 8px;
        background: #0f172a;
        color: #e2e8f0;
        position: relative;
    }
    .tape-cell.active {
        border-color: #f59e0b;
        background: #78350f;
        color: #fef08a;
        box-shadow: 0 0 12px rgba(245, 158, 11, 0.4);
        transform: translateY(-2px);
    }
    .tape-cell.consumed {
        border-color: #334155;
        background: #1e293b;
        color: #64748b;
    }
    .tape-pointer {
        position: absolute;
        top: -16px;
        font-size: 14px;
        color: #f59e0b;
    }
    .verdict-box {
        padding: 16px 20px;
        border-radius: 10px;
        font-weight: 600;
        font-size: 17px;
        margin-bottom: 15px;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .verdict-accept {
        background-color: rgba(16, 185, 129, 0.15);
        border: 1.5px solid #10b981;
        color: #34d399;
    }
    .verdict-reject {
        background-color: rgba(239, 68, 68, 0.15);
        border: 1.5px solid #ef4444;
        color: #f87171;
    }
    .badge {
        display: inline-block;
        padding: 3px 8px;
        border-radius: 9999px;
        font-size: 12px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# Helper function to initialize session state
def init_session_state():
    if "nfa_data" not in st.session_state:
        # Default to preset "Ends with '01'"
        default_preset = PRESETS["Ends with '01'"]
        st.session_state.nfa_data = {
            "states": list(default_preset["states"]),
            "alphabet": list(default_preset["alphabet"]),
            "initial_states": list(default_preset["initial_states"]),
            "final_states": list(default_preset["final_states"]),
            "transitions": {s: {sym: list(targets) for sym, targets in sm.items()}
                            for s, sm in default_preset["transitions"].items()}
        }
    if "input_str" not in st.session_state:
        st.session_state.input_str = "1001"
    if "step_index" not in st.session_state:
        st.session_state.step_index = 0

init_session_state()

# Build current NFA object
current_nfa = NFA.from_dict(st.session_state.nfa_data)

# ==================== SIDEBAR ====================
with st.sidebar:
    st.title("🔀 NFA Studio")
    st.caption("Interactive Automaton Design & Simulation")

    # --- Preset Gallery ---
    st.subheader("📚 Presets Gallery")
    preset_choice = st.selectbox("Choose a pre-built automaton:", list(PRESETS.keys()))
    preset_info = PRESETS[preset_choice]
    st.info(preset_info["description"])
    
    if st.button("🚀 Load This Preset", use_container_width=True):
        st.session_state.nfa_data = {
            "states": list(preset_info["states"]),
            "alphabet": list(preset_info["alphabet"]),
            "initial_states": list(preset_info["initial_states"]),
            "final_states": list(preset_info["final_states"]),
            "transitions": {s: {sym: list(targets) for sym, targets in sm.items()}
                            for s, sm in preset_info["transitions"].items()}
        }
        if preset_info["sample_accepted"]:
            st.session_state.input_str = preset_info["sample_accepted"][0]
        st.session_state.step_index = 0
        st.rerun()

    st.markdown("---")

    # --- Quick Setup ---
    st.subheader("⚙️ Automaton Setup")
    
    # States input
    states_str = st.text_input("States (comma-separated):", value=", ".join(st.session_state.nfa_data["states"]))
    parsed_states = [s.strip() for s in states_str.split(",") if s.strip()]

    # Alphabet input
    alphabet_str = st.text_input("Alphabet (comma-separated, use 'ε' for empty):", value=", ".join(st.session_state.nfa_data["alphabet"]))
    parsed_alphabet = [a.strip() for a in alphabet_str.split(",") if a.strip()]

    # Initial states selection
    valid_initials = [s for s in st.session_state.nfa_data["initial_states"] if s in parsed_states]
    new_initials = st.multiselect("Initial State(s) Q₀:", parsed_states, default=valid_initials)

    # Final states selection
    valid_finals = [s for s in st.session_state.nfa_data["final_states"] if s in parsed_states]
    new_finals = st.multiselect("Final / Accept State(s) F:", parsed_states, default=valid_finals)

    # Sync quick setup updates
    if (parsed_states != st.session_state.nfa_data["states"] or 
        parsed_alphabet != st.session_state.nfa_data["alphabet"] or 
        new_initials != st.session_state.nfa_data["initial_states"] or 
        new_finals != st.session_state.nfa_data["final_states"]):
        
        # Ensure transitions structure matches new states and alphabet
        new_transitions = {}
        for s in parsed_states:
            new_transitions[s] = {}
            for a in parsed_alphabet:
                old_targets = st.session_state.nfa_data["transitions"].get(s, {}).get(a, [])
                new_transitions[s][a] = [t for t in old_targets if t in parsed_states]
        
        st.session_state.nfa_data["states"] = parsed_states
        st.session_state.nfa_data["alphabet"] = parsed_alphabet
        st.session_state.nfa_data["initial_states"] = new_initials
        st.session_state.nfa_data["final_states"] = new_finals
        st.session_state.nfa_data["transitions"] = new_transitions
        st.rerun()

    st.markdown("---")

    # --- JSON Import / Export ---
    st.subheader("💾 Import / Export")
    col_exp, col_imp = st.columns(2)
    with col_exp:
        nfa_json = json.dumps(st.session_state.nfa_data, indent=2)
        st.download_button(
            "⬇️ Export JSON",
            data=nfa_json,
            file_name="nfa_automaton.json",
            mime="application/json",
            use_container_width=True
        )
    with col_imp:
        uploaded_file = st.file_uploader("Upload JSON", type=["json"], label_visibility="collapsed")
        if uploaded_file is not None:
            try:
                loaded_data = json.load(uploaded_file)
                if "states" in loaded_data and "alphabet" in loaded_data:
                    st.session_state.nfa_data = loaded_data
                    st.session_state.step_index = 0
                    st.success("Loaded!")
                    st.rerun()
            except Exception as e:
                st.error(f"Invalid JSON: {e}")

# ==================== MAIN TABS ====================
tab_sim, tab_table, tab_theory = st.tabs([
    "🎮 Simulation & Stepper", 
    "📝 Transition Matrix & Editor", 
    "📖 Formal Theory & Properties"
])

# Re-instantiate NFA
current_nfa = NFA.from_dict(st.session_state.nfa_data)

# ----------------------------------------------------
# TAB 1: SIMULATION & STEPPER
# ----------------------------------------------------
with tab_sim:
    col_input, col_preset_tests = st.columns([2, 1])
    with col_input:
        input_val = st.text_input(
            "🔤 Input String to Evaluate:",
            value=st.session_state.input_str,
            placeholder="e.g. 0101 or empty for ε",
            help="Type symbols belonging to the alphabet."
        )
        if input_val != st.session_state.input_str:
            st.session_state.input_str = input_val
            st.session_state.step_index = 0
            st.rerun()

    with col_preset_tests:
        st.write("**Quick Test Samples:**")
        sample_acc = preset_info.get("sample_accepted", [])
        sample_rej = preset_info.get("sample_rejected", [])
        btn_cols = st.columns(4)
        for i, s_val in enumerate(sample_acc[:2] + sample_rej[:2]):
            with btn_cols[i % 4]:
                label = f"'{s_val}'" if s_val else "'' (ε)"
                if st.button(label, key=f"quick_test_{i}", help="Test this sample"):
                    st.session_state.input_str = s_val
                    st.session_state.step_index = 0
                    st.rerun()

    # Compute execution trace
    trace = current_nfa.step_by_step_trace(st.session_state.input_str)
    total_steps = len(trace) - 1
    
    # Clamp step_index
    if st.session_state.step_index > total_steps:
        st.session_state.step_index = total_steps
    step_idx = st.session_state.step_index
    current_step_data = trace[step_idx]

    # Overall Verdict
    final_step = trace[-1]
    is_accepted = final_step["is_accepted"]
    
    verdict_class = "verdict-accept" if is_accepted else "verdict-reject"
    verdict_icon = "✅" if is_accepted else "❌"
    verdict_text = "ACCEPTED" if is_accepted else "REJECTED"
    verdict_sub = f"Evaluated string of length {len(st.session_state.input_str)} across {total_steps} transition steps."
    
    st.markdown(f"""
    <div class="verdict-box {verdict_class}">
        <div>
            <span style="font-size: 20px; margin-right: 8px;">{verdict_icon}</span>
            <strong>{verdict_text}</strong> — {verdict_sub}
        </div>
        <div>
            Active states at end: <code>{{{', '.join(final_step['active_states']) if final_step['active_states'] else '∅'}}}</code>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Visual Input Tape
    tape_html = ['<div class="tape-container">']
    if not st.session_state.input_str:
        tape_html.append('<div class="tape-cell active"><span class="tape-pointer">▼</span>ε</div>')
    else:
        for idx, char in enumerate(st.session_state.input_str):
            is_char_active = (idx == step_idx - 1) if step_idx > 0 else False
            is_char_consumed = idx < (step_idx - 1) if step_idx > 0 else False
            
            cls = "tape-cell"
            ptr = ""
            if is_char_active:
                cls += " active"
                ptr = '<span class="tape-pointer">▼</span>'
            elif is_char_consumed:
                cls += " consumed"
            
            tape_html.append(f'<div class="{cls}">{ptr}{char}</div>')
    tape_html.append('</div>')
    st.markdown("".join(tape_html), unsafe_allow_html=True)

    # Interactive Stepper Controls
    st.markdown("### ⏯️ Step-by-Step Stepper")
    ctl_cols = st.columns([1, 1, 1, 1, 4])
    with ctl_cols[0]:
        if st.button("⏮️ Start", use_container_width=True, disabled=(step_idx == 0)):
            st.session_state.step_index = 0
            st.rerun()
    with ctl_cols[1]:
        if st.button("◀️ Prev", use_container_width=True, disabled=(step_idx == 0)):
            st.session_state.step_index = max(0, step_idx - 1)
            st.rerun()
    with ctl_cols[2]:
        if st.button("Next ▶️", use_container_width=True, disabled=(step_idx >= total_steps)):
            st.session_state.step_index = min(total_steps, step_idx + 1)
            st.rerun()
    with ctl_cols[3]:
        if st.button("⏭️ End", use_container_width=True, disabled=(step_idx >= total_steps)):
            st.session_state.step_index = total_steps
            st.rerun()
    with ctl_cols[4]:
        new_step_val = st.slider(
            "Step scrubber",
            min_value=0,
            max_value=max(1, total_steps),
            value=step_idx,
            label_visibility="collapsed"
        )
        if new_step_val != step_idx:
            st.session_state.step_index = new_step_val
            st.rerun()

    # Step Detail Narrative
    st.info(
        f"**Step {current_step_data['step']} / {total_steps}:** {current_step_data['description']} | "
        f"**Currently Active States:** `{{{', '.join(current_step_data['active_states']) if current_step_data['active_states'] else '∅'}}}` " +
        ("🏁 *(Accept state reached!)*" if current_step_data["is_accepted"] else "")
    )

    # Graph & Trace Split
    graph_col, trace_col = st.columns([3, 2])
    with graph_col:
        st.markdown("**Interactive Automaton Graph:** *(Yellow = currently active states, drag to rearrange, scroll to zoom)*")
        active_set = set(current_step_data["active_states"])
        active_transitions = current_step_data["transitions_taken"]
        graph_html = generate_vis_network_html(current_nfa, active_states=active_set, active_transitions=active_transitions, height_px=450)
        components.html(graph_html, height=470)

    with trace_col:
        st.markdown("**Step-by-Step History Log:**")
        trace_rows = []
        for s in trace:
            sym_display = s["symbol"] if s["symbol"] is not None else "— (Start)"
            states_display = "{" + ", ".join(s["active_states"]) + "}" if s["active_states"] else "∅"
            status_display = "Accept" if s["is_accepted"] else ("Dead-end" if s["is_dead_end"] else "In progress")
            trace_rows.append({
                "Step": s["step"],
                "Symbol": sym_display,
                "Active States": states_display,
                "Status": status_display
            })
        df_trace = pd.DataFrame(trace_rows)
        st.dataframe(
            df_trace,
            use_container_width=True,
            height=430,
            hide_index=True
        )

# ----------------------------------------------------
# TAB 2: TRANSITION MATRIX & EDITOR
# ----------------------------------------------------
with tab_table:
    st.subheader("📝 Transition Matrix")
    st.caption("Each cell represents the set of next states δ(state, symbol).")

    # Render interactive/editable transition table
    table_matrix = []
    for st_name in current_nfa.states:
        row = {"State": st_name}
        for sym in sorted(list(current_nfa.alphabet)):
            targets = current_nfa.transitions.get(st_name, {}).get(sym, set())
            row[sym] = ", ".join(sorted(list(targets))) if targets else "∅"
        table_matrix.append(row)
    
    df_table = pd.DataFrame(table_matrix).set_index("State")
    st.table(df_table)

    st.markdown("---")
    st.subheader("✏️ Edit Transitions")
    edit_col1, edit_col2, edit_col3, edit_col4 = st.columns(4)
    with edit_col1:
        edit_from = st.selectbox("From State (q):", sorted(list(current_nfa.states)), key="edit_from")
    with edit_col2:
        edit_sym = st.selectbox("On Symbol (σ):", sorted(list(current_nfa.alphabet)), key="edit_sym")
    with edit_col3:
        current_val = list(current_nfa.transitions.get(edit_from, {}).get(edit_sym, set()))
        edit_targets = st.multiselect("To Next State(s) [supports non-determinism]:", sorted(list(current_nfa.states)), default=current_val, key="edit_targets")
    with edit_col4:
        st.write("")
        st.write("")
        if st.button("💾 Save Transition", use_container_width=True):
            if edit_from not in st.session_state.nfa_data["transitions"]:
                st.session_state.nfa_data["transitions"][edit_from] = {}
            st.session_state.nfa_data["transitions"][edit_from][edit_sym] = edit_targets
            st.success(f"Updated δ({edit_from}, {edit_sym}) → {{{', '.join(edit_targets)}}}")
            st.rerun()

# ----------------------------------------------------
# TAB 3: FORMAL THEORY & PROPERTIES
# ----------------------------------------------------
with tab_theory:
    st.subheader("🧮 Formal 5-Tuple Definition")
    st.latex(r"M = (Q, \Sigma, \delta, Q_0, F)")
    
    t_c1, t_c2 = st.columns(2)
    with t_c1:
        st.markdown(rf"""
        - **$Q$ (Set of States):** `{{{', '.join(sorted(current_nfa.states))}}}` (Count: {len(current_nfa.states)})
        - **$\Sigma$ (Alphabet):** `{{{', '.join(sorted(current_nfa.alphabet))}}}` (Count: {len(current_nfa.alphabet)})
        - **$Q_0$ (Initial States):** `{{{', '.join(sorted(current_nfa.initial_states)) or '∅'}}}`
        - **$F$ (Accept States):** `{{{', '.join(sorted(current_nfa.final_states)) or '∅'}}}`
        """)
    with t_c2:
        # Check non-determinism
        is_nondeterministic = False
        has_epsilon = False
        for s, sm in current_nfa.transitions.items():
            for sym, tgts in sm.items():
                if len(tgts) > 1 or len(tgts) == 0:
                    is_nondeterministic = True
                if current_nfa.is_epsilon(sym) and len(tgts) > 0:
                    has_epsilon = True

        st.markdown(f"""
        - **Automaton Classification:** **{'ε-NFA' if has_epsilon else ('NFA (Non-Deterministic)' if is_nondeterministic else 'DFA (Deterministic)')}**
        - **Non-deterministic Branches Detected:** {'Yes' if is_nondeterministic else 'No (Single target per transition)'}
        - **Epsilon Transitions Present:** {'Yes (Automatic ε-closure computation active)' if has_epsilon else 'None'}
        """)

    st.markdown("---")
    st.markdown(r"""
    ### 💡 How Non-Deterministic Evaluation Works
    Unlike a DFA where computation follows a single path, an NFA explores **all possible branches concurrently**.
    At each step:
    1. Read input symbol $a \in \Sigma$.
    2. Compute the union of next states: $\bigcup_{q \in S} \delta(q, a)$.
    3. Expand with $\epsilon$-closure: add all states reachable by taking 0 or more $\epsilon$-transitions.
    4. If the final active state set intersects with $F$ ($S \cap F \neq \emptyset$), the string is **Accepted**!
    """)
