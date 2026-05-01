import streamlit as st
import random

# 1. SETUP
st.set_page_config(page_title="Wumpus World AI", layout="wide")

# 2. STATE
if "agent_pos" not in st.session_state:
    st.session_state.agent_pos = [1, 1]
    st.session_state.visited = {(1, 1)}
    st.session_state.steps = 0
    st.session_state.kb = 14
    st.session_state.game_over = False
    st.session_state.status = "EXPLORING"
    st.session_state.pits = {(3, 1), (2, 3)}
    st.session_state.wumpus = (3, 3)
    st.session_state.gold = (4, 4)

# 3. CSS (FIXED CONTRAST & SIMPLIFIED BAR)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap');
    
    .stApp { background-color: #f8fafc; }
    
    /* PANEL CARDS */
    .card {
        background: white;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
    }

    /* GRID TILES */
    .grid-box { display: grid; grid-template-columns: repeat(4, 75px); gap: 10px; justify-content: center; }
    .tile {
        width: 75px; height: 75px; border-radius: 10px; border: 1px solid #eef2f6;
        display: flex; align-items: center; justify-content: center; font-size: 24px; background: white;
    }
    .tile-visited { background: #f1f5f9; }
    .tile-agent { background: #2563eb !important; color: white !important; box-shadow: 0 4px 10px rgba(37, 99, 235, 0.3); }
    .tile-pit { background: #fee2e2 !important; }
    .tile-wumpus { background: #f3e8ff !important; }
    .tile-gold { background: #fef9c3 !important; }

    /* DARK BUTTONS WITH WHITE TEXT (FIXED) */
    div.stButton > button {
        background-color: #0f172a !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        border: none !important;
        width: 100%;
        height: 45px;
        border-radius: 8px;
    }
    div.stButton > button:hover {
        background-color: #1e293b !important;
        color: #3b82f6 !important;
    }

    /* SIMPLIFIED METRIC ROW */
    .metric-row {
        display: flex;
        justify-content: space-between;
        padding: 12px 0;
        border-bottom: 1px solid #f1f5f9;
        font-family: 'Inter', sans-serif;
    }
    .m-label { color: #64748b; font-size: 14px; }
    .m-value { color: #0f172a; font-weight: 700; font-size: 15px; }

</style>
""", unsafe_allow_html=True)

# 4. LOGIC
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
        st.session_state.steps += 1
        st.session_state.kb += random.randint(2, 5)
        pos = (nr, nc)
        if pos in st.session_state.pits:
            st.session_state.status = "DEAD (PIT)"; st.session_state.game_over = True
        elif pos == st.session_state.wumpus:
            st.session_state.status = "DEAD (WUMPUS)"; st.session_state.game_over = True
        elif pos == st.session_state.gold:
            st.session_state.status = "WINNER!"; st.session_state.game_over = True

# 5. UI
st.title("🏹 Wumpus World AI")

c1, c2, c3 = st.columns([1, 1.2, 1])

with c1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Instructions")
    st.write("💨 Breeze: Pit nearby")
    st.write("🤢 Stench: Wumpus nearby")
    st.write("✨ Glitter: Gold is here")
    st.write("---")
    if st.button("🔄 Reset Game"):
        for key in list(st.session_state.keys()): del st.session_state[key]
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

with c2:
    # Game Status
    if st.session_state.game_over:
        if "WIN" in st.session_state.status: st.success(st.session_state.status)
        else: st.error(st.session_state.status)
    else: st.info("🤖 AI Exploring...")

    # Grid
    grid_html = '<div class="grid-box">'
    for r in range(4, 0, -1):
        for c in range(1, 5):
            curr = (r, c)
            is_a = curr == tuple(st.session_state.agent_pos)
            is_v = curr in st.session_state.visited
            style = "tile"
            icon = ""
            if is_a: style += " tile-agent"; icon = "🤖"
            elif is_v:
                style += " tile-visited"
                if curr in st.session_state.pits: style += " tile-pit"; icon = "🕳️"
                elif curr == st.session_state.wumpus: style += " tile-wumpus"; icon = "👾"
                elif curr == st.session_state.gold: style += " tile-gold"; icon = "💰"
                else:
                    percepts = get_percepts(r, c)
                    if "Breeze" in percepts: icon = "💨"
                    elif "Stench" in percepts: icon = "🤢"
            grid_html += f'<div class="{style}">{icon}</div>'
    grid_html += '</div>'
    st.markdown(grid_html, unsafe_allow_html=True)

    # Controls
    st.write("")
    _, mid, _ = st.columns([1,1,1])
    with mid: st.button("UP", on_click=do_move, args=(1, 0))
    l, d, r_btn = st.columns(3)
    with l: st.button("LEFT", on_click=do_move, args=(0, -1))
    with d: st.button("DOWN", on_click=do_move, args=(-1, 0))
    with r_btn: st.button("RIGHT", on_click=do_move, args=(0, 1))

with c3:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    pos = st.session_state.agent_pos
    p_list = get_percepts(pos[0], pos[1])
    
    rows = [
        ("Current Node", f"({pos[0]}, {pos[1]})"),
        ("Active Percepts", ", ".join(p_list) if p_list else "None"),
        ("Resolution Steps", st.session_state.steps),
        ("KB Clauses", st.session_state.kb)
    ]
    
    for label, val in rows:
        st.markdown(f'<div class="metric-row"><span class="m-label">{label}</span><span class="m-value">{val}</span></div>', unsafe_allow_html=True)
    
    st.markdown("<br>🏹 <b>Arrow:</b> Ready", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
