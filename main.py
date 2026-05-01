import streamlit as st
import random

st.set_page_config(layout="wide")

ROWS, COLS = 4, 4

# ---------------- CSS ----------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@600&family=Inter:wght@400;500&display=swap');

body {
    background: radial-gradient(circle at top, #1a0f2e, #0d0a0e);
    color: #e8dcc8;
    font-family: 'Inter', sans-serif;
}

/* Title */
.title {
    font-family: 'Cinzel', serif;
    font-size: 34px;
    color: #d4a843;
    letter-spacing: 2px;
}

.subtitle {
    color: #8a7aa0;
    margin-bottom: 20px;
}

/* GRID */
.grid {
    display: grid;
    grid-template-columns: repeat(4, 90px);
    gap: 14px;
}

.cell {
    height: 90px;
    border-radius: 14px;
    display:flex;
    align-items:center;
    justify-content:center;
    font-size:20px;
    border:1px solid #2a2038;
}

.agent {
    background:#2a1a40;
    border-color:#6a3acc;
    box-shadow:0 0 18px rgba(106,58,204,0.6);
    color:#fff;
}

.safe { background:#1a2820; }
.unknown { background:#1c1628; }
.danger { background:#2a1515; color:#ff8080; }
.gold {
    background:#2a2210;
    border-color:#8c7030;
    box-shadow:0 0 12px rgba(212,168,67,0.4);
}

/* PANEL */
.panel {
    background:#13101a;
    padding:20px;
    border-radius:14px;
    border:1px solid #2a2038;
}

.metric {
    margin-bottom: 8px;
    color:#b8a8c8;
}

.value {
    font-family:'Cinzel';
    color:#d4a843;
}

/* Buttons */
.stButton>button {
    background: linear-gradient(135deg,#3a1e6e,#5a2e9e);
    color:white;
    border-radius:10px;
    height:50px;
    font-weight:bold;
    border:none;
}

.stButton>button:hover {
    background: linear-gradient(135deg,#4a2a8e,#6a3abe);
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
        self.r, self.c = 1,1
        self.visited = {(1,1)}
        self.danger = set()
        self.percepts = ["None"]
        self.hasGold = False

# ---------------- INIT ----------------
def init_game():
    st.session_state.world = World()
    st.session_state.agent = Agent()
    st.session_state.steps = 0
    st.session_state.game_over = False
    st.session_state.status = "EXPLORING"

if "world" not in st.session_state:
    init_game()

world = st.session_state.world
agent = st.session_state.agent

# ---------------- HEADER ----------------
st.markdown('<div class="title">WUMPUS WORLD</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Knowledge-Based Agent</div>', unsafe_allow_html=True)

# Status Badge
if st.session_state.status == "WIN":
    st.success("🏆 VICTORY")
elif st.session_state.status == "DEAD":
    st.error("💀 GAME OVER")
else:
    st.info("🟢 EXPLORING")

col1, col2 = st.columns([2,1])

# ---------------- GRID ----------------
with col1:
    grid_html = '<div class="grid">'

    for r in range(ROWS, 0, -1):
        for c in range(1, COLS+1):

            cls = "cell unknown"
            text = ""

            if (r,c) == (agent.r, agent.c):
                cls = "cell agent"
                text = "⚔"
            elif (r,c) in agent.visited:
                cls = "cell safe"
            elif (r,c) in agent.danger:
                cls = "cell danger"
                text = "?"

            if (r,c) == world.gold and agent.hasGold:
                cls = "cell gold"
                text = "✦"

            grid_html += f'<div class="{cls}">{text}</div>'

    grid_html += "</div>"
    st.markdown(grid_html, unsafe_allow_html=True)

# ---------------- SIDE PANEL ----------------
with col2:
    st.markdown('<div class="panel">', unsafe_allow_html=True)

    st.markdown(f"<div class='metric'>Steps: <span class='value'>{st.session_state.steps}</span></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='metric'>Position: <span class='value'>({agent.r},{agent.c})</span></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='metric'>Arrow: <span class='value'>READY</span></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='metric'>Gold: <span class='value'>{'FOUND' if agent.hasGold else 'Not Found'}</span></div>", unsafe_allow_html=True)

    st.markdown("---")

    st.markdown("**Current Percepts**")
    st.markdown(f"""
    <div style="
        background:#0d0a14;
        border:1px solid #2a2038;
        padding:10px;
        border-radius:8px;
        color:#a898c8;
        font-style:italic;
    ">
        {", ".join(agent.percepts)}
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    st.markdown("**Legend**")
    st.markdown("""
    🟪 Agent  
    🟩 Safe  
    🟫 Unknown  
    🟥 Danger  
    🟨 Gold  
    """)

    st.markdown('</div>', unsafe_allow_html=True)

# ---------------- BUTTONS ----------------
colA, colB = st.columns(2)

with colA:
    if st.button("🔄 New Game"):
        init_game()
        st.rerun()

with colB:
    if st.button("➡ Step Agent") and not st.session_state.game_over:

        moves = []
        for dr,dc in [(-1,0),(1,0),(0,-1),(0,1)]:
            nr, nc = agent.r+dr, agent.c+dc
            if 1 <= nr <= ROWS and 1 <= nc <= COLS:
                moves.append((nr,nc))

        move = random.choice(moves)

        agent.r, agent.c = move
        agent.visited.add(move)
        st.session_state.steps += 1

        if move in world.pits:
            agent.percepts = ["Fell into Pit"]
            st.session_state.game_over = True
            st.session_state.status = "DEAD"

        elif move == world.wumpus:
            agent.percepts = ["Eaten by Wumpus"]
            st.session_state.game_over = True
            st.session_state.status = "DEAD"

        elif move == world.gold:
            agent.hasGold = True
            agent.percepts = ["Gold Found!"]
            st.session_state.game_over = True
            st.session_state.status = "WIN"

        else:
            agent.percepts = ["Exploring..."]

        st.rerun()
