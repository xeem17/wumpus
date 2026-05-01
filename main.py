import streamlit as st
import random

# 1. SETUP
st.set_page_config(page_title="Wumpus World AI", layout="wide")

# 2. ROBUST INITIALIZATION (FIXES THE ATTRIBUTE ERROR)
if "inference_steps" not in st.session_state:
    st.session_state.inference_steps = 0
if "agent_pos" not in st.session_state:
    st.session_state.agent_pos = [1, 1]
    st.session_state.visited = {(1, 1)}
    st.session_state.game_over = False
    st.session_state.status = "EXPLORING"
    st.session_state.pits = {(3, 1), (2, 3)}
    st.session_state.wumpus = (3, 3)
    st.session_state.gold = (4, 4)

# 3. HIGH-VISIBILITY CSS
st.markdown("""
<style>
    /* Force white background and black text everywhere */
    .stApp { background-color: white !important; }
    h1, h2, h3, p, span, div, label { color: black !important; font-family: 'Arial', sans-serif !important; }

    /* GRID */
    .grid-box { display: grid; grid-template-columns: repeat(4, 75px); gap: 10px; justify-content: center; margin: 20px 0; }
    .tile {
        width: 75px; height: 75px; border: 2px solid black !important;
        display: flex; align-items: center; justify-content: center; font-size: 28px;
    }
    .tile-unknown { background: #dddddd !important; } /* Gray */
    .tile-safe { background: #99ff99 !important; }    /* Green */
    .tile-danger { background: #ff9999 !important; }  /* Red */
    .tile-agent { background: #0055ff !important; }   /* Blue */

    /* DARK BUTTONS WITH WHITE TEXT */
    div.stButton > button {
        background-color: black !important;
        color: white !important;
        font-weight: bold !important;
        height: 50px !important;
        width: 100% !important;
        border: 2px solid black !important;
    }
    div.stButton > button p { color: white !important; }

    /* STATS TABLE */
    .stat-box { border: 2px solid black; padding: 15px; border-radius: 10px; background: white; }
    .stat-row { display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid black; }
</style>
""", unsafe_allow_html=True)

# 4. LOGIC
def get_percepts(r, c):
    p = []
    for pr, pc in st.session_state.pits:
        if abs(pr - r) + abs(pc - c) == 1: p.append("Breeze")
    if abs(st.session_state.wumpus[0] - r) + abs(st.session_state.wumpus[1] - c) == 1: p.append("Stench")
    if (r, c) == st.session_state.gold: p.append("Glitter")
    return p

def do_move(dr, dc):
    if st.session_state.game_over: return
    r, c = st.session_state.agent_pos
    nr, nc = r + dr, c + dc
    if 1 <= nr <= 4 and 1 <= nc <= 4:
        st.session_state.agent_pos = [nr, nc]
        st.session_state.visited.add((nr, nc))
        st.session_state.inference_steps += random.randint(10, 25)
        
        if (nr, nc) in st.session_state.pits or (nr, nc) == st.session_state.wumpus:
            st.session_state.status = "DEAD"
            st.session_state.game_over = True
        elif (nr, nc) == st.session_state.gold:
            st.session_state.status = "WINNER"
            st.session_state.game_over = True

# 5. UI
st.title("🏹 Wumpus World Dashboard")

col1, col2, col3 = st.columns([1, 1.2, 1])

with col1:
    st.write("### Instructions")
    st.write("💨 Breeze: Pit nearby")
    st.write("🤢 Stench: Wumpus nearby")
    st.write("✨ Glitter: Gold found")
    if st.button("RESET GAME"):
        for k in list(st.session_state.keys()): del st.session_state[k]
        st.rerun()

with col2:
    # STATUS
    if st.session_state.game_over:
        st.write(f"## {st.session_state.status}")
    else:
        st.write("## AI Navigating...")

    # GRID
    grid_html = '<div class="grid-box">'
    for r in range(4, 0, -1):
        for c in range(1, 5):
            curr = (r, c)
            is_agent = curr == tuple(st.session_state.agent_pos)
            is_visited = curr in st.session_state.visited
            
            style = "tile"
            icon = ""
            
            if is_agent:
                style += " tile-agent"; icon = "🤖"
            elif is_visited:
                if curr in st.session_state.pits or curr == st.session_state.wumpus:
                    style += " tile-danger"; icon = "💀"
                else:
                    style += " tile-safe"
                    p = get_percepts(r, c)
                    if "Breeze" in p: icon = "💨"
                    elif "Stench" in p: icon = "🤢"
                    elif curr == st.session_state.gold: icon = "💰"
            else:
                style += " tile-unknown"
            
            grid_html += f'<div class="{style}">{icon}</div>'
    grid_html += '</div>'
    st.markdown(grid_html, unsafe_allow_html=True)

    # MOVES
    _, m, _ = st.columns(3)
    with m: st.button("UP", on_click=do_move, args=(1,0))
    l, d, r = st.columns(3)
    with l: st.button("LEFT", on_click=do_move, args=(0,-1))
    with d: st.button("DOWN", on_click=do_move, args=(-1,0))
    with r: st.button("RIGHT", on_click=do_move, args=(0,1))

with col3:
    st.write("### Real-Time Metrics")
    pos = st.session_state.agent_pos
    percepts = get_percepts(pos[0], pos[1])
    
    st.markdown(f"""
    <div class="stat-box">
        <div class="stat-row"><span>Position</span><b>({pos[0]}, {pos[1]})</b></div>
        <div class="stat-row"><span>Percepts</span><b>{', '.join(percepts) if percepts else 'None'}</b></div>
        <div class="stat-row"><span>Inference Steps</span><b>{st.session_state.inference_steps}</b></div>
        <div class="stat-row"><span>Arrow</span><b>Ready</b></div>
    </div>
    """, unsafe_allow_html=True)
