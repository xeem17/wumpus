import streamlit as st
import random

# 1. PAGE SETUP
st.set_page_config(page_title="Wumpus World AI", layout="wide")

# 2. SESSION STATE
if "agent_pos" not in st.session_state:
    st.session_state.agent_pos = [1, 1]
    st.session_state.visited = {(1, 1)}
    st.session_state.steps = 0
    st.session_state.kb = 14
    st.session_state.game_over = False
    st.session_state.status = "EXPLORING"
    # Fixed world for demo
    st.session_state.pits = {(3, 1), (2, 3)}
    st.session_state.wumpus = (3, 3)
    st.session_state.gold = (4, 4)

# 3. HIGH-CONTRAST LIGHT MODE CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    
    /* Global Styles */
    .stApp { background-color: #f8fafc; color: #1e293b; }
    h1, h2, h3, p, span { font-family: 'Inter', sans-serif !important; color: #1e293b !important; }

    /* Instructions & Stats Panels */
    .panel-card {
        background: white; 
        padding: 24px; 
        border-radius: 16px; 
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }

    /* Metrics Table (Screenshot Match) */
    .metric-row {
        display: flex; justify-content: space-between;
        padding: 14px 0; border-bottom: 1px dotted #cbd5e1;
        font-size: 16px;
    }
    .metric-label { color: #64748b; font-weight: 400; }
    .metric-value { color: #0f172a; font-weight: 700; }

    /* Grid Tile Styles */
    .grid-wrapper { display: grid; grid-template-columns: repeat(4, 80px); gap: 12px; justify-content: center; margin-top: 10px;}
    .tile {
        width: 80px; height: 80px; border-radius: 12px;
        display: flex; align-items: center; justify-content: center;
        font-size: 32px; border: 2px solid #f1f5f9; background: white;
    }
    .tile-visited { background: #f1f5f9; border-color: #e2e8f0; }
    .tile-agent { background: #2563eb !important; color: white !important; border-color: #1d4ed8; box-shadow: 0 10px 15px -3px rgba(37, 99, 235, 0.4); }
    .tile-pit { background: #fee2e2 !important; border-color: #ef4444; }
    .tile-wumpus { background: #f3e8ff !important; border-color: #a855f7; }
    .tile-gold { background: #fef9c3 !important; border-color: #eab308; }

    /* DARK BUTTONS */
    div.stButton > button {
        background-color: #0f172a !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 10px 20px !important;
        font-weight: 700 !important;
        width: 100%;
        height: 50px;
        display: flex;
        justify-content: center;
        align-items: center;
    }
    div.stButton > button:hover { background-color: #1e293b !important; color: #3b82f6 !important; }
    
    /* Reset Button Specific */
    .reset-btn button { background-color: #ef4444 !important; }
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

def move(dr, dc):
    if st.session_state.game_over: return
    nr, nc = st.session_state.agent_pos[0] + dr, st.session_state.agent_pos[1] + dc
    if 1 <= nr <= 4 and 1 <= nc <= 4:
        st.session_state.agent_pos = [nr, nc]
        st.session_state.visited.add((nr, nc))
        st.session_state.steps += 1
        st.session_state.kb += random.randint(3, 8)
        
        pos = (nr, nc)
        if pos in st.session_state.pits:
            st.session_state.status = "DEAD (FELL IN PIT)"
            st.session_state.game_over = True
        elif pos == st.session_state.wumpus:
            st.session_state.status = "DEAD (EATEN BY WUMPUS)"
            st.session_state.game_over = True
        elif pos == st.session_state.gold:
            st.session_state.status = "WINNER (FOUND GOLD)"
            st.session_state.game_over = True

# 5. UI LAYOUT
st.title("🏹 Wumpus World AI")

col_left, col_mid, col_right = st.columns([1, 1.2, 1])

with col_left:
    st.markdown('<div class="panel-card">', unsafe_allow_html=True)
    st.subheader("Instructions")
    st.markdown("🎯 **Goal:** Find Gold (💰)")
    st.markdown("💨 **Breeze:** Pit is adjacent")
    st.markdown("🤢 **Stench:** Wumpus is adjacent")
    st.markdown("✨ **Glitter:** Gold is here")
    st.write("---")
    if st.button("🔄 Reset Game"):
        for key in list(st.session_state.keys()): del st.session_state[key]
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

with col_mid:
    # Game Status Alert
    if st.session_state.game_over:
        if "WIN" in st.session_state.status: st.success(f"🏆 {st.session_state.status}")
        else: st.error(f"💀 {st.session_state.status}")
    else:
        st.info("🤖 AI is exploring...")

    # Grid
    grid_html = '<div class="grid-wrapper">'
    for r in range(4, 0, -1):
        for c in range(1, 5):
            curr = (r, c)
            is_agent = curr == tuple(st.session_state.agent_pos)
            is_visited = curr in st.session_state.visited
            
            style = "tile"
            content = ""
            
            if is_agent:
                style += " tile-agent"; content = "🤖"
            elif is_visited:
                style += " tile-visited"
                if curr in st.session_state.pits: style += " tile-pit"; content = "🕳️"
                elif curr == st.session_state.wumpus: style += " tile-wumpus"; content = "👾"
                elif curr == st.session_state.gold: style += " tile-gold"; content = "💰"
                else:
                    percepts = get_percepts(r, c)
                    if "Breeze" in percepts: content = "💨"
                    elif "Stench" in percepts: content = "🤢"
            
            grid_html += f'<div class="{style}">{content}</div>'
    grid_html += '</div>'
    st.markdown(grid_html, unsafe_allow_html=True)

    # D-PAD Controls (High Contrast)
    st.write("")
    c1, c2, c3 = st.columns(3)
    with c2: st.button("UP", on_click=move, args=(1, 0))
    c4, c5, c6 = st.columns(3)
    with c4: st.button("LEFT", on_click=move, args=(0, -1))
    with c5: st.button("DOWN", on_click=move, args=(-1, 0))
    with c6: st.button("RIGHT", on_click=move, args=(0, 1))

with col_right:
    st.markdown('<div class="panel-card">', unsafe_allow_html=True)
    cur_r, cur_c = st.session_state.agent_pos
    p_list = get_percepts(cur_r, cur_c)
    p_text = ", ".join(p_list) if p_list else "None"
    
    rows = [
        ("Current Node", f"({cur_r}, {cur_c})"),
        ("Active Percepts", p_text),
        ("Resolution Steps", st.session_state.steps),
        ("KB Clauses", st.session_state.kb)
    ]
    
    for label, val in rows:
        st.markdown(f"""
        <div class="metric-row">
            <span class="metric-label">{label}</span>
            <span class="metric-value">{val}</span>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>🏹 **Arrow:** Ready", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
