import streamlit as st

st.set_page_config(page_title="Student Presentation Booking", page_icon="📅", layout="centered")

# Initialize session state to keep track of bookings
if "bookings" not in st.session_state:
    st.session_state.bookings = {}  # Format: { "Day - Slot": "Group Name" }

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

st.title("🎓 Student Presentation Booking System")
st.markdown("Select an available 15-minute time slot for your group presentation. Slots are updated in real-time.")

with st.form("booking_form"):
    st.subheader("Book Your Slot")
    group_name = st.text_input("Group Name / Student Names", placeholder="e.g., Group 4 (Alice, Bob)")
    
    # Filter out already booked slots
    available_slots = [slot for slot in ALL_SLOTS if slot not in st.session_state.bookings]
    
    selected_slot = st.selectbox("Choose an Available Time Slot", available_slots if available_slots else ["No slots available!"])
    
    submit_button = st.form_submit_button("Confirm Booking")
    
    if submit_button:
        if not group_name.strip():
            st.error("Please enter your group name or student names.")
        elif not available_slots:
            st.error("All slots have been booked!")
        else:
            st.session_state.bookings[selected_slot] = group_name.strip()
            st.success(f"Success! {group_name.strip()} is booked for {selected_slot}.")
            st.rerun()

st.markdown("---")
st.subheader("📋 Current Booking Schedule")

if st.session_state.bookings:
    # Format bookings for display
    booking_data = [{"Time Slot": slot, "Booked By Group": group} for slot, group in sorted(st.session_state.bookings.items())]
    st.table(booking_data)
else:
    st.info("No bookings made yet. Be the first to pick a slot!")

# --- 5. FOOTER ---
st.markdown("---")
st.markdown(
    "<div style='text-align: center; font-family: monospace; color: #888888; font-size: 0.85rem; letter-spacing: 1px;'>Crafted by Thendo Ravele</div>",
    unsafe_allow_html=True,
)
