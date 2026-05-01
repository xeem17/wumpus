import streamlit as st
import random

# --- CONFIG ---
st.set_page_config(page_title="Wumpus World Pro", layout="centered")

ROWS, COLS = 4, 4

# --- STYLING ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }

    .main {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
    }

    /* Game Container */
    .game-container {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 24px;
        padding: 2rem;
        backdrop-filter: blur(10px);
        box-shadow: 0 20px 50px rgba(0,0,0,0.3);
    }

    /* Grid System */
    .wumpus-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 12px;
        margin-bottom: 20px;
    }

    .cell {
        aspect-ratio: 1/1;
        border-radius: 12px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        font-size: 24px;
        font-weight: bold;
        transition: all 0.3s ease;
        border: 1px solid rgba(255,255,255,0.05);
        position: relative;
    }

    /* Cell States */
    .cell-unvisited { background: #334155; color: #475569; }
    .cell-visited { background: #1e293b; border: 1px solid #3b82f6; }
    .cell-agent { background: #3b82f6 !important; box-shadow: 0 0 20px rgba(59, 130, 246, 0.5); transform: scale(1.05); z-index: 2; }
    .cell-pit { background: #ef4444 !important; color: white; }
    .cell-wumpus { background: #9333ea !important; color: white; }
    .cell-gold { background: #f59e0b !important; color: #451a03; box-shadow: 0 0 20px rgba(245, 158, 11, 0.4); }

    /* Percept Labels */
    .percept-tag {
        font-size: 10px;
        text-transform: uppercase;
        margin-top: 4px;
        font-weight: 700;
        letter-spacing: 0.5px;
    }

    /* Sidebar/Stats */
    .stat-card {
        background: rgba(0,0,0,0.2);
        padding: 15px;
        border-radius: 15px;
        border: 1px solid rgba(255,255,255,0.1);
        margin-bottom: 10px;
    }
    
    .status-text {
        font-size: 1.2rem;
        font-weight: 700;
        text-align: center;
        padding: 10px;
        border-radius: 10px;
        margin-bottom: 20px;
    }

    /* Buttons */
    .stButton>button {
        width: 100%;
        border-radius: 12px;
        border: none;
        height: 50px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
        transition: all 0.2s;
    }
</style>
""", unsafe_allow_html=True)

# --- WORLD LOGIC ---
class World:
    def __init__(self):
        # Fixed positions for the example, but could be random
        self.pits = {(2, 3), (3, 1)}
        self.wumpus = (3, 3)
        self.gold = (4, 4)

class Agent:
    def __init__(self):
        self.r, self.c = 1, 1
        self.visited = {(1, 1)}
        self.arrows = 1
        self.score = 0

def init_game():
    st.session_state.world = World()
    st.session_state.agent = Agent()
    st.session_state.game_over = False
    st.session_state.status_msg = ("EXPLORING", "#3b82f6") # Text, Color

if "world" not in st.session_state:
    init_game()

w = st.session_state.world
a = st.session_state.agent

def get_percepts(r, c):
    p = []
    # Check neighbors for breeze
    for pr, pc in w.pits:
        if abs(pr - r) + abs(pc - c) == 1: p.append("Breeze")
    # Check neighbors for stench
    if abs(w.wumpus[0] - r) + abs(w.wumpus[1] - c) == 1: p.append("Stench")
    # Check current for gold
    if (r, c) == w.gold: p.append("Glitter")
    return list(set(p))

def move_agent(dr, dc):
    if st.session_state.game_over: return
    
    new_r, new_c = a.r + dr, a.c + dc
    if 1 <= new_r <= ROWS and 1 <= new_c <= COLS:
        a.r, a.c = new_r, new_c
        a.visited.add((a.r, a.c))
        a.score -= 1
        
        # Check deaths
        if (a.r, a.c) in w.pits:
            st.session_state.status_msg = ("FELL INTO PIT", "#ef4444")
            st.session_state.game_over = True
        elif (a.r, a.c) == w.wumpus:
            st.session_state.status_msg = ("EATEN BY WUMPUS", "#9333ea")
            st.session_state.game_over = True
        elif (a.r, a.c) == w.gold:
            st.session_state.status_msg = ("GOLD FOUND! YOU WIN", "#f59e0b")
            a.score += 1000
            st.session_state.game_over = True

# --- UI LAYOUT ---
st.title("🏹 Wumpus World")

col1, col2 = st.columns([1.5, 1])

with col1:
    # Status Header
    msg, color = st.session_state.status_msg
    st.markdown(f'<div class="status-text" style="background: {color}22; color: {color}; border: 1px solid {color}55;">{msg}</div>', unsafe_allow_html=True)

    # Grid Rendering
    grid_html = '<div class="wumpus-grid">'
    for r in range(ROWS, 0, -1):
        for c in range(1, COLS + 1):
            is_agent = (r, c) == (a.r, a.c)
            is_visited = (r, c) in a.visited
            percepts = get_percepts(r, c) if is_visited else []
            
            # Determine Class
            cls = "cell"
            content = ""
            
            if is_agent:
                cls += " cell-agent"
                content = "🤖"
            elif not is_visited:
                cls += " cell-unvisited"
                content = "?"
            else:
                cls += " cell-visited"
                if (r,c) in w.pits: 
                    cls += " cell-pit"; content = "🕳️"
                elif (r,c) == w.wumpus: 
                    cls += " cell-wumpus"; content = "👾"
                elif (r,c) == w.gold: 
                    cls += " cell-gold"; content = "💰"
                else:
                    # Show percept icons for visited cells
                    icons = []
                    if "Breeze" in percepts: icons.append("💨")
                    if "Stench" in percepts: icons.append("🤢")
                    if "Glitter" in percepts: icons.append("✨")
                    content = "".join(icons)
            
            # Percept Text Tags
            tag_html = ""
            if is_agent:
                tag_html = f'<div class="percept-tag">POS: {r},{c}</div>'
            
            grid_html += f'<div class="{cls}">{content}{tag_html}</div>'
    grid_html += '</div>'
    st.markdown(grid_html, unsafe_allow_html=True)

with col2:
    st.markdown('<div class="stat-card">', unsafe_allow_html=True)
    st.subheader("Agent Knowledge")
    current_percepts = get_percepts(a.r, a.c)
    if not current_percepts: current_percepts = ["Clear Air"]
    
    for p in current_percepts:
        st.info(f"**Percept:** {p}")
    
    st.markdown(f"**Score:** `{a.score}`")
    st.markdown(f"**Arrows:** `{'🏹' * a.arrows}`")
    st.markdown('</div>', unsafe_allow_html=True)

    # Controls
    st.write("---")
    u_col1, u_col2, u_col3 = st.columns(3)
    with u_col2: st.button("▲", on_click=move_agent, args=(1, 0))
    
    l_col1, l_col2, l_col3 = st.columns(3)
    with l_col1: st.button("◀", on_click=move_agent, args=(0, -1))
    with l_col2: st.button("▼", on_click=move_agent, args=(-1, 0))
    with l_col3: st.button("▶", on_click=move_agent, args=(0, 1))

    if st.button("🔄 Reset Environment"):
        init_game()
        st.rerun()

# --- FOOTER ---
st.caption("Instructions: Use the arrows to navigate. Find the Gold (💰) and avoid the Pits (🕳️) or the Wumpus (👾). Use 'Breeze' to sense pits nearby and 'Stench' for the Wumpus.")
