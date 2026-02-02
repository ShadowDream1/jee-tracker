import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from streamlit_gsheets import GSheetsConnection

# --- CONFIGURATION ---
st.set_page_config(page_title="JEE Adv. Tracker", layout="wide", page_icon="⚛️")

# --- DATABASE CONNECTION ---
# This establishes a connection to your Google Sheet
conn = st.connection("gsheets", type=GSheetsConnection)

def get_data(worksheet_name):
    # Read data from the specific worksheet (Logs or Revision)
    # ttl=0 ensures we don't cache old data
    try:
        return conn.read(worksheet=worksheet_name, ttl=0, usecols=list(range(6)))
    except:
        return pd.DataFrame()

def update_data(df, worksheet_name):
    # Write data back to the sheet
    conn.update(worksheet=worksheet_name, data=df)

# --- SIDEBAR & QUOTE ---
st.sidebar.title("🚀 JEE Advanced Mode")
st.sidebar.markdown("*“If I push hard, I think I can finish by the end of March.”*")
st.sidebar.markdown("---")

# --- LOAD DATA ---
# We load data at the start to calculate streaks
try:
    df_logs = get_data("Logs")
    # Ensure correct columns if sheet is empty
    if df_logs.empty:
        df_logs = pd.DataFrame(columns=["Date", "Block", "Subject", "Topic", "Hours", "Focus_Area"])
    
    df_rev = get_data("Revision")
    if df_rev.empty:
        df_rev = pd.DataFrame(columns=["Topic", "Last_Studied", "Next_Review", "Iteration"])

    # Streak Calculation
    if not df_logs.empty:
        # Convert Date column to datetime objects
        df_logs['Date'] = pd.to_datetime(df_logs['Date'], errors='coerce').dt.date
        unique_days = df_logs['Date'].nunique()
        st.sidebar.metric("Active Days Tracked", f"{unique_days} Days")
    else:
        st.sidebar.info("Start logging to see stats.")

except Exception as e:
    st.error(f"Connection Error: Please check your Secrets! {e}")
    st.stop()

# --- MAIN TABS ---
tab1, tab2, tab3, tab4 = st.tabs(["⏱️ Daily Logger", "📊 Analytics", "🧠 Spaced Revision", "📜 Strategy"])

# --- TAB 1: DAILY LOGGER ---
with tab1:
    st.header("Log Your Blocks")
    c1, c2 = st.columns(2)
    
    with c1:
        date_input = st.date_input("Date", datetime.now())
        block_input = st.selectbox("Select Block", [
            "Block 1: Pure Maths (5AM - 11AM)", 
            "Block 2: Spaced Revision (1PM - 3:30PM)", 
            "Block 3: Phys/Chem Solving (5PM - 10PM)", 
            "Block 4: Inorganic/Short Notes (Late Night)"
        ])
        subject_input = st.radio("Subject", ["Mathematics", "Physics", "Chemistry"], horizontal=True)
        topic_input = st.text_input("Chapter/Topic Name")

    with c2:
        hours_input = st.number_input("Hours", 0.0, 12.0, step=0.5, value=2.0)
        st.write("**Focus:**")
        chk_cols = st.columns(4)
        done_mod = chk_cols[0].checkbox("Module")
        done_pyq = chk_cols[1].checkbox("PYQ")
        done_rev = chk_cols[2].checkbox("RevBook")
        done_notes = chk_cols[3].checkbox("Notes")
        
        focus = []
        if done_mod: focus.append("Module")
        if done_pyq: focus.append("PYQ")
        if done_rev: focus.append("RevBook")
        if done_notes: focus.append("Notes")
        
        if st.button("✅ Log Session", type="primary"):
            if not topic_input:
                st.error("Topic name required!")
            else:
                new_entry = pd.DataFrame([{
                    "Date": str(date_input),
                    "Block": block_input,
                    "Subject": subject_input,
                    "Topic": topic_input,
                    "Hours": hours_input,
                    "Focus_Area": ", ".join(focus)
                }])
                updated_logs = pd.concat([df_logs, new_entry], ignore_index=True)
                update_data(updated_logs, "Logs") # Save to Google Sheet
                
                # Revision Logic
                if "Revision" in block_input or st.checkbox("Add to Spaced Cycle?", value=True):
                    next_date = date_input + timedelta(days=1)
                    new_rev_entry = pd.DataFrame([{
                        "Topic": topic_input,
                        "Last_Studied": str(date_input),
                        "Next_Review": str(next_date),
                        "Iteration": 1
                    }])
                    updated_rev = pd.concat([df_rev, new_rev_entry], ignore_index=True)
                    update_data(updated_rev, "Revision") # Save to Google Sheet
                
                st.success("Saved to Cloud Database!")
                st.rerun()

# --- TAB 2: ANALYTICS ---
with tab2:
    if not df_logs.empty:
        today_data = df_logs[df_logs['Date'] == datetime.now().date()]
        st.metric("Hours Today", f"{today_data['Hours'].sum()} hrs")
        
        # Simple Pie Chart
        st.subheader("Subject Split")
        fig, ax = plt.subplots()
        df_logs.groupby("Subject")["Hours"].sum().plot.pie(autopct='%1.1f%%', ax=ax)
        st.pyplot(fig)

# --- TAB 3: SPACED REVISION ---
with tab3:
    st.header("Due for Revision")
    if not df_rev.empty:
        # Convert date strings to objects for comparison
        df_rev['Next_Review'] = pd.to_datetime(df_rev['Next_Review']).dt.date
        today = datetime.now().date()
        
        due = df_rev[df_rev['Next_Review'] <= today]
        
        if due.empty:
            st.success("No revisions due!")
        else:
            for i, row in due.iterrows():
                if st.button(f"Mark Revised: {row['Topic']}", key=f"rev_{i}"):
                    # Logic: Update date by 2^n
                    new_iter = int(row['Iteration']) + 1
                    days_add = 2 ** int(row['Iteration'])
                    new_date = today + timedelta(days=days_add)
                    
                    df_rev.at[i, 'Last_Studied'] = str(today)
                    df_rev.at[i, 'Next_Review'] = str(new_date)
                    df_rev.at[i, 'Iteration'] = new_iter
                    
                    # Clean up dates for saving (convert back to string)
                    save_df = df_rev.copy()
                    save_df['Next_Review'] = save_df['Next_Review'].astype(str)
                    
                    update_data(save_df, "Revision")
                    st.rerun()

# --- TAB 4: STRATEGY ---
with tab4:
    st.markdown("### Your Plan\n* **Block 1:** Maths\n* **Block 2:** Revision\n* **Block 3:** Phys/Chem\n* **Block 4:** Inorganic")