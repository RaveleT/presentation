import streamlit as st
import pandas as pd
import os
import io
from datetime import datetime

st.set_page_config(page_title="Student Presentation Booking", page_icon="📅", layout="centered")

CSV_FILE = "bookings.csv"

# Function to initialize or load bookings from CSV (ignoring blank rows)
def load_bookings_and_students():
    bookings_dict = {}
    registered_student_numbers = set()
    
    if os.path.exists(CSV_FILE):
        try:
            df = pd.read_csv(CSV_FILE)
            for _, row in df.iterrows():
                slot = row.get("Time Slot")
                leader_name = row.get("Leader Name", "")
                
                # Skip if slot or leader name is missing/empty/nan
                if not slot or pd.isna(leader_name) or str(leader_name).strip() == "" or str(leader_name).lower() == "nan":
                    continue
                
                leader_name = str(leader_name).strip()
                leader_num = str(row.get("Leader Student Number", ""))
                
                if leader_num and leader_num.lower() != "nan":
                    registered_student_numbers.add(leader_num.strip())
                
                members = []
                for i in range(1, 4):
                    m_name = row.get(f"Member {i} Name", "")
                    m_num = row.get(f"Member {i} Student Number", "")
                    if pd.notna(m_name) and str(m_name).strip() and str(m_name).lower() != "nan":
                        members.append({"name": str(m_name).strip(), "number": str(m_num).strip()})
                        if pd.notna(m_num) and str(m_num).lower() != "nan":
                            registered_student_numbers.add(str(m_num).strip())
                
                bookings_dict[slot] = {
                    "leader_name": leader_name,
                    "leader_num": leader_num,
                    "members": members
                }
        except Exception:
            pass
            
    return bookings_dict, registered_student_numbers

# Initialize session state from CSV file
if "bookings" not in st.session_state:
    st.session_state.bookings, st.session_state.registered_students = load_bookings_and_students()

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
admin_password_secret = st.secrets.get("admin_password", "changeme123")

