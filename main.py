import streamlit as st
import random

# 1. PAGE SETUP
st.set_page_config(page_title="Wumpus World AI", layout="wide")

# 2. SESSION STATE (Initialization)
if "agent_pos" not in st.session_state:
    st.session_state.agent_pos = [1, 1]  # [row, col]
    st.session_state.visited = {(1, 1)}
    st.session_state.steps = 0
    st.session_state.kb_clauses = 14
    st.session_state.game_over = False
    st.session_state.status = "EXPLORING"
    # Fixed World Layout
    st.session_state.pits = {(3, 1), (2, 3)} 
    st.session_state.wumpus = (3, 3)
    st.session_state.gold = (4, 4)

# 3. CSS (Light Mode + Dark Buttons + Better Colors)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    
    html, body, [class*="st-"] {
        font-family: 'Inter', sans-serif;
        background-color: #fcfcfd;
    }

    /* Metric Table Style from Screenshot */
    .stats-container { background: white; padding: 20px; border-radius: 12px; }
    .metric-row {
        display: flex; justify-content: space-between;
        padding: 12px 0; border-bottom: 1px dotted #e2e8f0;
        font-size: 16px; color: #475569;
    }
    .metric-value { font-weight: 700; color: #1e293b; }

    /* Grid Tile Colors */
    .grid-container { display: grid; grid-template-columns: repeat(4, 85px); gap: 10px; justify-content: center; }
    .tile {
        width: 85px; height: 85px; border-radius: 12px;
        display: flex; align-items: center; justify-content: center;
        font-size: 28px; border: 1px solid #eef2f6; transition: 0.3s;
    }
    .tile-empty { background: white; box-shadow: inset 0 0 5px rgba(0,0,0,0.02); }
    .tile-visited { background: #f0fdf4; border-color: #dcfce7; } /* Soft Green */
    .tile-agent { background: #3b82f6 !important; color: white; box-shadow: 0 8px 15px rgba(59,130,246,0.3); } /* Bold Blue */
    .tile-pit { background: #fee2e2 !important; border-color: #fecaca; } /* Red */
    .tile-wumpus { background: #f3e8ff !important; border-color: #e9d5ff; } /* Purple */
    .tile-gold { background: #fef9c3 !important; border-color: #fef08a; } /* Gold */

    /* DARK Movement Buttons */
    .stButton>button {
        background-color: #1e293b !important;
        color: white !important;
        border-radius: 8px !important;
        border: none !important;
        height: 45px !important;
        width: 100% !important;
        font-weight: bold !important;
    }
    .stButton>button:hover { background-color: #334155 !important; }
    
    .instruction-box { background: white; padding: 20px; border-radius: 12px; border: 1px solid #e2e8f0; }
</style>
""", unsafe_allow_html=True)

# 4. LOGIC
def get_percepts(r, c):
    p = []
    # Check for breeze
    for pr, pc in st.session_state.pits:
        if abs(pr - r) + abs(pc - c) == 1: p.append("Breeze")
    # Check for stench
    wr, wc = st.session_state.wumpus
    if abs(wr - r) + abs(wc - c) == 1: p.append("Stench")
    # Check for glitter
    if (r, c) == st.session_state.gold: p.append("Glitter")
    return p

def move(dr, dc):
    if st.session_state.game_over: return
    
    new_r = st.session_state.agent_pos[0] + dr
    new_c = st.session_state.agent_pos[1] + dc
    
    if 1 <= new_r <= 4 and 1 <= new_c <= 4:
        st.session_state.agent_pos = [new_r, new_c]
        st.session_state.visited.add((new_r, new_c))
        st.session_state.steps += 1
        st.session_state.kb_clauses += random.randint(2, 6)
        
        # Check Collision
        pos = (new_r, new_c)
        if pos in st.session_state.pits:
            st.session_state.status = "DEAD (FELL IN PIT)"
            st.session_state.game_over = True
        elif pos == st.session_state.wumpus:
            st.session_state.status = "DEAD (EATEN BY WUMPUS)"
            st.session_state.game_over = True
        elif pos == st.session_state.gold:
            st.session_state.status = "WINNER (GOLD FOUND)"
            st.session_state.game_over = True

# 5. UI DISPLAY
st.title("🏹 Wumpus World AI")

col_inst, col_grid, col_stats = st.columns([1, 1.2, 1])

# --- LEFT COLUMN: INSTRUCTIONS ---
with col_inst:
    st.markdown('<div class="instruction-box">', unsafe_allow_html=True)
    st.subheader("Instructions")
    st.write("Find the **Gold** (💰) and return safely.")
    st.write("💨 **Breeze**: Pit is nearby")
    st.write("🤢 **Stench**: Wumpus is nearby")
    st.write("✨ **Glitter**: Gold is here!")
    if st.button("🔄 Reset Environment"):
        for key in list(st.session_state.keys()): del st.session_state[key]
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# --- MIDDLE COLUMN: THE GRID ---
with col_grid:
    # Status Banner
    if st.session_state.game_over:
        if "WIN" in st.session_state.status: st.success(f"🏆 {st.session_state.status}")
        else: st.error(f"💀 {st.session_state.status}")
    else:
        st.info("🟢 Status: Exploring Cave...")

    # Rendering Grid
    grid_html = '<div class="grid-container">'
    for r in range(4, 0, -1):
        for c in range(1, 5):
            cur_pos = (r, c)
            is_agent = cur_pos == tuple(st.session_state.agent_pos)
            is_visited = cur_pos in st.session_state.visited
            
            tile_class = "tile tile-empty"
            content = ""
            
            if is_agent:
                tile_class = "tile tile-agent"; content = "🤖"
            elif is_visited:
                tile_class = "tile tile-visited"
                if cur_pos in st.session_state.pits: tile_class = "tile tile-pit"; content = "🕳️"
                elif cur_pos == st.session_state.wumpus: tile_class = "tile tile-wumpus"; content = "👾"
                elif cur_pos == st.session_state.gold: tile_class = "tile tile-gold"; content = "💰"
                else:
                    percepts = get_percepts(r, c)
                    if "Breeze" in percepts: content = "💨"
                    elif "Stench" in percepts: content = "🤢"
            
            grid_html += f'<div class="{tile_class}">{content}</div>'
    grid_html += '</div>'
    st.markdown(grid_html, unsafe_allow_html=True)

    # Movement Controls
    st.write("")
    bc1, bc2, bc3 = st.columns(3)
    with bc2: st.button("▲", on_click=move, args=(1, 0))
    bc4, bc5, bc6 = st.columns(3)
    with bc4: st.button("◀", on_click=move, args=(0, -1))
    with bc5: st.button("▼", on_click=move, args=(-1, 0))
    with bc6: st.button("▶", on_click=move, args=(0, 1))

# --- RIGHT COLUMN: STATS ---
with col_stats:
    st.markdown('<div class="stats-container">', unsafe_allow_html=True)
    
    p_list = get_percepts(st.session_state.agent_pos[0], st.session_state.agent_pos[1])
    p_display = ", ".join(p_list) if p_list else "None"
    
    metrics = [
        ("Current Node", f"({st.session_state.agent_pos[0]}, {st.session_state.agent_pos[1]})"),
        ("Active Percepts", p_display),
        ("Resolution Steps", st.session_state.steps),
        ("KB Clauses", st.session_state.kb_clauses)
    ]
    
    for label, val in metrics:
        st.markdown(f"""
            <div class="metric-row">
                <span class="metric-label">{label}</span>
                <span class="metric-value">{val}</span>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>🏹 **Arrow:** Ready", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
