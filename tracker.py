import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from streamlit_gsheets import GSheetsConnection
import time

# --- APP CONFIG & THEME ---
st.set_page_config(page_title="JEE Adv. Pro Tracker", layout="wide", page_icon="🎯")

# --- CUSTOM CSS FOR UI ---
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
    }
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
    """, unsafe_content_allowed=True)

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
    st.error("Connect your Google Sheet first!")
    st.stop()

# --- SIDEBAR: THE VIBE CONSOLE ---
st.sidebar.title("🎮 Vibe Console")

# 1. Motivational Quote
quotes = [
    "“The only way to learn mathematics is to do mathematics.” – Paul Halmos",
    "“Inorganic is scoring. Don't neglect the NCERT lines.”",
    "“Discipline is doing what needs to be done, even if you don't want to.”",
    "“Your future self will thank you for today's Block 1.”"
]
st.sidebar.caption(quotes[int(time.time() % len(quotes))])

# 2. Background / Theme
theme = st.sidebar.selectbox("Theme", ["Deep Space", "Midnight Study", "Forest Rain"])

# 3. Focus Music (Embeds)
st.sidebar.subheader("🎧 Focus Sounds")
track = st.sidebar.radio("Audio Mode", ["Silence", "Rain", "White Noise", "Brown Noise"])
audio_urls = {
    "Rain": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3", # Replace with actual loop URLs
    "White Noise": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-2.mp3",
    "Brown Noise": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-3.mp3"
}
if track != "Silence":
    st.sidebar.audio(audio_urls[track], format="audio/mp3", loop=True)

# 4. Links Widget
st.sidebar.subheader("🔗 Quick Links")
st.sidebar.markdown("[🎯 Practice on Marks.app](https://web.getmarks.app/)")

# --- MAIN UI: COUNTDOWNS ---
col_c1, col_c2, col_c3 = st.columns(3)

def get_countdown(target_date):
    delta = target_date - datetime.now()
    return f"{delta.days}d {delta.seconds//3600}h"

# JEE Main 2nd Attempt: April 2, 2026
# JEE Advanced: May 18, 2026
c_april = datetime(2026, 4, 2)
c_may = datetime(2026, 5, 18)

col_c1.metric("JEE Main (Apr 2)", get_countdown(c_april))
col_c2.metric("JEE Advanced (May 18)", get_countdown(c_may))

# --- TABS ---
tab_log, tab_rev, tab_syllabus, tab_focus = st.tabs(["⏱️ Daily Logger", "🧠 Spaced Repetition", "📚 Syllabus Reference", "🧘 Focus Mode"])

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
            
            # Logic: Auto-lock subject for Block 1 and Block 4
            if "Block 1" in block:
                subject = st.selectbox("Subject", ["Mathematics"], disabled=True)
            elif "Block 4" in block:
                subject = st.selectbox("Subject", ["Chemistry (Inorganic)"], disabled=True)
            else:
                subject = st.selectbox("Subject", ["Physics", "Chemistry (Physical/Org)", "Mathematics"])
            
            topic = st.text_input("Topic Name", placeholder="Enter Chapter...")

        with c2:
            hours = st.slider("Hours Studied", 0.5, 6.0, 2.0, 0.5)
            st.write("Resources Used:")
            res_cols = st.columns(2)
            m = res_cols[0].checkbox("FIITJEE Module")
            p = res_cols[0].checkbox("20Y PYQs")
            r = res_cols[1].checkbox("Review Booklet")
            s = res_cols[1].checkbox("Short Notes")
            
        if st.button("🔥 Complete Session"):
            if topic:
                # Add sound effect (Browser plays this on success)
                st.balloons()
                st.toast("Session Saved! Playing Chime...", icon="🔔")
                
                # Logic to save to GSheets
                new_row = pd.DataFrame([{"Date": str(datetime.now().date()), "Block": block, "Subject": subject, "Topic": topic, "Hours": hours}])
                updated_df = pd.concat([df_logs, new_row], ignore_index=True)
                conn.update(worksheet="Logs", data=updated_df)
                
                # Add to revision if not there
                if topic not in df_rev['Topic'].values:
                    new_rev = pd.DataFrame([{"Topic": topic, "Last_Studied": str(datetime.now().date()), "Next_Review": str(datetime.now().date() + timedelta(days=1)), "Iteration": 1}])
                    df_rev = pd.concat([df_rev, new_rev], ignore_index=True)
                    conn.update(worksheet="Revision", data=df_rev)
                
                st.success("Log Synced to Cloud!")
            else:
                st.warning("Please enter a topic name.")

# --- TAB 2: REVISION TRACKER ---
with tab_rev:
    st.header("Spaced Revision List")
    st.caption("Showing chapters based on your study history.")
    
    df_rev['Next_Review'] = pd.to_datetime(df_rev['Next_Review']).dt.date
    today = datetime.now().date()
    due = df_rev[df_rev['Next_Review'] <= today]
    
    if due.empty:
        st.success("No revisions due today. Keep pushing the syllabus!")
    else:
        for i, row in due.iterrows():
            with st.expander(f"📌 {row['Topic']} (Last Revised: {row['Last_Studied']})"):
                st.write(f"This is iteration #{row['Iteration']}.")
                if st.button("Mark as Revised", key=f"rev_{i}"):
                    days = 2**int(row['Iteration'])
                    df_rev.at[i, 'Next_Review'] = str(today + timedelta(days=days))
                    df_rev.at[i, 'Last_Studied'] = str(today)
                    df_rev.at[i, 'Iteration'] = int(row['Iteration']) + 1
                    conn.update(worksheet="Revision", data=df_rev)
                    st.rerun()

# --- TAB 3: SYLLABUS REFERENCE ---
with tab_syllabus:
    st.header("Syllabus Checklist")
    
    col_s1, col_s2, col_s3 = st.columns(3)
    
    with col_s1:
        with st.expander("🧪 Chemistry"):
            st.markdown("**Physical:** Mole Concept, Thermodynamics, Equilibrium, Kinetics, Solid State.")
            st.markdown("**Inorganic:** P-Block, Coordination, Metallurgy, Qualitative Analysis.")
            st.markdown("**Organic:** Hydrocarbons, Halides, Alcohols, Carbonyls, Amines, Polymers.")
            
    with col_s2:
        with st.expander("🔭 Physics"):
            st.markdown("**Mechanics:** Kinematics, NLM, Rotation, Gravitation, Fluids.")
            st.markdown("**Thermal:** Calorimetry, Thermo, KTG.")
            st.markdown("**Elec/Mag:** Electrostatics, Capacitors, Current, EMI, AC.")
            
    with col_s3:
        with st.expander("📐 Mathematics"):
            st.markdown("**Algebra:** Sets, Complex, Matrices, P&C, Probability.")
            st.markdown("**Calculus:** Limits, Derivatives, Integration, Diff Equations.")
            st.markdown("**Coordinate:** Straight Lines, Circles, Conics.")

# --- TAB 4: FOCUS MODE ---
with tab_focus:
    st.header("🧘 Focus Timer")
    duration = st.number_input("Set Timer (Minutes)", 1, 180, 25)
    if st.button("Start Timer"):
        st.warning("Focus Mode Active. Don't leave this tab!")
        progress_bar = st.progress(0)
        for i in range(duration * 60):
            time.sleep(1)
            progress_bar.progress((i + 1) / (duration * 60))
        st.success("Time's Up! Great Session.")
        st.balloons()