if admin_password_input:
    if admin_password_input == admin_password_secret:
        st.sidebar.success("Access Granted")
        if os.path.exists(CSV_FILE):
            # 1. Download Detailed CSV Button
            with open(CSV_FILE, "rb") as f:
                st.sidebar.download_button(
                    label="📥 Download Detailed CSV",
                    data=f,
                    file_name="presentation_bookings_detailed.csv",
                    mime="text/csv"
                )
            
            # 2. Download Cleaned Excel (.xlsx) Button
            try:
                df_raw = pd.read_csv(CSV_FILE)
                clean_rows = []
                for _, row in df_raw.iterrows():
                    slot = row.get("Time Slot")
                    l_name = row.get("Leader Name", "")
                    l_num = row.get("Leader Student Number", "")
                    
                    if not slot or pd.isna(l_name) or str(l_name).strip() == "" or str(l_name).lower() == "nan":
                        continue
                    
                    names_list = [str(l_name).strip()]
                    nums_list = [str(l_num).strip()] if pd.notna(l_num) and str(l_num).lower() != "nan" else [""]
                    
                    for i in range(1, 4):
                        m_name = row.get(f"Member {i} Name", "")
                        m_num = row.get(f"Member {i} Student Number", "")
                        if pd.notna(m_name) and str(m_name).strip() and str(m_name).lower() != "nan":
                            names_list.append(str(m_name).strip())
                        if pd.notna(m_num) and str(m_num).strip() and str(m_num).lower() != "nan":
                            nums_list.append(str(m_num).strip())
                            
                    clean_rows.append({
                        "Time Slot": slot,
                        "Group Leader": str(l_name).strip(),
                        "Members": ", ".join(names_list),
                        "Student Numbers": ", ".join(nums_list)
                    })
                
                df_clean = pd.DataFrame(clean_rows)
                
                # Write to Excel in memory using openpyxl
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df_clean.to_excel(writer, index=False, sheet_name="Bookings")
                excel_data = output.getvalue()
                
                st.sidebar.download_button(
                    label="📊 Download Cleaned Excel (.xlsx)",
                    data=excel_data,
                    file_name="cleaned_presentation_bookings.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            except Exception as e:
                st.sidebar.error(f"Error generating Excel file: {e}")
        else:
            st.sidebar.info("No bookings recorded yet.")
    else:
        st.sidebar.error("Incorrect password.")

# --- MAIN APP INTERFACE ---
st.title("🎓 Presentation Booking")
st.markdown("Select an available 15-minute time slot. Only the **Group Leader's name** will appear publicly on the schedule.")

with st.form("booking_form"):
    st.subheader("Group Leader Details")
    leader_name = st.text_input("Group Leader Full Name", placeholder="e.g., Ravele Thendo")
    leader_num = st.text_input("Group Leader Student Number", placeholder=" ")
    
    st.subheader("Group Members Details")
    col1, col2 = st.columns(2)
    with col1:
        m1_name = st.text_input("Member 1 Name")
        m2_name = st.text_input("Member 2 Name")
        m3_name = st.text_input("Member 3 Name")
    with col2:
        m1_num = st.text_input("Member 1 Student Number")
        m2_num = st.text_input("Member 2 Student Number")
        m3_num = st.text_input("Member 3 Student Number")
    
    # Filter out already booked slots
    available_slots = [slot for slot in ALL_SLOTS if slot not in st.session_state.bookings]
    selected_slot = st.selectbox("Choose an Available Time Slot", available_slots if available_slots else ["No slots available!"])
    
    submit_button = st.form_submit_button("Confirm Booking")
    
    if submit_button:
        l_name = leader_name.strip()
        l_num = leader_num.strip()
        
        current_members = []
        for name_val, num_val in [(m1_name, m1_num), (m2_name, m2_num), (m3_name, m3_num)]:
            if name_val.strip() or num_val.strip():
                current_members.append({"name": name_val.strip(), "number": num_val.strip()})
        
        all_student_nums = [l_num] + [m["number"] for m in current_members if m["number"]]
        
        duplicate_found = False
        duplicate_num = ""
        for num in all_student_nums:
            if num and num in st.session_state.registered_students:
                duplicate_found = True
                duplicate_num = num
                break

        if not l_name or not l_num:
            st.error("Please provide the Group Leader's name and student number.")
        elif duplicate_found:
            st.error(f"Duplicate booking error: Student number '{duplicate_num}' is already registered in another booking. Each student can only be registered once!")
        elif not available_slots:
            st.error("All slots have been booked!")
        else:
            st.session_state.bookings[selected_slot] = {
                "leader_name": l_name,
                "leader_num": l_num,
                "members": current_members
            }
            
            for num in all_student_nums:
                if num:
                    st.session_state.registered_students.add(num)
            
            row_data = {
                "Time Slot": selected_slot,
                "Leader Name": l_name,
                "Leader Student Number": l_num,
                "Member 1 Name": current_members[0]["name"] if len(current_members) > 0 else "",
                "Member 1 Student Number": current_members[0]["number"] if len(current_members) > 0 else "",
                "Member 2 Name": current_members[1]["name"] if len(current_members) > 1 else "",
                "Member 2 Student Number": current_members[1]["number"] if len(current_members) > 1 else "",
                "Member 3 Name": current_members[2]["name"] if len(current_members) > 2 else "",
                "Member 3 Student Number": current_members[2]["number"] if len(current_members) > 2 else "",
                "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            new_df = pd.DataFrame([row_data])
            
            if os.path.exists(CSV_FILE):
                try:
                    existing_df = pd.read_csv(CSV_FILE)
                    if "Leader Student Number" not in existing_df.columns:
                        new_df.to_csv(CSV_FILE, mode='w', header=True, index=False)
                    else:
                        new_df.to_csv(CSV_FILE, mode='a', header=False, index=False)
                except Exception:
                    new_df.to_csv(CSV_FILE, mode='w', header=True, index=False)
            else:
                new_df.to_csv(CSV_FILE, mode='w', header=True, index=False)
                
            st.success(f"Success! Booked for {selected_slot} under group leader {l_name}.")
            st.rerun()

st.markdown("---")
st.subheader("📋 Current Booking Schedule")

if st.session_state.bookings:
    booking_data = []
    for slot, info in sorted(st.session_state.bookings.items()):
        booking_data.append({"Time Slot": slot, "Group Leader": info.get("leader_name", "")})
    st.table(booking_data)
else:
    st.info("No bookings made yet. Be the first to pick a slot!")

# --- FOOTER ---
st.markdown("---")
st.markdown(
    "<div style='text-align: center; font-family: monospace; color: #888888; font-size: 0.85rem; letter-spacing: 1px;'>Crafted by Thendo Ravele</div>",
    unsafe_allow_html=True,
)
