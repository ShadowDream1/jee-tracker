import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from streamlit_gsheets import GSheetsConnection
import time

# --- APP CONFIG & CYBER-DARK THEME ---
st.set_page_config(page_title="JEE Phase 3: Pro Mastery", layout="wide", page_icon="⚡")

# Custom CSS for the "Cool" Look
st.markdown("""
    <style>
    /* Global Theme */
    .stApp {
        background-color: #050505;
        color: #e0e0e0;
    }
    
    /* Metrics Styling */
    div[data-testid="stMetric"] {
        background: linear-gradient(145deg, #111111, #1a1a1a);
        border: 1px solid #333;
        border-radius: 12px;
        padding: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    div[data-testid="stMetricValue"] {
        color: #00e5ff !important;
        font-family: 'Courier New', monospace;
    }
    
    /* Tables/Schedule */
    .stDataFrame {
        border: 1px solid #333;
        border-radius: 10px;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background-color: #0a0a0a;
        padding: 10px;
        border-radius: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #1a1a1a;
        color: #888;
        border-radius: 6px;
        border: 1px solid #333;
    }
    .stTabs [aria-selected="true"] {
        background-color: #00e5ff !important;
        color: #000 !important;
        font-weight: bold;
    }
    
    /* Buttons */
    .stButton>button {
        background: linear-gradient(90deg, #00c6ff, #0072ff);
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: scale(1.02);
        box-shadow: 0 0 15px rgba(0, 229, 255, 0.6);
    }
    </style>
    """, unsafe_allow_html=True)

# --- DATABASE CONNECTION ---
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data(sheet):
    try:
        return conn.read(worksheet=sheet, ttl=0)
    except:
        return pd.DataFrame()

df_logs = load_data("Logs")
df_rev = load_data("Revision")

# --- PHASE 3 SCHEDULE DATA ---
# [cite_start]Start Date: 08-02-2026 [cite: 1]
PHASE_3_SCHEDULE = [
    [cite_start]{"Test": "Major Test-1", "Date": "2026-02-08", "Pattern": "Main + Adv", "Syllabus": "Full Syllabus [cite: 115]"},
    [cite_start]{"Test": "Major Test-2", "Date": "2026-02-15", "Pattern": "Main + Adv", "Syllabus": "Full Syllabus [cite: 115]"},
    [cite_start]{"Test": "Major Test-3", "Date": "2026-02-22", "Pattern": "Main + Adv", "Syllabus": "Full Syllabus [cite: 115]"},
    [cite_start]{"Test": "Major Test-4", "Date": "2026-03-01", "Pattern": "Main + Adv", "Syllabus": "Full Syllabus [cite: 115]"},
    [cite_start]{"Test": "Major Test-5", "Date": "2026-03-08", "Pattern": "Main + Adv", "Syllabus": "Full Syllabus [cite: 115]"},
    [cite_start]{"Test": "Major Test-6", "Date": "2026-03-15", "Pattern": "Main + Adv", "Syllabus": "Full Syllabus [cite: 115]"},
    [cite_start]{"Test": "Major Test-7", "Date": "2026-03-18", "Pattern": "JEE Main", "Syllabus": "Full Syllabus [cite: 119]"},
    [cite_start]{"Test": "Major Test-8", "Date": "2026-03-20", "Pattern": "JEE Main", "Syllabus": "Full Syllabus [cite: 119]"},
    [cite_start]{"Test": "AIOOT (Test-9)", "Date": "2026-03-22", "Pattern": "JEE Main", "Syllabus": "Full Syllabus (09:00 AM) [cite: 119]"},
    [cite_start]{"Test": "Major Test-10", "Date": "2026-03-25", "Pattern": "JEE Main", "Syllabus": "Full Syllabus [cite: 119]"},
    [cite_start]{"Test": "Major Test-11", "Date": "2026-03-27", "Pattern": "JEE Main", "Syllabus": "Full Syllabus [cite: 119]"},
    [cite_start]{"Test": "Major Test-12", "Date": "2026-03-29", "Pattern": "JEE Main", "Syllabus": "Full Syllabus [cite: 119]"},
    [cite_start]{"Test": "Major Test-13", "Date": "2026-04-12", "Pattern": "JEE Adv (2 Papers)", "Syllabus": "Full Syllabus [cite: 123]"},
    [cite_start]{"Test": "Major Test-14", "Date": "2026-04-19", "Pattern": "JEE Adv (2 Papers)", "Syllabus": "Full Syllabus [cite: 123]"},
    [cite_start]{"Test": "Major Test-15", "Date": "2026-04-26", "Pattern": "JEE Adv (2 Papers)", "Syllabus": "Full Syllabus [cite: 123]"},
    [cite_start]{"Test": "AIOOT (Test-16)", "Date": "2026-05-03", "Pattern": "JEE Adv (2 Papers)", "Syllabus": "Full Syllabus [cite: 123]"},
    [cite_start]{"Test": "AIOOT (Test-17)", "Date": "2026-05-10", "Pattern": "JEE Adv (2 Papers)", "Syllabus": "Full Syllabus [cite: 123]"},
    [cite_start]{"Test": "Major Test-18", "Date": "2026-05-13", "Pattern": "JEE Adv (2 Papers)", "Syllabus": "Full Syllabus [cite: 123]"},
]

