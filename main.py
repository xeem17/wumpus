import streamlit as st
import random

ROWS, COLS = 4, 4

# ---------------- CUSTOM CSS ----------------
st.markdown("""
<style>
body {
    background: linear-gradient(135deg, #eef2ff, #f8fafc);
}

.grid {
    display: grid;
    grid-template-columns: repeat(4, 80px);
    gap: 12px;
}

.cell {
    height: 80px;
    border-radius: 12px;
    display:flex;
    align-items:center;
    justify-content:center;
    font-weight:bold;
    font-size:20px;
    transition: 0.2s;
}

.cell:hover {
    transform: scale(1.05);
}

/* states */
.agent { background:#3b82f6; color:white; }
.safe { background:#bbf7d0; }
.unknown { background:#e5e7eb; }
.danger { background:#fecaca; }
.gold { background:#fde68a; }

.panel {
    background:white;
    padding:15px;
    border-radius:12px;
    box-shadow:0 4px 10px rgba(0,0,0,0.05);
}
</style>
""", unsafe_allow_html=True)

# ---------------- WORLD ----------------
class World:
    def __init__(self):
        self.pits = {(2,3)}
        self.wumpus = (3,3)
        self.gold = (4,4)
        self.wumpusAlive = True

# ---------------- AGENT ----------------
class Agent:
    def __init__(self):
        self.r, self.c = 1,1
        self.visited = {(1,1)}
        self.danger = set()
        self.percepts = ["None"]
        self.hasGold = False

# ---------------- INIT ----------------
if "world" not in st.session_state:
    st.session_state.world = World()
    st.session_state.agent = Agent()
    st.session_state.steps = 0
    st.session_state.message = ""

world = st.session_state.world
agent = st.session_state.agent

# ---------------- LAYOUT ----------------
st.title("🧠 Wumpus KB Agent")
col1, col2 = st.columns([2,1])

# ---------------- GRID ----------------
with col1:
    st.subheader("Environment")

    grid_html = '<div class="grid">'
    for r in range(ROWS, 0, -1):
        for c in range(1, COLS+1):

            classes = "cell unknown"
            text = ""

            if (r,c) == (agent.r, agent.c):
                classes = "cell agent"
                text = "A"
            elif (r,c) in agent.visited:
                classes = "cell safe"
            elif (r,c) in agent.danger:
                classes = "cell danger"
                text = "✕"

            if (r,c) == world.gold and agent.hasGold:
                classes = "cell gold"
                text = "G"

            grid_html += f'<div class="{classes}">{text}</div>'

    grid_html += "</div>"

    st.markdown(grid_html, unsafe_allow_html=True)

# ---------------- SIDE PANEL ----------------
with col2:
    st.markdown('<div class="panel">', unsafe_allow_html=True)

    st.subheader("📊 Session")

    st.write("**Position:**", (agent.r, agent.c))
    st.write("**Percepts:**", ", ".join(agent.percepts))
    st.write("**Steps:**", st.session_state.steps)

    st.markdown("---")

    st.subheader("🏹 Status")
    st.success("Arrow Ready")

    st.markdown("---")

    st.subheader("🎯 Legend")
    st.write("🟦 Agent")
    st.write("🟩 Safe")
    st.write("⬜ Unknown")
    st.write("🟥 Danger")
    st.write("🟨 Gold")

    st.markdown('</div>', unsafe_allow_html=True)

# ---------------- BUTTONS ----------------
colA, colB = st.columns(2)

with colA:
    if st.button("🎮 New Game"):
        st.session_state.world = World()
        st.session_state.agent = Agent()
        st.session_state.steps = 0
        st.session_state.message = ""
        st.rerun()

with colB:
    if st.button("➡ Step Agent"):
        # simple movement demo
        moves = [(1,2),(2,1)]
        move = random.choice(moves)

        agent.r, agent.c = move
        agent.visited.add(move)
        agent.percepts = ["Exploring..."]

        st.session_state.steps += 1
        st.session_state.message = f"Moved to {move}"

        if move == world.gold:
            agent.hasGold = True
            agent.percepts = ["✨ Gold Found!"]

        st.rerun()

# ---------------- STATUS ----------------
if st.session_state.message:
    st.info(st.session_state.message)
