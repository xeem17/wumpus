import streamlit as st
import random

st.set_page_config(layout="wide")

ROWS, COLS = 4, 4

# ---------------- CSS ----------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');

body {
    background: #f6f8fc;
    font-family: 'Inter', sans-serif;
}

/* TITLE */
.title {
    font-size: 34px;
    font-weight: 700;
    color: #1f2937;
}

.subtitle {
    color: #6b7280;
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
    border: 1px solid #e5e7eb;
    box-shadow: 0 2px 6px rgba(0,0,0,0.05);
}

/* CELL COLORS */
.agent { background: #dbeafe; }
.safe { background: #dcfce7; }
.danger { background: #fee2e2; }
.gold { background: #fef9c3; border: 2px solid #facc15; }

/* PANEL */
.panel {
    background: #111827;
    padding: 18px;
    border-radius: 14px;
    border: 1px solid #374151;
    color: white;
}

/* TEXT */
.metric {
    margin-bottom: 10px;
    color: white;
    font-weight: 500;
}

/* PERCEPT BOX */
.percept-box {
    background: #1f2937;
    border: 1px solid #374151;
    padding: 10px;
    border-radius: 10px;
    color: #e5e7eb;
}

/* 🔘 DARK BUTTON */
.stButton>button {
    background: #111827 !important;
    color: white !important;
    border-radius: 10px;
    height: 48px;
    border: 1px solid #374151 !important;
    font-weight: 600;
}

.stButton>button:hover {
    background: #1f2937 !important;
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
        self.percepts = ["None"]
        self.hasGold = False

# ---------------- INIT ----------------
def init_game():
    st.session_state.world = World()
    st.session_state.agent = Agent()
    st.session_state.steps = 0
    st.session_state.status = "EXPLORING"
    st.session_state.game_over = False
    st.session_state.steps_logical = 16
    st.session_state.kb = 14

if "world" not in st.session_state:
    init_game()

world = st.session_state.world
agent = st.session_state.agent

# ---------------- PERCEPTS ----------------
def get_percepts(r, c):
    p = []

    for pr, pc in world.pits:
        if abs(pr - r) + abs(pc - c) == 1:
            p.append("Breeze")

    if abs(world.wumpus[0] - r) + abs(world.wumpus[1] - c) == 1:
        p.append("Stench")

    if (r, c) == world.gold:
        p.append("Glitter")

    if not p:
        p.append("Safe")

    return p

# ---------------- HEADER ----------------
st.markdown('<div class="title">WUMPUS WORLD</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Clean UI Knowledge-Based Agent</div>', unsafe_allow_html=True)

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
            text = ""

            if (r,c) == (agent.r, agent.c):
                cls += " agent"
                text = "🤖"
            elif (r,c) in agent.visited:
                cls += " safe"
            else:
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

# ---------------- PANEL ----------------
with col2:
    st.markdown('<div class="panel">', unsafe_allow_html=True)

    st.markdown(f"<div class='metric'>Current Node: ({agent.r}, {agent.c})</div>", unsafe_allow_html=True)

    st.markdown("Active Percepts")
    st.markdown(f"<div class='percept-box'>{', '.join(agent.percepts)}</div>", unsafe_allow_html=True)

    st.markdown(f"<div class='metric'>Resolution Steps: {st.session_state.steps_logical}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='metric'>KB Clauses: {st.session_state.kb}</div>", unsafe_allow_html=True)
    st.markdown("<div class='metric'>🏹 Arrow: Ready</div>", unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# ---------------- BUTTONS ----------------
colA, colB = st.columns(2)

with colA:
    if st.button("🔄 New Game"):
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

        if (agent.r, agent.c) in world.pits or (agent.r, agent.c) == world.wumpus:
            st.session_state.status = "DEAD"
            st.session_state.game_over = True

        if (agent.r, agent.c) == world.gold:
            st.session_state.status = "WIN"
            st.session_state.game_over = True

        st.rerun()