# --- SYLLABUS FROM PDF (Pages 1-2) ---
SYLLABUS = {
    "Physics": [
        "Units & Measurements", "Vectors", "Kinematics", "NLM & Friction", "Circular Motion", "Work Power Energy", 
        "Centre of Mass", "Rotational Motion", "SHM", "Fluids", "Heat & Thermodynamics", "Electrostatics", 
        "Current & Capacitor", "Magnetism", "EMI & AC", "Geometrical Optics", "Waves & Sound", "Wave Optics", 
        "Modern Physics", "Errors", "Semiconductors"
    ],
    "Chemistry": [
        "Mole Concept", "Atomic Structure", "Periodic Table", "Chemical Bonding", "Stoichiometry", "Redox", 
        "Thermodynamics (I & II)", "Chemical Equilibrium", "Ionic Equilibrium", "GOC", "Isomerism", "Hydrocarbons", 
        "Solutions", "Electrochemistry", "Kinetics", "Coordination Compounds", "d & f Block", "Haloalkanes/Haloarenes", 
        "Alcohols/Phenols", "Carbonyls", "Amines", "Biomolecules", "Polymers", "Surface Chemistry", "Metallurgy", 
        "Solid State", "P-Block"
    ],
    "Maths": [
        "Algebra Basics", "Quadratic Eq", "Sets & Numbers", "Log & Sequence", "Trigonometry", "Solution of Triangle", 
        "P&C", "Binomial Theorem", "Straight Lines", "Circles", "Conics (Parabola/Ellipse/Hyperbola)", "Statistics", 
        "Functions & Relations", "ITF", "Limits", "Continuity & Diff", "MOD", "Tangent & Normal", "Monotonicity", 
        "Max/Min", "Matrices & Det", "Integration", "Diff Equations", "Area", "Vectors", "3D Geometry", 
        "Probability", "Complex Numbers"
    ]
}

# --- TABS LAYOUT ---
tab_dashboard, tab_schedule, tab_mastery, tab_focus = st.tabs(["🚀 Command Deck", "📅 Phase 3 Schedule", "🏆 Mastery Wall", "🧘 Zen Mode"])

