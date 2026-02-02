import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from streamlit_gsheets import GSheetsConnection
import time

# --- APP CONFIG & THEME ---
st.set_page_config(page_title="JEE Adv. Pro Tracker", layout="wide", page_icon="🎯")

# --- FIXED CSS FOR UI ---
st.markdown("""
    <style>
    .stMetric {
        background-color: #1e2130;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #3e4259;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #FF4B4B;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True) # FIXED PARAMETER NAME HERE

# --- DATABASE CONNECTION ---
conn = st.connection("gsheets", type=GSheetsConnection)

def load_logs():
    return conn.read(worksheet="Logs", ttl=0)

def load_revision():
    return conn.read(worksheet="Revision", ttl=0)

# --- DATA LOADING ---
try:
    df_logs = load_logs()
    df_rev = load_revision()
except:
    st.error("Connect your Google Sheet first! Ensure tabs 'Logs' and 'Revision' exist.")
    st.stop()

# --- SIDEBAR: THE VIBE CONSOLE ---
st.sidebar.title("🎮 Vibe Console")
st.sidebar.caption("“Your future self will thank you for today's Block 1.”")

# Focus Music
st.sidebar.subheader("🎧 Focus Sounds")
track = st.sidebar.radio("Audio Mode", ["Silence", "Rain", "White Noise", "Brown Noise"])
audio_urls = {
    "Rain": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3", 
    "White Noise": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-2.mp3",
    "Brown Noise": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-3.mp3"
}
if track != "Silence":
    st.sidebar.audio(audio_urls[track], format="audio/mp3", loop=True)

st.sidebar.markdown("---")
st.sidebar.markdown("[🎯 Practice on Marks.app](https://web.getmarks.app/)")

# --- MAIN UI: COUNTDOWNS ---
col_c1, col_c2 = st.columns(2)

def get_countdown(target_date):
    delta = target_date - datetime.now()
    return f"{delta.days}d {delta.seconds//3600}h"

c_april = datetime(2026, 4, 2)
c_may = datetime(2026, 5, 18)

col_c1.metric("JEE Main (Apr 2)", get_countdown(c_april))
col_c2.metric("JEE Advanced (May 18)", get_countdown(c_may))

# --- TABS ---
tab_log, tab_rev, tab_syllabus, tab_focus = st.tabs(["⏱️ Daily Logger", "🧠 Spaced Repetition", "📚 Syllabus Check", "🧘 Focus Mode"])

# --- TAB 1: SMART LOGGER ---
with tab_log:
    st.header("Log Session")
    with st.container():
        c1, c2 = st.columns(2)
        with c1:
            block = st.selectbox("Select Study Block", [
                "Block 1 (5AM-11AM): Pure Maths",
                "Block 2 (1PM-4PM): Revision",
                "Block 3 (5PM-10PM): Physics/Chem",
                "Block 4 (Late Night): Inorganic NCERT"
            ])
            
            if "Block 1" in block:
                subject = st.selectbox("Subject", ["Mathematics"], key="sb1")
            elif "Block 4" in block:
                subject = st.selectbox("Subject", ["Chemistry (Inorganic)"], key="sb4")
            else:
                subject = st.selectbox("Subject", ["Physics", "Chemistry (Physical/Org)", "Mathematics"], key="sb_other")
            
            topic = st.text_input("Topic Name", placeholder="Enter Chapter...")

        with c2:
            hours = st.slider("Hours Studied", 0.5, 8.0, 2.0, 0.5)
            st.write("Marked for Later?")
            save_q = st.checkbox("Save high-yield questions from this session?")
            
        if st.button("🔥 Complete Session"):
            if topic:
                st.balloons()
                # Save Log
                new_row = pd.DataFrame([{"Date": str(datetime.now().date()), "Block": block, "Subject": subject, "Topic": topic, "Hours": hours}])
                updated_df = pd.concat([df_logs, new_row], ignore_index=True)
                conn.update(worksheet="Logs", data=updated_df)
                
                # Update Revision
                if topic not in df_rev['Topic'].values:
                    new_rev = pd.DataFrame([{"Topic": topic, "Last_Studied": str(datetime.now().date()), "Next_Review": str(datetime.now().date() + timedelta(days=1)), "Iteration": 1}])
                    df_rev = pd.concat([df_rev, new_rev], ignore_index=True)
                    conn.update(worksheet="Revision", data=df_rev)
                
                st.success("Log Synced! Sound Chime: 🔔")
                time.sleep(1)
                st.rerun()

# --- TAB 2: REVISION TRACKER ---
with tab_rev:
    st.header("Due for Revision")
    df_rev['Next_Review'] = pd.to_datetime(df_rev['Next_Review']).dt.date
    today = datetime.now().date()
    due = df_rev[df_rev['Next_Review'] <= today]
    
    if due.empty:
        st.success("No revisions due today!")
    else:
        for i, row in due.iterrows():
            c_a, c_b = st.columns([4, 1])
            c_a.write(f"📌 **{row['Topic']}** (Iter: {row['Iteration']})")
            if c_b.button("Done", key=f"rev_btn_{i}"):
                days = 2**int(row['Iteration'])
                df_rev.at[i, 'Next_Review'] = str(today + timedelta(days=days))
                df_rev.at[i, 'Last_Studied'] = str(today)
                df_rev.at[i, 'Iteration'] = int(row['Iteration']) + 1
                conn.update(worksheet="Revision", data=df_rev)
                st.rerun()

# --- TAB 3: SYLLABUS CHECKLIST ---
with tab_syllabus:
    st.header("Syllabus Master List")
    # Using your provided syllabus lists
    chem_list = ["Mole Concept", "Atomic Structure", "Thermodynamics", "Equilibrium", "Electrochemistry", "P-Block", "Coordination", "General Organic", "Hydrocarbons", "Carbonyls"]
    phys
