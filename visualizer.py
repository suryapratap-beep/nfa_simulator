"""Interactive Graph and SVG Visualizer for NFA Simulator."""

import json
from typing import Set, Dict, List, Optional, Any

def generate_vis_network_html(
    nfa,
    active_states: Optional[Set[str]] = None,
    active_transitions: Optional[List[Dict[str, str]]] = None,
    height_px: int = 480
) -> str:
    """
    Generate an interactive Vis-network graph HTML with SVG fallback.
    Supports zoom, drag, physics, highlighting active states and transitions.
    """
    active_states = active_states or set()
    active_trans_set = set()
    if active_transitions:
        for t in active_transitions:
            active_trans_set.add((t["from"], t["symbol"], t["to"]))

    # Prepare nodes
    nodes = []
    # Add virtual start node(s) for initial states
    start_edges = []
    for init_st in sorted(list(nfa.initial_states)):
        v_id = f"__start__{init_st}"
        nodes.append({
            "id": v_id,
            "label": "START",
            "shape": "box",
            "size": 10,
            "font": {"size": 11, "color": "#10b981", "bold": True},
            "color": {"background": "rgba(16, 185, 129, 0.15)", "border": "#10b981"},
            "borderWidth": 1.5,
            "margin": 4,
            "physics": True
        })
        start_edges.append({
            "from": v_id,
            "to": init_st,
            "arrows": "to",
            "color": {"color": "#10b981", "highlight": "#10b981"},
            "width": 2.5,
            "dashes": False
        })

    for state in sorted(list(nfa.states)):
        is_initial = state in nfa.initial_states
        is_final = state in nfa.final_states
        is_active = state in active_states

        # Color schemes
        if is_active:
            # Radiant highlight for active states
            bg_color = "#fef08a" if not is_final else "#a7f3d0"
            border_color = "#f59e0b" if not is_final else "#059669"
            font_color = "#0f172a"
            border_width = 5
            scale_size = 32
            shadow = {"enabled": True, "color": "#f59e0b" if not is_final else "#10b981", "size": 18, "x": 0, "y": 0}
        else:
            if is_final:
                bg_color = "#ecfdf5"
                border_color = "#059669"
                font_color = "#064e3b"
                border_width = 4
                scale_size = 28
                shadow = {"enabled": True, "color": "rgba(5, 150, 105, 0.2)", "size": 8, "x": 0, "y": 2}
            else:
                bg_color = "#f8fafc"
                border_color = "#3b82f6"
                font_color = "#1e293b"
                border_width = 2.5
                scale_size = 25
                shadow = {"enabled": True, "color": "rgba(59, 130, 246, 0.15)", "size": 6, "x": 0, "y": 2}

        subtext = ""
        if is_final and is_initial:
            subtext = "\n[Start | Accept]"
        elif is_final:
            subtext = "\n[Accept]"
        elif is_initial:
            subtext = "\n[Start]"

        nodes.append({
            "id": state,
            "label": f"{state}{subtext}",
            "title": f"State: {state} | {'Final/Accept' if is_final else 'Regular'}",
            "shape": "circle",
            "size": scale_size,
            "borderWidth": border_width,
            "color": {
                "background": bg_color,
                "border": border_color,
                "highlight": {"background": "#fed7aa", "border": "#ea580c"}
            },
            "font": {
                "size": 13,
                "color": font_color,
                "face": "system-ui, -apple-system, sans-serif",
                "bold": True
            },
            "shadow": shadow
        })

    # Prepare edges
    edge_map: Dict[tuple, List[str]] = {}
    for from_state, sym_map in nfa.transitions.items():
        for sym, to_states in sym_map.items():
            for to_state in to_states:
                key = (from_state, to_state)
                if key not in edge_map:
                    edge_map[key] = []
                edge_map[key].append(sym)

    edges = list(start_edges)
    for (u, v), symbols in edge_map.items():
        sym_label = ", ".join(sorted(symbols))
        is_edge_active = any((u, s, v) in active_trans_set for s in symbols)

        edge_color = "#f59e0b" if is_edge_active else "#64748b"
        edge_width = 3.5 if is_edge_active else 1.8
        
        edges.append({
            "from": u,
            "to": v,
            "label": f"  {sym_label}  ",
            "arrows": "to",
            "font": {
                "size": 13,
                "color": "#d97706" if is_edge_active else "#334155",
                "bold": True,
                "background": "#ffffff",
                "strokeWidth": 2,
                "strokeColor": "#f8fafc"
            },
            "color": {
                "color": edge_color,
                "highlight": "#f59e0b",
                "hover": "#0284c7"
            },
            "width": edge_width,
            "smooth": {"type": "curvedCW", "roundness": 0.25} if u != v else {"type": "discrete"},
            "selfReferenceSize": 26
        })

    nodes_json = json.dumps(nodes)
    edges_json = json.dumps(edges)

    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8" />
      <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
          font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
          background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
          color: #f1f5f9;
          overflow: hidden;
          width: 100%;
          height: {height_px}px;
          border-radius: 12px;
          border: 1px solid #334155;
          position: relative;
        }}
        #network {{
          width: 100%;
          height: 100%;
        }}
        .controls {{
          position: absolute;
          top: 12px;
          right: 12px;
          display: flex;
          gap: 6px;
          z-index: 10;
        }}
        .btn {{
          background: rgba(30, 41, 59, 0.85);
          color: #94a3b8;
          border: 1px solid #475569;
          padding: 6px 12px;
          border-radius: 6px;
          font-size: 12px;
          font-weight: 500;
          cursor: pointer;
          backdrop-filter: blur(4px);
          transition: all 0.2s ease;
        }}
        .btn:hover {{
          background: #3b82f6;
          color: #ffffff;
          border-color: #3b82f6;
          transform: translateY(-1px);
        }}
        .legend {{
          position: absolute;
          bottom: 12px;
          left: 12px;
          background: rgba(15, 23, 42, 0.85);
          border: 1px solid #334155;
          border-radius: 8px;
          padding: 8px 12px;
          font-size: 11px;
          display: flex;
          gap: 12px;
          align-items: center;
          backdrop-filter: blur(6px);
          z-index: 10;
        }}
        .legend-item {{
          display: flex;
          align-items: center;
          gap: 5px;
        }}
        .legend-dot {{
          width: 12px;
          height: 12px;
          border-radius: 50%;
          display: inline-block;
        }}
        .dot-normal {{ background: #f8fafc; border: 2px solid #3b82f6; }}
        .dot-accept {{ background: #ecfdf5; border: 3px double #059669; }}
        .dot-active {{ background: #fef08a; border: 3px solid #f59e0b; box-shadow: 0 0 6px #f59e0b; }}
        .dot-start {{ background: #10b981; border-radius: 2px; width: 8px; height: 8px; }}
        #fallback {{
          display: none;
          padding: 20px;
          text-align: center;
          color: #94a3b8;
        }}
      </style>
      <script src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
    </head>
    <body>
      <div class="controls">
        <button class="btn" onclick="network.fit({{ animation: {{ duration: 500 }} }})">⛶ Fit View</button>
        <button class="btn" onclick="togglePhysics()">⚡ Toggle Physics</button>
      </div>

      <div class="legend">
        <div class="legend-item"><span class="legend-dot dot-start"></span> Start</div>
        <div class="legend-item"><span class="legend-dot dot-normal"></span> State</div>
        <div class="legend-item"><span class="legend-dot dot-accept"></span> Accept</div>
        <div class="legend-item"><span class="legend-dot dot-active"></span> Active State</div>
      </div>

      <div id="network"></div>
      <div id="fallback">Visualization loading or offline mode active.</div>

      <script>
        let network = null;
        let physicsEnabled = true;

        try {{
          const container = document.getElementById('network');
          const data = {{
            nodes: new vis.DataSet({nodes_json}),
            edges: new vis.DataSet({edges_json})
          }};

          const options = {{
            nodes: {{
              borderWidthSelected: 4,
              chosen: true
            }},
            edges: {{
              arrows: {{
                to: {{ enabled: true, scaleFactor: 0.8 }}
              }},
              font: {{ align: 'top' }},
              selectionWidth: 3
            }},
            physics: {{
              solver: 'forceAtlas2Based',
              forceAtlas2Based: {{
                gravitationalConstant: -70,
                centralGravity: 0.015,
                springLength: 130,
                springConstant: 0.08,
                damping: 0.5
              }},
              stabilization: {{ iterations: 150 }}
            }},
            interaction: {{
              hover: true,
              tooltipDelay: 150,
              zoomView: true,
              dragView: true
            }}
          }};

          network = new vis.Network(container, data, options);
          
          network.once('stabilized', function() {{
            network.setOptions({{ physics: {{ enabled: false }} }});
            physicsEnabled = false;
          }});

        }} catch (e) {{
          console.error(e);
          document.getElementById('fallback').style.display = 'block';
          document.getElementById('network').style.display = 'none';
        }}

        function togglePhysics() {{
          if (!network) return;
          physicsEnabled = !physicsEnabled;
          network.setOptions({{ physics: {{ enabled: physicsEnabled }} }});
        }}
      </script>
    </body>
    </html>
    """
    return html_code