# --- TAB 1: COMMAND DECK ---
with tab_dashboard:
    # Countdown Logic
    today = datetime.now()
    next_test = min([datetime.strptime(t["Date"], "%Y-%m-%d") for t in PHASE_3_SCHEDULE if datetime.strptime(t["Date"], "%Y-%m-%d") >= today], default=today)
    days_left = (next_test - today).days
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Next Test", f"{next_test.strftime('%b %d')}", f"{days_left} Days Left")
    c2.metric("Study Streak", "ACTIVE", "Keep going")
    c3.metric("Phase 3 Status", "Loading...", "Target 100%")
    
    st.markdown("---")
    
    # Quick Logger
    with st.container():
        st.subheader("⚡ Quick Log")
        with st.form("quick_log_form"):
            lc1, lc2, lc3 = st.columns(3)
            sub_select = lc1.selectbox("Subject", list(SYLLABUS.keys()))
            chap_select = lc2.selectbox("Chapter", SYLLABUS[sub_select])
            activity = lc3.selectbox("Activity", ["Theory", "Module Solving", "PYQs", "Revision"])
            
            hours = st.slider("Session Duration (Hrs)", 0.5, 6.0, 1.5)
            
            if st.form_submit_button("COMMIT SESSION"):
                st.toast(f"Logged {hours} hrs of {activity} on {chap_select}!", icon="🔥")
                # Save Logic
                new_row = pd.DataFrame([{
                    "Date": str(datetime.now().date()), 
                    "Subject": sub_select, 
                    "Chapter": chap_select, 
                    "Work_Type": activity, 
                    "Hours": hours
                }])
                updated_logs = pd.concat([df_logs, new_row], ignore_index=True)
                conn.update(worksheet="Logs", data=updated_logs)

# --- TAB 2: PHASE 3 SCHEDULE ---
with tab_schedule:
    st.markdown("### 🗓️ Target 2026: Phase 3 Roadmap")
    st.info("Start Date: 08-02-2026. All tests are Full Syllabus.")
    
    # Convert list to DataFrame for pretty display
    schedule_df = pd.DataFrame(PHASE_3_SCHEDULE)
    
    # Highlight next test
    def highlight_next(s):
        is_next = s['Date'] == next_test.strftime('%Y-%m-%d')
        return ['background-color: #004d40' if is_next else '' for _ in s]

    st.dataframe(
        schedule_df.style.apply(highlight_next, axis=1), 
        use_container_width=True,
        column_config={
            "Test": "Test Name",
            "Date": "Exam Date",
            "Pattern": "Exam Pattern",
            "Syllabus": "Coverage"
        },
        hide_index=True
    )

# --- TAB 3: MASTERY WALL ---
with tab_mastery:
    st.markdown("### 🏆 Syllabus Mastery Tracking")
    st.caption("Track your completion for the 18 Full Syllabus Tests.")
    
    col_m1, col_m2, col_m3 = st.columns(3)
    
    # Function to render subject column with UNIQUE KEYS
    def render_subject(col, name, chapters):
        with col:
            st.subheader(name)
            for chap in chapters:
                # We use 'name' + 'chap' to create a unique key (e.g., Physics_Vectors)
                # This prevents "Vectors" in Maths crashing with "Vectors" in Physics
                safe_key = f"{name}_{chap}".replace(" ", "_")
                
                with st.expander(chap):
                    c_chk1, c_chk2 = st.columns(2)
                    c_chk1.checkbox("Module", key=f"mod_{safe_key}")
                    c_chk2.checkbox("PYQs", key=f"pyq_{safe_key}")
                    st.progress(0.5) 
    
    render_subject(col_m1, "Physics", SYLLABUS["Physics"])
    render_subject(col_m2, "Chemistry", SYLLABUS["Chemistry"])
    render_subject(col_m3, "Maths", SYLLABUS["Maths"])

# --- TAB 4: ZEN MODE ---
with tab_focus:
    st.markdown("### 🧘 Deep Work Zone")
    c_f1, c_f2 = st.columns([1, 2])
    
    with c_f1:
        st.write("Set your timer:")
        minutes = st.number_input("Minutes", 15, 180, 45)
        if st.button("START FOCUS TIMER"):
            st.warning("Minimizing distractions...")
            # Timer logic would go here
            with st.empty():
                for seconds in range(minutes * 60, 0, -1):
                    st.metric("Time Remaining", f"{seconds // 60}:{seconds % 60:02d}")
                    time.sleep(1)
                st.success("Session Complete!")
    
    with c_f2:
        st.markdown("**Focus Soundscapes**")
        sound = st.radio("Ambience", ["Rain", "White Noise", "Deep Space"], horizontal=True)
        # Audio players
        if sound == "Rain":
            st.audio("https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3")
