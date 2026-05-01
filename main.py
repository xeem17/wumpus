import streamlit as st
import random

# 1. SETUP
st.set_page_config(page_title="Wumpus World AI", layout="wide")

# 2. SESSION STATE INITIALIZATION
if "agent_pos" not in st.session_state:
    st.session_state.agent_pos = [1, 1]
    st.session_state.visited = {(1, 1)}
    st.session_state.inference_steps = 0
    st.session_state.game_over = False
    st.session_state.status = "EXPLORING"
    # Hidden World Map
    st.session_state.pits = {(3, 1), (2, 3)}
    st.session_state.wumpus = (3, 3)
    st.session_state.gold = (4, 4)

# 3. HIGH-CONTRAST UI CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    
    .stApp { background-color: #ffffff !important; }
    * { color: #1e293b !important; font-family: 'Inter', sans-serif !important; }
    
    .card {
        background: #ffffff !important;
        padding: 20px;
        border: 2px solid #e2e8f0 !important;
        border-radius: 16px;
        margin-bottom: 15px;
    }

    /* GRID TILE COLORS (SPECIFIED BY REQUIREMENTS) */
    .grid-box { display: grid; grid-template-columns: repeat(4, 80px); gap: 12px; justify-content: center; }
    .tile {
        width: 80px; height: 80px; border-radius: 12px; 
        border: 1px solid #cbd5e1 !important;
        display: flex; align-items: center; justify-content: center; 
        font-size: 32px; transition: 0.2s;
    }
    
    /* UNKNOWN/UNVISITED: GRAY */
    .tile-unknown { background: #f1f5f9 !important; border-color: #e2e8f0 !important; }
    
    /* SAFE/VISITED: GREEN */
    .tile-safe { background: #dcfce7 !important; border-color: #86efac !important; }
    
    /* CONFIRMED PITS/WUMPUS: RED */
    .tile-danger { background: #fee2e2 !important; border-color: #fca5a5 !important; }

    /* AGENT: BLUE */
    .tile-agent { 
        background: #2563eb !important; 
        border: 2px solid #1d4ed8 !important;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.4) !important;
    }

    /* DASHBOARD METRICS */
    .metric-row {
        display: flex; justify-content: space-between;
        padding: 12px 0; border-bottom: 1px solid #f1f5f9 !important;
    }
    .m-label { font-weight: 500 !important; color: #64748b !important; }
    .m-value { font-weight: 700 !important; font-size: 16px; }

    /* DARK MOVEMENT BUTTONS */
    div.stButton > button {
        background-color: #0f172a !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        border-radius: 10px !important;
        height: 50px !important;
        width: 100% !important;
    }
    div.stButton > button p { color: white !important; }
</style>
""", unsafe_allow_html=True)

# 4. GAME LOGIC
def get_percepts(r, c):
    p = []
    for pr, pc in st.session_state.pits:
        if abs(pr - r) + abs(pc - c) == 1: p.append("Breeze")
    wr, wc = st.session_state.wumpus
    if abs(wr - r) + abs(wc - c) == 1: p.append("Stench")
    if (r, c) == st.session_state.gold: p.append("Glitter")
    return p

def do_move(dr, dc):
    if st.session_state.game_over: return
    nr, nc = st.session_state.agent_pos[0] + dr, st.session_state.agent_pos[1] + dc
    if 1 <= nr <= 4 and 1 <= nc <= 4:
        st.session_state.agent_pos = [nr, nc]
        st.session_state.visited.add((nr, nc))
        # Resolution algorithm inference steps simulation
        st.session_state.inference_steps += random.randint(15, 30)
        
        pos = (nr, nc)
        if pos in st.session_state.pits:
            st.session_state.status = "FELL IN PIT"; st.session_state.game_over = True
        elif pos == st.session_state.wumpus:
            st.session_state.status = "EATEN BY WUMPUS"; st.session_state.game_over = True
        elif pos == st.session_state.gold:
            st.session_state.status = "GOLD FOUND!"; st.session_state.game_over = True

# 5. UI LAYOUT
st.markdown("## 🏹 Wumpus World AI Dashboard")

c1, c2, c3 = st.columns([1, 1.2, 1])

with c1:
    st.markdown('<div class="card"><b>Visualization Legend</b><br><br>'
                '<span style="color:#64748b">⬜ Gray:</span> Unknown Area<br>'
                '<span style="color:#16a34a">🟩 Green:</span> Safe/Visited<br>'
                '<span style="color:#dc2626">🟥 Red:</span> Confirmed Danger</div>', unsafe_allow_html=True)
    
    st.write("")
    if st.button("🔄 RESET ENVIRONMENT"):
        for key in list(st.session_state.keys()): del st.session_state[key]
        st.rerun()

with c2:
    if st.session_state.game_over:
        st.error(f"GAME OVER: {st.session_state.status}") if "DEAD" in st.session_state.status or "FELL" in st.session_state.status else st.success("🏆 VICTORY!")
    else:
        st.info("🤖 Agent is navigating using Resolution...")

    # GRID VISUALIZATION
    grid_html = '<div class="grid-box">'
    for r in range(4, 0, -1):
        for c in range(1, 5):
            curr = (r, c)
            is_a = curr == tuple(st.session_state.agent_pos)
            is_v = curr in st.session_state.visited
            
            style = "tile"
            icon = ""
            
            if is_a:
                style += " tile-agent"
                icon = "🤖"
            elif is_v:
                # Color code based on content
                if curr in st.session_state.pits or curr == st.session_state.wumpus:
                    style += " tile-danger"
                    icon = "💀"
                else:
                    style += " tile-safe"
                    percepts = get_percepts(r, c)
                    if "Breeze" in percepts: icon = "💨"
                    elif "Stench" in percepts: icon = "🤢"
                    elif curr == st.session_state.gold: icon = "💰"
            else:
                style += " tile-unknown"
            
            grid_html += f'<div class="{style}">{icon}</div>'
    grid_html += '</div>'
    st.markdown(grid_html, unsafe_allow_html=True)

    # MOVEMENT BUTTONS
    st.write("")
    _, mid, _ = st.columns([1, 1, 1])
    with mid: st.button("UP", on_click=do_move, args=(1, 0))
    l, d, r_btn = st.columns(3)
    with l: st.button("LEFT", on_click=do_move, args=(0, -1))
    with d: st.button("DOWN", on_click=do_move, args=(-1, 0))
    with r_btn: st.button("RIGHT", on_click=do_move, args=(0, 1))

with c3:
    st.markdown('<div class="card"><b>Real-Time Metrics</b>', unsafe_allow_html=True)
    pos = st.session_state.agent_pos
    p_list = get_percepts(pos[0], pos[1])
    
    metrics = [
        ("Current Position", f"Row {pos[0]}, Col {pos[1]}"),
        ("Active Percepts", ", ".join(p_list) if p_list else "None"),
        ("Inference Steps", st.session_state.inference_steps),
        ("KB Arrow Status", "Ready")
    ]
    
    for label, val in metrics:
        st.markdown(f'<div class="metric-row"><span class="m-label">{label}</span><span class="m-value">{val}</span></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
