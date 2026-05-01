import streamlit as st
import random
from collections import deque

# ---------------- CONFIG ----------------
ROWS, COLS = 4, 4
DIRS = [(-1,0),(1,0),(0,-1),(0,1)]

# ---------------- WORLD ----------------
class World:
    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self.pits = set()
        self.wumpus = None
        self.gold = None
        self.wumpusAlive = True
        self.generate()

    def neighbours(self, r, c):
        return [(r+dr, c+dc) for dr,dc in DIRS
                if 1 <= r+dr <= self.rows and 1 <= c+dc <= self.cols]

    def generate(self):
        start_safe = set(self.neighbours(1,1))
        start_safe.add((1,1))

        cells = [(r,c) for r in range(1,self.rows+1)
                        for c in range(1,self.cols+1)
                        if (r,c)!=(1,1)]

        for cell in cells:
            if cell not in start_safe and random.random() < 0.2:
                self.pits.add(cell)

        candidates = [c for c in cells if c not in self.pits and c not in start_safe]
        self.wumpus = random.choice(candidates if candidates else cells)

        candidates = []
        for r,c in cells:
            if (r,c) in self.pits or (r,c)==self.wumpus:
                continue
            if any(n not in self.pits for n in self.neighbours(r,c)):
                candidates.append((r,c))

        self.gold = random.choice(candidates if candidates else cells)

    def breeze(self, r, c):
        return any(n in self.pits for n in self.neighbours(r,c))

    def stench(self, r, c):
        return self.wumpusAlive and any(n == self.wumpus for n in self.neighbours(r,c))


# ---------------- KB ----------------
class KB:
    def __init__(self):
        self.clauses = []

    def tell(self, clause):
        c = set(clause)
        for l in c:
            if negate(l) in c:
                return
        if c not in self.clauses:
            self.clauses.append(c)

    def ask(self, query):
        sos = [set([negate(query)])]

        while sos:
            c1 = sos.pop(0)
            for c2 in self.clauses:
                for lit in c1:
                    if negate(lit) in c2:
                        new = (c1 | c2) - {lit, negate(lit)}
                        if not new:
                            return True
                        sos.append(new)
        return False


def negate(l):
    return l[1:] if l.startswith('-') else '-' + l


# ---------------- AGENT ----------------
class Agent:
    def __init__(self):
        self.r, self.c = 1,1
        self.safe = {(1,1)}
        self.visited = {(1,1)}
        self.danger = set()
        self.hasGold = False

    def perceive(self, world, kb):
        r,c = self.r, self.c

        kb.tell([f"-P_{r}_{c}"])
        kb.tell([f"-W_{r}_{c}"])

        breeze = world.breeze(r,c)
        stench = world.stench(r,c)

        kb.tell([f"B_{r}_{c}" if breeze else f"-B_{r}_{c}"])
        kb.tell([f"S_{r}_{c}" if stench else f"-S_{r}_{c}"])

        return breeze, stench, (world.gold == (r,c))

    def infer(self, world, kb):
        for r in range(1,world.rows+1):
            for c in range(1,world.cols+1):
                if (r,c) in self.safe or (r,c) in self.danger:
                    continue

                if kb.ask(f"-P_{r}_{c}") and kb.ask(f"-W_{r}_{c}"):
                    self.safe.add((r,c))
                elif kb.ask(f"P_{r}_{c}") or kb.ask(f"W_{r}_{c}"):
                    self.danger.add((r,c))


# ---------------- UI FUNCTIONS ----------------
def draw_grid(world, agent):
    grid = ""
    for r in range(world.rows, 0, -1):
        row = ""
        for c in range(1, world.cols+1):
            cell = "⬜"

            if (r,c) == (agent.r, agent.c):
                cell = "🤖"
            elif (r,c) in agent.visited:
                if (r,c) in world.pits:
                    cell = "🕳"
                elif (r,c) == world.wumpus and world.wumpusAlive:
                    cell = "👹"
                elif (r,c) == world.gold:
                    cell = "💰"
                else:
                    cell = "🟩"
            elif (r,c) in agent.danger:
                cell = "❌"

            row += cell + " "
        grid += row + "\n"
    return grid


# ---------------- SESSION STATE ----------------
if "world" not in st.session_state:
    st.session_state.world = World(ROWS, COLS)
    st.session_state.agent = Agent()
    st.session_state.kb = KB()
    st.session_state.game_over = False
    st.session_state.message = ""

world = st.session_state.world
agent = st.session_state.agent
kb = st.session_state.kb

# ---------------- UI ----------------
st.title("🧠 Wumpus World (AI Agent)")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Grid")
    st.text(draw_grid(world, agent))

with col2:
    st.subheader("Status")
    st.write(f"Position: ({agent.r},{agent.c})")
    st.write(st.session_state.message)

# ---------------- BUTTONS ----------------
if st.button("Restart"):
    st.session_state.world = World(ROWS, COLS)
    st.session_state.agent = Agent()
    st.session_state.kb = KB()
    st.session_state.game_over = False
    st.session_state.message = ""
    st.rerun()

if st.button("Step") and not st.session_state.game_over:
    breeze, stench, glitter = agent.perceive(world, kb)

    if (agent.r,agent.c) in world.pits:
        st.session_state.message = "💀 Fell into Pit"
        st.session_state.game_over = True

    elif (agent.r,agent.c) == world.wumpus and world.wumpusAlive:
        st.session_state.message = "💀 Eaten by Wumpus"
        st.session_state.game_over = True

    elif glitter:
        st.session_state.message = "🏆 Gold Found!"
        st.session_state.game_over = True

    else:
        agent.infer(world, kb)

        choices = [c for c in agent.safe if c not in agent.visited]

        if not choices:
            st.session_state.message = "⚠ No safe moves"
            st.session_state.game_over = True
        else:
            nr,nc = random.choice(choices)
            agent.r, agent.c = nr,nc
            agent.visited.add((nr,nc))

            st.session_state.message = f"Moved to ({nr},{nc})"

    st.rerun()
