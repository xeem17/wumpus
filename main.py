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
        self.percepts = ["None"]   # IMPORTANT FIX
        self.hasGold = False

# ---------------- INIT SESSION ----------------
def init_game():
    st.session_state.world = World()
    st.session_state.agent = Agent()
    st.session_state.steps = 0
    st.session_state.message = ""
    st.session_state.game_over = False

if "world" not in st.session_state:
    init_game()

world = st.session_state.world
agent = st.session_state.agent

# safety fix (prevents AttributeError)
if "percepts" not in vars(agent):
    agent.percepts = ["None"]

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
        init_game()
        st.rerun()

with colB:
    if st.button("➡ Step Agent") and not st.session_state.game_over:

        # possible moves
        moves = []
        for dr,dc in [(-1,0),(1,0),(0,-1),(0,1)]:
            nr = agent.r + dr
            nc = agent.c + dc
            if 1 <= nr <= ROWS and 1 <= nc <= COLS:
                moves.append((nr,nc))

        if not moves:
            st.session_state.message = "⚠ No moves"
            st.session_state.game_over = True
        else:
            move = random.choice(moves)

            agent.r, agent.c = move
            agent.visited.add(move)
            st.session_state.steps += 1

            # check events
            if move in world.pits:
                agent.percepts = ["💀 Fell into Pit"]
                st.session_state.message = "Game Over"
                st.session_state.game_over = True

            elif move == world.wumpus and world.wumpusAlive:
                agent.percepts = ["💀 Eaten by Wumpus"]
                st.session_state.message = "Game Over"
                st.session_state.game_over = True

            elif move == world.gold:
                agent.hasGold = True
                agent.percepts = ["✨ Gold Found!"]
                st.session_state.message = "🏆 You Win!"
                st.session_state.game_over = True

            else:
                agent.percepts = ["Exploring..."]
                st.session_state.message = f"Moved to {move}"

        st.rerun()

# ---------------- STATUS ----------------
if st.session_state.message:
    st.info(st.session_state.message)
