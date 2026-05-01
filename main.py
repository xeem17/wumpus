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

# 3. HIGH-VISIBILITY CSS
st.markdown("""
<style>
    /* Force all text to be visible and dark */
    .main, p, span, label, div {
        color: #1e293b !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }

    /* GRID TILES */
    .grid-box { display: grid; grid-template-columns: repeat(4, 70px); gap: 10px; justify-content: center; margin: 20px 0; }
    .tile {
        width: 70px; height: 70px; border-radius: 10px; border: 2px solid #e2e8f0;
        display: flex; align-items: center; justify-content: center; font-size: 24px; background: white;
    }
    .tile-agent { background: #2563eb !important; color: white !important; box-shadow: 0 4px 10px rgba(37, 99, 235, 0.5); }
    .tile-visited { background: #f1f5f9; }

    /* BUTTONS: DARK BACKGROUND, BRIGHT WHITE TEXT */
    div.stButton > button {
        background-color: #0f172a !important;
        color: #ffffff !important;
        font-weight: 800 !important;
        font-size: 16px !important;
        border: none !important;
        height: 50px !important;
        width: 100% !important;
        opacity: 1 !important;
    }
    
    /* SIDEBAR DATA STYLE */
    .metric-row {
        display: flex; justify-content: space-between;
        padding: 10px 0; border-bottom: 1px solid #e2e8f0;
    }
    .m-label { font-weight: 500; color: #64748b !important; }
    .m-value { font-weight: 700; color: #0f172a !important; }

    /* ICON BOXES */
    .icon-box { background: white; padding: 15px; border-radius: 10px; border: 1px solid #e2e8f0; margin-bottom: 10px; }
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
    st.subheader("Instructions")
    st.markdown('<div class="icon-box">💨 <b>Breeze:</b> Pit nearby</div>', unsafe_allow_html=True)
    st.markdown('<div class="icon-box">🤢 <b>Stench:</b> Wumpus nearby</div>', unsafe_allow_html=True)
    st.markdown('<div class="icon-box">✨ <b>Glitter:</b> Gold is here</div>', unsafe_allow_html=True)
    if st.button("🔄 RESET GAME"):
        for key in list(st.session_state.keys()): del st.session_state[key]
        st.rerun()

with c2:
    if st.session_state.game_over:
        st.error(st.session_state.status) if "DEAD" in st.session_state.status else st.success("🏆 WINNER")
    else:
        st.info("🤖 AI Currently Exploring...")

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
                if curr in st.session_state.pits: icon = "🕳️"
                elif curr == st.session_state.wumpus: icon = "👾"
                elif curr == st.session_state.gold: icon = "💰"
                else:
                    percepts = get_percepts(r, c)
                    if "Breeze" in percepts: icon = "💨"
                    if "Stench" in percepts: icon = "🤢"
            grid_html += f'<div class="{style}">{icon}</div>'
    grid_html += '</div>'
    st.markdown(grid_html, unsafe_allow_html=True)

    # D-PAD
    _, mid, _ = st.columns([1, 1, 1])
    with mid: st.button("UP", on_click=do_move, args=(1, 0))
    l, d, r_btn = st.columns(3)
    with l: st.button("LEFT", on_click=do_move, args=(0, -1))
    with d: st.button("DOWN", on_click=do_move, args=(-1, 0))
    with r_btn: st.button("RIGHT", on_click=do_move, args=(0, 1))

with c3:
    st.subheader("Agent Data")
    pos = st.session_state.agent_pos
    p_list = get_percepts(pos[0], pos[1])
    
    metrics = [
        ("Current Node", f"({pos[0]}, {pos[1]})"),
        ("Active Percepts", ", ".join(p_list) if p_list else "None"),
        ("Resolution Steps", st.session_state.steps),
        ("KB Clauses", st.session_state.kb)
    ]
    
    for label, val in metrics:
        st.markdown(f'<div class="metric-row"><span class="m-label">{label}</span><span class="m-value">{val}</span></div>', unsafe_allow_html=True)
    
    st.write("")
    st.write("🏹 **Arrow:** Ready")
