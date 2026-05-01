import streamlit as st
import random

# 1. SET CONFIG
st.set_page_config(page_title="Wumpus World", layout="wide")

# 2. INITIALIZE SESSION STATE (FIXES YOUR ERROR)
if "world" not in st.session_state:
    st.session_state.world = {"pits": {(2, 3), (3, 1)}, "wumpus": (3, 3), "gold": (4, 4)}
    st.session_state.agent = {"r": 1, "c": 1, "visited": {(1, 1)}, "steps": 0, "kb": 14}
    st.session_state.game_over = False
    st.session_state.status = "EXPLORING"

# Short aliases
w = st.session_state.world
a = st.session_state.agent

# 3. CSS LIGHT MODE
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');
    html, body, [class*="st-"] { font-family: 'Inter', sans-serif; background-color: #f8fafc; color: #1e293b; }
    
    .panel { background: white; padding: 20px; border-radius: 12px; border: 1px solid #e2e8f0; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    
    /* Metrics Table Style */
    .metric-row { display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px dotted #e2e8f0; font-size: 15px; }
    .metric-label { color: #64748b; }
    .metric-value { color: #1e293b; font-weight: 600; }

    /* Grid */
    .wumpus-grid { display: grid; grid-template-columns: repeat(4, 75px); gap: 8px; justify-content: center; }
    .cell { width: 75px; height: 75px; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 24px; background: white; border: 1px solid #e2e8f0; }
    .cell-visited { background: #f1f5f9; }
    .cell-agent { background: #3b82f6 !important; color: white; box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4); }
    
    /* Buttons */
    .stButton>button { width: 100%; border-radius: 6px; height: 40px; font-weight: 600; }
</style>
""", unsafe_allow_html=True)

# 4. GAME FUNCTIONS
def get_percepts(r, c):
    p = []
    for pr, pc in w["pits"]:
        if abs(pr - r) + abs(pc - c) == 1: p.append("Breeze")
    if abs(w["wumpus"][0] - r) + abs(w["wumpus"][1] - c) == 1: p.append("Stench")
    if (r, c) == w["gold"]: p.append("Glitter")
    return p

def move_agent(dr, dc):
    if st.session_state.game_over: return
    nr, nc = a["r"] + dr, a["c"] + dc
    if 1 <= nr <= 4 and 1 <= nc <= 4:
        a["r"], a["c"] = nr, nc
        a["visited"].add((nr, nc))
        a["steps"] += 1
        a["kb"] += random.randint(1, 3)
        
        if (nr, nc) in w["pits"] or (nr, nc) == w["wumpus"]:
            st.session_state.status = "DEAD"
            st.session_state.game_over = True
        elif (nr, nc) == w["gold"]:
            st.session_state.status = "WIN"
            st.session_state.game_over = True

# 5. UI LAYOUT
st.title("🏹 Wumpus World AI")

col_left, col_mid, col_right = st.columns([1, 1.2, 1])

with col_left:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.subheader("Instructions")
    st.write("Find the Gold (💰) and avoid Pits (🕳️) or the Wumpus (👾).")
    st.write("💨 Breeze = Pit nearby")
    st.write("🤢 Stench = Wumpus nearby")
    if st.button("🔄 New Game"):
        for key in list(st.session_state.keys()): del st.session_state[key]
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

with col_mid:
    # Status Alert
    if st.session_state.status == "WIN": st.success("🏆 VICTORY!")
    elif st.session_state.status == "DEAD": st.error("💀 GAME OVER")
    else: st.info("🤖 Exploring...")

    # Grid
    grid_html = '<div class="wumpus-grid">'
    for r in range(4, 0, -1):
        for c in range(1, 5):
            is_agent = (r, c) == (a["r"], a["c"])
            is_visited = (r, c) in a["visited"]
            
            cls = "cell"
            content = ""
            if is_agent:
                cls += " cell-agent"; content = "🤖"
            elif is_visited:
                cls += " cell-visited"
                if (r,c) in w["pits"]: content = "🕳️"
                elif (r,c) == w["wumpus"]: content = "👾"
                elif (r,c) == w["gold"]: content = "💰"
                else:
                    percepts = get_percepts(r, c)
                    if "Breeze" in percepts: content = "💨"
                    if "Stench" in percepts: content = "🤢"
            grid_html += f'<div class="{cls}">{content}</div>'
    grid_html += '</div>'
    st.markdown(grid_html, unsafe_allow_html=True)

    # D-PAD
    st.write("")
    mc1, mc2, mc3 = st.columns(3)
    with mc2: st.button("▲", key="u", on_click=move_agent, args=(1,0))
    mc4, mc5, mc6 = st.columns(3)
    with mc4: st.button("◀", key="l", on_click=move_agent, args=(0,-1))
    with mc5: st.button("▼", key="d", on_click=move_agent, args=(-1,0))
    with mc6: st.button("▶", key="r_btn", on_click=move_agent, args=(0,1))

with col_right:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    curr_p = get_percepts(a["r"], a["c"])
    p_text = ", ".join(curr_p) if curr_p else "None"
    
    metrics = [
        ("Current Node", f"({a['r']}, {a['c']})"),
        ("Active Percepts", p_text),
        ("Resolution Steps", str(a["steps"])),
        ("KB Clauses", str(a["kb"]))
    ]
    
    for label, val in metrics:
        st.markdown(f'<div class="metric-row"><span class="metric-label">{label}</span><span class="metric-value">{val}</span></div>', unsafe_allow_html=True)
    
    st.markdown("<br>🏹 <b>Arrow:</b> Ready", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
