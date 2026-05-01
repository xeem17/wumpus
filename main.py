import streamlit as st
import random

st.set_page_config(layout="wide")

ROWS, COLS = 4, 4

# ---------------- LIGHT UI CSS ----------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');

body {
    background: linear-gradient(135deg, #f7f9fc, #eef3ff);
    font-family: 'Inter', sans-serif;
    color: #1f2a44;
}

.title {
    font-size: 34px;
    font-weight: 700;
    color: #2b3a67;
}

.subtitle {
    color: #5b6b8c;
    margin-bottom: 15px;
}

/* GRID */
.grid {
    display: grid;
    grid-template-columns: repeat(4, 85px);
    gap: 12px;
}

.cell {
    height: 85px;
    border-radius: 12px;
    display:flex;
    align-items:center;
    justify-content:center;
    font-size:18px;
    background: white;
    border: 1px solid #d9e2ef;
    box-shadow: 0 2px 6px rgba(0,0,0,0.05);
}

.agent {
    background: #4f8cff;
    color: white;
}

.safe {
    background: #e8f5e9;
}

.danger {
    background: #ffeaea;
}

.gold {
    background: #fff6cc;
    border: 2px solid #f4c542;
}

/* PANEL */
.panel {
    background: white;
    padding: 18px;
    border-radius: 14px;
    border: 1px solid #e3e9f5;
    box-shadow: 0 2px 10px rgba(0,0,0,0.05);
}

.metric {
    margin-bottom: 8px;
    color: #3a4a6b;
}

.value {
    font-weight: 600;
    color: #1f2a44;
}

.percept-box {
    background: #f4f7ff;
    padding: 10px;
    border-radius: 8px;
    border: 1px solid #dbe6ff;
}

.stButton>button {
    background: #4f8cff;
    color: white;
    border-radius: 10px;
    height: 45px;
    border: none;
}
</style>
""", unsafe_allow_html=True)

# ---------------- WORLD ----------------
class World:
    def __init__(self):
        self.pits = {(2,3)}
        self.wumpus = (3,3)
        self.gold = (4,4)

# ---------------- AGENT ----------------
class Agent:
    def __init__(self):
        self.r, self.c = 1, 1
        self.visited = {(1,1)}
        self.hasGold = False
        self.percepts = ["None"]

# ---------------- INIT ----------------
def init_game():
    st.session_state.world = World()
    st.session_state.agent = Agent()
    st.session_state.steps = 0
    st.session_state.status = "EXPLORING"
    st.session_state.game_over = False
    st.session_state.kb = 14
    st.session_state.steps_logical = 16

if "world" not in st.session_state:
    init_game()

world = st.session_state.world
agent = st.session_state.agent

# ---------------- PERCEPT FUNCTION ----------------
def get_percepts(r, c):
    percepts = []

    # Breeze (near pit)
    for pr, pc in world.pits:
        if abs(pr - r) + abs(pc - c) == 1:
            percepts.append("Breeze")

    # Stench (near wumpus)
    if abs(world.wumpus[0] - r) + abs(world.wumpus[1] - c) == 1:
        percepts.append("Stench")

    # Glitter (gold nearby or same cell)
    if (r, c) == world.gold:
        percepts.append("Glitter")

    if not percepts:
        percepts.append("Safe")

    return percepts

# ---------------- HEADER ----------------
st.markdown('<div class="title">WUMPUS WORLD</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Knowledge-Based Agent Simulation</div>', unsafe_allow_html=True)

# ---------------- STATUS ----------------
status = st.session_state.get("status", "EXPLORING")

if status == "WIN":
    st.success("🏆 VICTORY")
elif status == "DEAD":
    st.error("💀 GAME OVER")
else:
    st.info("🟢 EXPLORING")

col1, col2 = st.columns([2,1])

# ---------------- GRID ----------------
with col1:
    grid_html = '<div class="grid">'

    for r in range(ROWS, 0, -1):
        for c in range(1, COLS+1):

            cls = "cell"

            if (r,c) == (agent.r, agent.c):
                cls += " agent"
                text = "🤖"
            elif (r,c) in agent.visited:
                cls += " safe"
                text = ""
            else:
                cls += ""
                text = ""

            if (r,c) in world.pits:
                cls = "cell danger"
                text = "P"
            if (r,c) == world.wumpus:
                cls = "cell danger"
                text = "W"
            if (r,c) == world.gold:
                cls = "cell gold"
                text = "G"

            grid_html += f'<div class="{cls}">{text}</div>'

    grid_html += "</div>"
    st.markdown(grid_html, unsafe_allow_html=True)

# ---------------- UPDATE PERCEPTS ----------------
agent.percepts = get_percepts(agent.r, agent.c)

# ---------------- SIDE PANEL ----------------
with col2:
    st.markdown('<div class="panel">', unsafe_allow_html=True)

    st.markdown(f"<div class='metric'>Current Node: <span class='value'>({agent.r}, {agent.c})</span></div>", unsafe_allow_html=True)

    st.markdown("Active Percepts")
    st.markdown(f"<div class='percept-box'>{', '.join(agent.percepts)}</div>", unsafe_allow_html=True)

    st.markdown(f"<div class='metric'>Resolution Steps: <span class='value'>{st.session_state.steps_logical}</span></div>", unsafe_allow_html=True)

    st.markdown(f"<div class='metric'>KB Clauses: <span class='value'>{st.session_state.kb}</span></div>", unsafe_allow_html=True)

    st.markdown(f"<div class='metric'>🏹 Arrow: <span class='value'>Ready</span></div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

# ---------------- BUTTONS ----------------
colA, colB = st.columns(2)

with colA:
    if st.button("🔄 Reset"):
        init_game()
        st.rerun()

with colB:
    if st.button("➡ Move Agent") and not st.session_state.game_over:

        moves = []
        for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
            nr, nc = agent.r + dr, agent.c + dc
            if 1 <= nr <= ROWS and 1 <= nc <= COLS:
                moves.append((nr,nc))

        agent.r, agent.c = random.choice(moves)
        agent.visited.add((agent.r, agent.c))

        st.session_state.steps_logical += 1

        if (agent.r, agent.c) == world.pits or (agent.r, agent.c) == world.wumpus:
            st.session_state.status = "DEAD"
            st.session_state.game_over = True

        if (agent.r, agent.c) == world.gold:
            st.session_state.status = "WIN"
            agent.hasGold = True
            st.session_state.game_over = True

        st.rerun()
