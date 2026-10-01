from datetime import datetime
import io
import os
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Student Presentation Booking", page_icon="📅", layout="centered"
)

# --- HIDE STREAMLIT HEADER & GITHUB ICONS ---
hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    div[data-testid="stToolbar"] {display: none !important;}
    div[data-testid="stDecoration"] {display: none !important;}
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

CSV_FILE = "bookings_cleaned.csv"


# Function to initialize or load registered students from the clean CSV
def load_registered_students():
  registered_student_numbers = set()
  bookings_dict = {}

  if os.path.exists(CSV_FILE):
    try:
      df = pd.read_csv(CSV_FILE)
      for _, row in df.iterrows():
        day = row.get("Day", "")
        time_slot = row.get("Time Slot", "")
        leader = row.get("Group Leader", "")
        name = row.get("Student Name", "")
        num = row.get("Student Number", "")

        if not time_slot or pd.isna(name) or str(name).strip() == "":
          continue

        full_slot = f"{day}: {time_slot}" if day else time_slot

        if full_slot not in bookings_dict:
          bookings_dict[full_slot] = {
              "leader_name": leader,
              "members": [],
          }

        if str(name).strip() != str(leader).strip():
          bookings_dict[full_slot]["members"].append(
              {"name": str(name).strip(), "number": str(num).strip()}
          )

        if pd.notna(num) and str(num).strip() and str(num).lower() != "nan":
          registered_student_numbers.add(str(num).strip())
    except Exception:
      pass

  return bookings_dict, registered_student_numbers


# Initialize session state from CSV file
if "bookings" not in st.session_state:
  st.session_state.bookings, st.session_state.registered_students = (
      load_registered_students()
  )

# Define available slots based on the timetable
THURSDAY_SLOTS = [
    # Morning Block (09:00 - 11:00)
    "Thursday: 09:00 - 09:15",
    "Thursday: 09:15 - 09:30",
    "Thursday: 09:30 - 09:45",
    "Thursday: 09:45 - 10:00",
    "Thursday: 10:00 - 10:15",
    "Thursday: 10:15 - 10:30",
    "Thursday: 10:30 - 10:45",
    "Thursday: 10:45 - 11:00",
    # Midday Block (12:00 - 13:00)
    "Thursday: 12:00 - 12:15",
    "Thursday: 12:15 - 12:30",
    "Thursday: 12:30 - 12:45",
    "Thursday: 12:45 - 13:00",
    # Afternoon Block (14:00 - 16:00)
    "Thursday: 14:00 - 14:15",
    "Thursday: 14:15 - 14:30",
    "Thursday: 14:30 - 14:45",
    "Thursday: 14:45 - 15:00",
    "Thursday: 15:00 - 15:15",
    "Thursday: 15:15 - 15:30",
    "Thursday: 15:30 - 15:45",
    "Thursday: 15:45 - 16:00",
]

