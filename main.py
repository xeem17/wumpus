import streamlit as st
import random

# --- CONFIG ---
st.set_page_config(page_title="Wumpus World Pro", layout="wide")

ROWS, COLS = 4, 4

# --- CSS LIGHT MODE ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    html, body, [class*="st-"] {
        font-family: 'Inter', sans-serif;
        background-color: #f8fafc;
        color: #1e293b;
    }

    .main-title {
        font-size: 32px;
        font-weight: 800;
        color: #0f172a;
        margin-bottom: 20px;
        text-align: center;
    }

    /* Column Containers */
    .side-panel {
        background: white;
        padding: 24px;
        border-radius: 16px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }

    /* The Metrics Table (Matching the Screenshot) */
    .metric-row {
        display: flex;
        justify-content: space-between;
        padding: 12px 0;
        border-bottom: 1px dotted #e2e8f0;
        font-size: 16px;
    }
    .metric-label { color: #64748b; font-weight: 400; }
    .metric-value { color: #1e293b; font-weight: 600; }

    /* Grid System */
    .wumpus-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 10px;
        max-width: 500px;
        margin: auto;
    }

    .cell {
        aspect-ratio: 1/1;
        border-radius: 12px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        font-size: 28px;
        background: white;
        border: 2px solid #f1f5f9;
        transition: all 0.2s;
    }

    .cell-visited { background: #f1f5f9; border-color: #e2e8f0; }
    .cell-agent { background: #3b82f6 !important; border-color: #2563eb; color: white; transform: scale(1.02); box-shadow: 0 10px 15px -3px rgba(59, 130, 246, 0.3); }
    .cell-pit { background: #fee2e2 !important; border-color: #fecaca; }
    .cell-wumpus { background: #f3e8ff !important; border-color: #e9d5ff; }
    .cell-gold { background: #fef9c3 !important; border-color: #fef08a; }
    
    .percept-icon { font-size: 14px; margin-top: 4px; }

    /* Button Styling */
    .stButton>button {
        background: #1e293b !important;
        color: white !important;
        border-radius: 8px;
        border: none;
        width: 100%;
        transition: transform 0.1s;
    }
    .stButton>button:hover { transform: translateY(-2px); background: #334155 !important; }
</style>
""", unsafe_allow_html=True)

# --- GAME LOGIC ---
class World:
    def __init__(self):
        self.pits = {(2, 3), (3, 1)}
        self.wumpus = (3, 3)
        self.gold = (4, 4)

class Agent:
    def __init__(self):
        self.r, self.c = 1, 1
        self.visited = {(1, 1)}
        self.steps = 0
        self.kb_clauses = 14

def init_game():
    st.session_state.world = World()
    st.session_state.agent = Agent()
    st.session_state.game_over = False
    st.session_state.status = "EXPLORING"

if "world" not in st.session_state:
    init_game()

w = st.session_state.world
a = st.session_state.agent

def get_percepts(r, c):
    p = []
    for pr, pc in w.pits:
        if abs(pr - r) + abs(pc - c) == 1: p.append("Breeze")
    if abs(w.wumpus[0] - r) + abs(w.wumpus[1] - c) == 1: p.append("Stench")
    if (r, c) == w.gold: p.append("Glitter")
    return p

def move_agent(dr, dc):
    if st.session_state.game_over: return
    new_r, new_c = a.r + dr, a.c + dc
    if 1 <= new_r <= ROWS and 1 <= new_c <= COLS:
        a.r, a.c = new_r, new_c
        a.visited.add((a.r, a.c))
        a.steps += 1
        a.kb_clauses += random.randint(2, 5) # Simulating logic growth
        
        if (a.r, a.c) in w.pits or (a.r, a.c) == w.wumpus:
            st.session_state.game_over = True
            st.session_state.status = "GAME OVER"
        elif (a.r, a.c) == w.gold:
            st.session_state.game_over = True
            st.session_state.status = "VICTORY"

# --- UI LAYOUT ---
st.markdown('<div class="main-title">WUMPUS WORLD AI</div>', unsafe_allow_html=True)

col_inst, col_grid, col_stats = st.columns([1, 1.5, 1])

# --- LEFT: INSTRUCTIONS ---
with col_inst:
    st.markdown('<div class="side-panel">', unsafe_allow_html=True)
    st.subheader("How to Play")
    st.markdown("""
    - **Goal:** Find the Gold (💰) and return safely.
    - **Pits (🕳️):** Avoid them! You'll feel a **Breeze** (💨) nearby.
    - **Wumpus (👾):** Avoid it! You'll smell a **Stench** (🤢) nearby.
    - **Movement:** Use the D-Pad buttons under the grid to navigate.
    - **Knowledge:** Every step updates the agent's Knowledge Base.
    """)
    if st.button("🔄 Reset Game"):
        init_game()
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# --- CENTER: GRID ---
with col_grid:
    # Game Status Banner
    if st.session_state.status == "VICTORY":
        st.success("🏆 Goal Reached! Victory!")
    elif st.session_state.status == "GAME OVER":
        st.error("💀 The Agent has perished.")
    else:
        st.info("🤖 Agent is exploring the cave...")

    grid_html = '<div class="wumpus-grid">'
    for r in range(ROWS, 0, -1):
        for c in range(1, COLS + 1):
            is_agent = (r, c) == (a.r, a.c)
            is_visited = (r, c) in a.visited
            
            cls = "cell"
            content = ""
            
            if is_agent:
                cls += " cell-agent"
                content = "🤖"
            elif not is_visited:
                content = "" # Fog of war
            else:
                cls += " cell-visited"
                if (r,c) in w.pits: cls += " cell-pit"; content = "🕳️"
                elif (r,c) == w.wumpus: cls += " cell-wumpus"; content = "👾"
                elif (r,c) == w.gold: cls += " cell-gold"; content = "💰"
                else:
                    percepts = get_percepts(r, c)
                    icons = []
                    if "Breeze" in percepts: icons.append("💨")
                    if "Stench" in percepts: icons.append("🤢")
                    content = f'<div class="percept-icon">{" ".join(icons)}</div>'
            
            grid_html += f'<div class="{cls}">{content}</div>'
    grid_html += '</div>'
    st.markdown(grid_html, unsafe_allow_html=True)

    # D-PAD CONTROLS
    st.write("")
    c1, c2, c3 = st.columns(3)
    with c2: st.button("▲", key="up", on_click=move_agent, args=(1, 0))
    c4, c5, c6 = st.columns(3)
    with c4: st.button("◀", key="left", on_click=move_agent, args=(0, -1))
    with c5: st.button("▼", key="down", on_click=move_agent, args=(-1, 0))
    with c6: st.button("▶", key="right", on_click=move_agent, args=(0, 1))

# --- RIGHT: METRICS (SCREENSHOT STYLE) ---
with col_stats:
    st.markdown('<div class="side-panel">', unsafe_allow_html=True)
    
    current_percepts = get_percepts(a.r, a.c)
    percept_text = ", ".join(current_percepts) if current_percepts else "None"
    
    # Table layout matching your image
    metrics = [
        ("Current Node", f"({a.r}, {a.c})"),
        ("Active Percepts", percept_text),
        ("Resolution Steps", str(a.steps)),
        ("KB Clauses", str(a.kb_clauses))
    ]
    
    for label, value in metrics:
        st.markdown(f"""
        <div class="metric-row">
            <span class="metric-label">{label}</span>
            <span class="metric-value">{value}</span>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("🏹 **Arrow:** Ready")
    st.markdown('</div>', unsafe_allow_html=True)
