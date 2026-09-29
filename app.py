import streamlit as st
import pandas as pd
import os
from datetime import datetime

st.set_page_config(page_title="Student Presentation Booking", page_icon="📅", layout="centered")

CSV_FILE = "bookings.csv"

# Function to initialize or load bookings from CSV
def load_bookings():
    if os.path.exists(CSV_FILE):
        try:
            df = pd.read_csv(CSV_FILE)
            # Convert dataframe to dictionary format: { "Slot": {"leader": ..., "members": ...} }
            bookings_dict = {}
            for _, row in df.iterrows():
                bookings_dict[row["Time Slot"]] = {
                    "leader": row["Group Leader"],
                    "members": row["Members & Student Numbers"]
                }
            return bookings_dict
        except Exception:
            return {}
    return {}

# Initialize session state bookings from CSV file
if "bookings" not in st.session_state:
    st.session_state.bookings = load_bookings()

# Define available slots based on the timetable
THURSDAY_SLOTS = [
    # Morning Block (09:00 - 11:00)
    "Thursday: 09:00 - 09:15", "Thursday: 09:15 - 09:30", "Thursday: 09:30 - 09:45", "Thursday: 09:45 - 10:00",
    "Thursday: 10:00 - 10:15", "Thursday: 10:15 - 10:30", "Thursday: 10:30 - 10:45", "Thursday: 10:45 - 11:00",
    # Midday Block (12:00 - 13:00)
    "Thursday: 12:00 - 12:15", "Thursday: 12:15 - 12:30", "Thursday: 12:30 - 12:45", "Thursday: 12:45 - 13:00",
    # Afternoon Block (14:00 - 16:00)
    "Thursday: 14:00 - 14:15", "Thursday: 14:15 - 14:30", "Thursday: 14:30 - 14:45", "Thursday: 14:45 - 15:00",
    "Thursday: 15:00 - 15:15", "Thursday: 15:15 - 15:30", "Thursday: 15:30 - 15:45", "Thursday: 15:45 - 16:00"
]

FRIDAY_SLOTS = [
    # Afternoon Block (14:00 - 16:00)
    "Friday: 14:00 - 14:15", "Friday: 14:15 - 14:30", "Friday: 14:30 - 14:45", "Friday: 14:45 - 15:00",
    "Friday: 15:00 - 15:15", "Friday: 15:15 - 15:30", "Friday: 15:30 - 15:45", "Friday: 15:45 - 16:00"
]

ALL_SLOTS = THURSDAY_SLOTS + FRIDAY_SLOTS

# --- SIDEBAR: ADMIN DOWNLOAD PANEL ---
st.sidebar.subheader("🔒 Admin Panel")
admin_password_input = st.sidebar.text_input("Admin Password", type="password")

# Retrieve admin password safely from st.secrets
admin_password_secret = st.secrets.get("admin_password", "changeme123")

if admin_password_input:
    if admin_password_input == admin_password_secret:
        st.sidebar.success("Access Granted")
        if os.path.exists(CSV_FILE):
            with open(CSV_FILE, "rb") as f:
                st.sidebar.download_button(
                    label="📥 Download Bookings CSV",
                    data=f,
                    file_name="presentation_bookings.csv",
                    mime="text/csv"
                )
        else:
            st.sidebar.info("No bookings recorded yet.")
    else:
        st.sidebar.error("Incorrect password.")

# --- MAIN APP INTERFACE ---
st.title("🎓 Student Presentation Booking System")
st.markdown("Select an available 15-minute time slot for your group presentation. Only the **Group Leader's name** will appear publicly on the schedule.")

with st.form("booking_form"):
    st.subheader("Book Your Slot")
    group_leader = st.text_input("Group Leader Name", placeholder="e.g., Alice Smith")
    members_info = st.text_area("Group Members & Student Numbers", placeholder="e.g.\n1. Alice Smith - 21900123\n2. Bob Jones - 21900456")
    
    # Filter out already booked slots
    available_slots = [slot for slot in ALL_SLOTS if slot not in st.session_state.bookings]
    
    selected_slot = st.selectbox("Choose an Available Time Slot", available_slots if available_slots else ["No slots available!"])
    
    submit_button = st.form_submit_button("Confirm Booking")
    
    if submit_button:
        if not group_leader.strip():
            st.error("Please enter the Group Leader's name.")
        elif not members_info.strip():
            st.error("Please enter group member names and student numbers.")
        elif not available_slots:
            st.error("All slots have been booked!")
        else:
            # Save to session state
            st.session_state.bookings[selected_slot] = {
                "leader": group_leader.strip(),
                "members": members_info.strip()
            }
            
            # Save/Append to CSV file in repo directory
            file_exists = os.path.exists(CSV_FILE)
            new_data = pd.DataFrame([{
                "Time Slot": selected_slot,
                "Group Leader": group_leader.strip(),
                "Members & Student Numbers": members_info.strip(),
                "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }])
            
            if file_exists:
                new_data.to_csv(CSV_FILE, mode='a', header=False, index=False)
            else:
                new_data.to_csv(CSV_FILE, mode='w', header=True, index=False)
                
            st.success(f"Success! Booked for {selected_slot} under group leader {group_leader.strip()}.")
            st.rerun()

st.markdown("---")
st.subheader("📋 Current Booking Schedule")

if st.session_state.bookings:
    # Format public bookings for display (showing ONLY the group leader's name)
    booking_data = [{"Time Slot": slot, "Group Leader": info["leader"]} for slot, info in sorted(st.session_state.bookings.items())]
    st.table(booking_data)
else:
    st.info("No bookings made yet. Be the first to pick a slot!")

# --- FOOTER ---
st.markdown("---")
st.markdown(
    "<div style='text-align: center; font-family: monospace; color: #888888; font-size: 0.85rem; letter-spacing: 1px;'>Crafted by Thendo Ravele</div>",
    unsafe_allow_html=True,
)
