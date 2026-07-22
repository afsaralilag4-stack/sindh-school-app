import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# Page Configuration
st.set_page_config(page_title="Sindh Govt School Portal", layout="wide")

# Connect to Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# --- AUTHENTICATION SYSTEM ---
def check_login(username, password):
    users_df = conn.read(worksheet="Users")
    user = users_df[(users_df['Username'] == username) & (users_df['Password'] == password)]
    if not user.empty:
        return user.iloc[0]['Role'], user.iloc[0]['Full_Name']
    return None, None

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if not st.session_state['logged_in']:
    st.title("🏫 Sindh Govt Primary School Portal")
    st.subheader("Please Login")
    
    with st.form("login_form"):
        user_input = st.text_input("Username")
        pass_input = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")
        
        if submit:
            role, name = check_login(user_input, pass_input)
            if role:
                st.session_state['logged_in'] = True
                st.session_state['role'] = role
                st.session_state['name'] = name
                st.rerun()
            else:
                st.error("Invalid Username or Password")
else:
    # --- LOGGED IN AREA ---
    st.sidebar.title(f"Welcome, {st.session_state['name']}")
    st.sidebar.write(f"Role: {st.session_state['role']}")
    
    menu = ["Dashboard", "Digital GR", "Teacher Leave", "Circulars", "Daily Reporting"]
    choice = st.sidebar.selectbox("Menu", menu)
    
    if st.sidebar.button("Logout"):
        st.session_state['logged_in'] = False
        st.rerun()

    # --- DASHBOARD ---
    if choice == "Dashboard":
        st.title("School Overview")
        st.write(f"Welcome to the management portal. You are logged in as **{st.session_state['role']}**.")
        # Here we would add summary cards (Total Students, Teachers on Leave today)

    # --- DIGITAL GR ---
    elif choice == "Digital GR":
        st.title("📖 Digital General Register (GR)")
        gr_df = conn.read(worksheet="Student_GR")
        
        # Search Feature
        search = st.text_input("Search Student by Name or GR No")
        if search:
            filtered_df = gr_df[gr_df['Student_Name'].str.contains(search, case=False) | gr_df['GR_No'].astype(str).contains(search)]
            st.dataframe(filtered_df)
        else:
            st.dataframe(gr_df)
        
        if st.session_state['role'] == "Principal":
            st.subheader("Add New Student")
            with st.form("add_student"):
                # Add input fields for GR, Name, Father Name, etc.
                st.form_submit_button("Save to GR")

    # --- TEACHER LEAVE ---
    elif choice == "Teacher Leave":
        st.title("📅 Leave Management")
        if st.session_state['role'] == "Teacher":
            st.subheader("Apply for Leave")
            with st.form("leave_form"):
                l_type = st.selectbox("Leave Type", ["Casual Leave", "Sick Leave", "Earned Leave"])
                start = st.date_input("Start Date")
                end = st.date_input("End Date")
                reason = st.text_area("Reason")
                if st.form_submit_button("Submit Request"):
                    st.success("Application submitted to Principal")
        
        elif st.session_state['role'] == "Principal":
            st.subheader("Pending Leave Requests")
            leave_df = conn.read(worksheet="Teacher_Leave")
            pending = leave_df[leave_df['Status'] == "Pending"]
            st.table(pending)
            # Add Approval/Rejection buttons here

    # --- CIRCULARS ---
    elif choice == "Circulars":
        st.title("📢 Official Circulars")
        circ_df = conn.read(worksheet="Circulars")
        for index, row in circ_df.iterrows():
            with st.expander(f"{row['Date']} - {row['Subject']}"):
                st.write(row['Content'])
                st.write(f"[View PDF/Image]({row['File_Link']})")

    # --- DAILY REPORTING ---
    elif choice == "Daily Reporting":
        st.title("📊 Daily School Report")
        with st.form("daily_report"):
            cls = st.selectbox("Class", ["Nursery", "Prep", "1", "2", "3", "4", "5"])
            pres = st.number_input("Students Present", min_value=0)
            absent = st.number_input("Students Absent", min_value=0)
            mdm = st.checkbox("Mid-Day Meal Served?")
            if st.form_submit_button("Submit Daily Log"):
                st.success("Report saved successfully")