FRIDAY_SLOTS = [
    # Afternoon Block (14:00 - 16:00)
    "Friday: 14:00 - 14:15",
    "Friday: 14:15 - 14:30",
    "Friday: 14:30 - 14:45",
    "Friday: 14:45 - 15:00",
    "Friday: 15:00 - 15:15",
    "Friday: 15:15 - 15:30",
    "Friday: 15:30 - 15:45",
    "Friday: 15:45 - 16:00",
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
      # 1. Download Cleaned CSV Button
      with open(CSV_FILE, "rb") as f:
        st.sidebar.download_button(
            label="📥 Download Cleaned CSV",
            data=f,
            file_name="flattened_presentation_bookings.csv",
            mime="text/csv",
        )

      # 2. Download Cleaned Excel (.xlsx) Button
      try:
        df_clean = pd.read_csv(CSV_FILE)
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
          df_clean.to_excel(writer, index=False, sheet_name="Bookings")
        excel_data = output.getvalue()

        st.sidebar.download_button(
            label="📊 Download Cleaned Excel (.xlsx)",
            data=excel_data,
            file_name="flattened_presentation_bookings_chronological.xlsx",
            mime=(
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            ),
        )
      except Exception as e:
        st.sidebar.error(f"Error generating Excel file: {e}")
    else:
      st.sidebar.info("No bookings recorded yet.")
  else:
    st.sidebar.error("Incorrect password.")

# --- MAIN APP INTERFACE ---
st.title("🎓 Presentation Booking")
st.markdown(
    "Select an available 15-minute time slot. Only the **Group Leader's name**"
    " will appear publicly on the schedule."
)

with st.form("booking_form"):
  st.subheader("Group Leader Details")
  col_l1, col_l2 = st.columns(2)
  with col_l1:
    leader_name = st.text_input(
        "Group Leader Full Name", placeholder="e.g., Ravele Thendo"
    )
  with col_l2:
    leader_num = st.text_input("Group Leader Student Number", placeholder="")

  st.subheader("Group Members Details")

  col_m1_1, col_m1_2 = st.columns(2)
  with col_m1_1:
    m1_name = st.text_input("Member 1 Name")
  with col_m1_2:
    m1_num = st.text_input("Member 1 Student Number")

  col_m2_1, col_m2_2 = st.columns(2)
  with col_m2_1:
    m2_name = st.text_input("Member 2 Name")
  with col_m2_2:
    m2_num = st.text_input("Member 2 Student Number")

  col_m3_1, col_m3_2 = st.columns(2)
  with col_m3_1:
    m3_name = st.text_input("Member 3 Name")
  with col_m3_2:
    m3_num = st.text_input("Member 3 Student Number")

  # Filter out already booked slots
  available_slots = [
      slot for slot in ALL_SLOTS if slot not in st.session_state.bookings
  ]
  selected_slot = st.selectbox(
      "Choose an Available Time Slot",
      available_slots if available_slots else ["No slots available!"],
  )

  submit_button = st.form_submit_button("Confirm Booking")

  if submit_button:
    l_name = leader_name.strip()
    l_num = leader_num.strip()

    current_members = []
    for name_val, num_val in [
        (m1_name, m1_num),
        (m2_name, m2_num),
        (m3_name, m3_num),
    ]:
      if name_val.strip() or num_val.strip():
        current_members.append(
            {"name": name_val.strip(), "number": num_val.strip()}
        )

    all_student_nums = [l_num] + [
        m["number"] for m in current_members if m["number"]
    ]

    duplicate_found = False
    duplicate_num = ""
    for num in all_student_nums:
      if num and num in st.session_state.registered_students:
        duplicate_found = True
        duplicate_num = num
        break

    if not l_name or not l_num:
      st.error(
          "Please provide the Group Leader's name and student number."
      )
    elif duplicate_found:
      st.error(
          f"Duplicate booking error: Student number '{duplicate_num}' is"
          " already registered in another booking. Each student can only be"
          " registered once!"
      )
    elif not available_slots:
      st.error("All slots have been booked!")
    else:
      st.session_state.bookings[selected_slot] = {
          "leader_name": l_name,
          "members": current_members,
      }

      for num in all_student_nums:
        if num:
          st.session_state.registered_students.add(num)

      # Build new rows for the flattened format
      parts = selected_slot.split(": ")
      day = parts[0].strip()
      time_part = ": ".join(parts[1:]).strip()

      new_rows = [{
          "Day": day,
          "Time Slot": time_part,
          "Group Leader": l_name,
          "Student Name": l_name,
          "Student Number": l_num,
      }]

      for m in current_members:
        new_rows.append({
            "Day": day,
            "Time Slot": time_part,
            "Group Leader": l_name,
            "Student Name": m["name"],
            "Student Number": m["number"],
        })

      new_df = pd.DataFrame(new_rows)

      if os.path.exists(CSV_FILE):
        try:
          existing_df = pd.read_csv(CSV_FILE)
          combined_df = pd.concat([existing_df, new_df], ignore_index=True)
        except Exception:
          combined_df = new_df
      else:
        combined_df = new_df

      # Sort chronologically by day and start time
      day_order = {"Thursday": 1, "Friday": 2}
      combined_df["Day_Order"] = combined_df["Day"].map(day_order).fillna(3)
      combined_df["Start_Time"] = combined_df["Time Slot"].apply(
          lambda x: x.split(" - ")[0] if " - " in str(x) else str(x)
      )
      combined_df = (
          combined_df.sort_values(by=["Day_Order", "Start_Time"])
          .drop(columns=["Day_Order", "Start_Time"])
          .reset_index(drop=True)
      )

      combined_df.to_csv(CSV_FILE, index=False)

      st.success(
          f"Success! Booked for {selected_slot} under group leader {l_name}."
      )
      st.rerun()

st.markdown("---")
st.subheader("📋 Current Booking Schedule")

if st.session_state.bookings:
  booking_data = []
  for slot, info in sorted(st.session_state.bookings.items()):
    booking_data.append(
        {"Time Slot": slot, "Group Leader": info.get("leader_name", "")}
    )
  st.table(booking_data)
else:
  st.info("No bookings made yet. Be the first to pick a slot!")

# --- FOOTER ---
st.markdown("---")
st.markdown(
    "<div style='text-align: center; font-family: monospace; color:"
    " #888888; font-size: 0.85rem; letter-spacing: 1px;'>Crafted by Thendo"
    " Ravele</div>",
    unsafe_allow_html=True,
)
