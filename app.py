import streamlit as st
import pandas as pd
from datetime import date
from streamlit_gsheets import GSheetsConnection

# ---------------------------------------------------------
# Page Configuration
# ---------------------------------------------------------
st.set_page_config(page_title="Sindh Govt School Portal", layout="wide", page_icon="🏫")

# ---------------------------------------------------------
# Connect to Google Sheets
# ---------------------------------------------------------
conn = st.connection("gsheets", type=GSheetsConnection)


def safe_read(worksheet, ttl=5):
    """Read a worksheet, but never crash the whole app if the sheet
    isn't reachable (bad share settings, wrong sheet id, network, etc)."""
    try:
        return conn.read(worksheet=worksheet, ttl=ttl)
    except Exception as e:
        st.error(
            f"Couldn't load the **{worksheet}** sheet. "
            f"Double-check sharing settings / worksheet name.\n\nDetails: {e}"
        )
        st.stop()


def safe_update(worksheet, data):
    try:
        conn.update(worksheet=worksheet, data=data)
        st.cache_data.clear()
        return True
    except Exception as e:
        st.error(f"Couldn't save to **{worksheet}**.\n\nDetails: {e}")
        return False


# ---------------------------------------------------------
# AUTHENTICATION
# ---------------------------------------------------------
def check_login(username, password):
    users_df = safe_read("Users")
    # Normalize so stray spaces / case differences don't break login
    users_df.columns = [c.strip() for c in users_df.columns]
    match = users_df[
        (users_df["Username"].astype(str).str.strip() == username.strip())
        & (users_df["Password"].astype(str) == password)
    ]
    if not match.empty:
        return match.iloc[0]["Role"], match.iloc[0]["Full_Name"]
    return None, None


if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    st.title("🏫 Sindh Govt Primary School Portal")
    st.subheader("Please Login")

    with st.form("login_form"):
        user_input = st.text_input("Username")
        pass_input = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")

        if submit:
            if not user_input or not pass_input:
                st.error("Please enter both username and password.")
            else:
                role, name = check_login(user_input, pass_input)
                if role:
                    st.session_state["logged_in"] = True
                    st.session_state["role"] = role
                    st.session_state["name"] = name
                    st.rerun()
                else:
                    st.error("Invalid Username or Password")

# ---------------------------------------------------------
# LOGGED-IN AREA
# ---------------------------------------------------------
else:
    st.sidebar.title(f"Welcome, {st.session_state['name']}")
    st.sidebar.write(f"Role: {st.session_state['role']}")

    menu = ["Dashboard", "Digital GR", "Teacher Leave", "Circulars", "Daily Reporting"]
    choice = st.sidebar.selectbox("Menu", menu)

    if st.sidebar.button("Logout"):
        st.session_state["logged_in"] = False
        st.rerun()

    # ---------------- DASHBOARD ----------------
    if choice == "Dashboard":
        st.title("School Overview")
        st.write(f"Welcome to the management portal. You are logged in as **{st.session_state['role']}**.")

        col1, col2, col3 = st.columns(3)
        try:
            gr_df = safe_read("Student_GR")
            col1.metric("Total Students", len(gr_df))
        except Exception:
            col1.metric("Total Students", "N/A")

        try:
            leave_df = safe_read("Teacher_Leave")
            pending_count = (leave_df["Status"] == "Pending").sum()
            col2.metric("Pending Leave Requests", int(pending_count))
        except Exception:
            col2.metric("Pending Leave Requests", "N/A")

        try:
            circ_df = safe_read("Circulars")
            col3.metric("Circulars Issued", len(circ_df))
        except Exception:
            col3.metric("Circulars Issued", "N/A")

    # ---------------- DIGITAL GR ----------------
    elif choice == "Digital GR":
        st.title("📖 Digital General Register (GR)")
        gr_df = safe_read("Student_GR")

        search = st.text_input("Search Student by Name or GR No")
        if search:
            name_match = gr_df["Student_Name"].astype(str).str.contains(search, case=False, na=False)
            gr_match = gr_df["GR_No"].astype(str).str.contains(search, case=False, na=False)
            filtered_df = gr_df[name_match | gr_match]
            st.dataframe(filtered_df, use_container_width=True)
        else:
            st.dataframe(gr_df, use_container_width=True)

        if st.session_state["role"] == "Principal":
            st.subheader("Add New Student")
            with st.form("add_student", clear_on_submit=True):
                gr_no = st.text_input("GR Number")
                s_name = st.text_input("Student Name")
                f_name = st.text_input("Father Name")
                s_class = st.selectbox("Class", ["Nursery", "Prep", "1", "2", "3", "4", "5"])
                dob = st.date_input("Date of Birth")
                if st.form_submit_button("Save to GR"):
                    if not gr_no or not s_name:
                        st.error("GR Number and Student Name are required.")
                    else:
                        new_row = pd.DataFrame([{
                            "GR_No": gr_no,
                            "Student_Name": s_name,
                            "Father_Name": f_name,
                            "Class": s_class,
                            "DOB": dob.strftime("%Y-%m-%d"),
                        }])
                        updated = pd.concat([gr_df, new_row], ignore_index=True)
                        if safe_update("Student_GR", updated):
                            st.success(f"{s_name} added to the register.")
                            st.rerun()

    # ---------------- TEACHER LEAVE ----------------
    elif choice == "Teacher Leave":
        st.title("📅 Leave Management")

        if st.session_state["role"] == "Teacher":
            st.subheader("Apply for Leave")
            with st.form("leave_form", clear_on_submit=True):
                l_type = st.selectbox("Leave Type", ["Casual Leave", "Sick Leave", "Earned Leave"])
                start = st.date_input("Start Date")
                end = st.date_input("End Date")
                reason = st.text_area("Reason")
                if st.form_submit_button("Submit Request"):
                    if end < start:
                        st.error("End date can't be before start date.")
                    else:
                        leave_df = safe_read("Teacher_Leave")
                        new_row = pd.DataFrame([{
                            "Teacher_Name": st.session_state["name"],
                            "Leave_Type": l_type,
                            "Start_Date": start.strftime("%Y-%m-%d"),
                            "End_Date": end.strftime("%Y-%m-%d"),
                            "Reason": reason,
                            "Status": "Pending",
                        }])
                        updated = pd.concat([leave_df, new_row], ignore_index=True)
                        if safe_update("Teacher_Leave", updated):
                            st.success("Application submitted to Principal")

            st.subheader("My Leave History")
            leave_df = safe_read("Teacher_Leave")
            mine = leave_df[leave_df["Teacher_Name"] == st.session_state["name"]]
            st.dataframe(mine, use_container_width=True)

        elif st.session_state["role"] == "Principal":
            st.subheader("Pending Leave Requests")
            leave_df = safe_read("Teacher_Leave")
            pending = leave_df[leave_df["Status"] == "Pending"]

            if pending.empty:
                st.info("No pending requests.")
            else:
                for idx, row in pending.iterrows():
                    with st.expander(f"{row['Teacher_Name']} — {row['Leave_Type']} ({row['Start_Date']} to {row['End_Date']})"):
                        st.write(f"**Reason:** {row['Reason']}")
                        c1, c2 = st.columns(2)
                        if c1.button("✅ Approve", key=f"approve_{idx}"):
                            leave_df.loc[idx, "Status"] = "Approved"
                            if safe_update("Teacher_Leave", leave_df):
                                st.success("Approved.")
                                st.rerun()
                        if c2.button("❌ Reject", key=f"reject_{idx}"):
                            leave_df.loc[idx, "Status"] = "Rejected"
                            if safe_update("Teacher_Leave", leave_df):
                                st.warning("Rejected.")
                                st.rerun()

    # ---------------- CIRCULARS ----------------
    elif choice == "Circulars":
        st.title("📢 Official Circulars")
        circ_df = safe_read("Circulars")

        if st.session_state["role"] == "Principal":
            with st.expander("➕ Post a new circular"):
                with st.form("new_circular", clear_on_submit=True):
                    subj = st.text_input("Subject")
                    content = st.text_area("Content")
                    link = st.text_input("File Link (optional PDF/Image URL)")
                    if st.form_submit_button("Post Circular"):
                        if not subj:
                            st.error("Subject is required.")
                        else:
                            new_row = pd.DataFrame([{
                                "Date": date.today().strftime("%Y-%m-%d"),
                                "Subject": subj,
                                "Content": content,
                                "File_Link": link,
                            }])
                            updated = pd.concat([circ_df, new_row], ignore_index=True)
                            if safe_update("Circulars", updated):
                                st.success("Circular posted.")
                                st.rerun()

        for index, row in circ_df.sort_index(ascending=False).iterrows():
            with st.expander(f"{row['Date']} - {row['Subject']}"):
                st.write(row["Content"])
                if row.get("File_Link"):
                    st.write(f"[View PDF/Image]({row['File_Link']})")

    # ---------------- DAILY REPORTING ----------------
    elif choice == "Daily Reporting":
        st.title("📊 Daily School Report")
        with st.form("daily_report", clear_on_submit=True):
            cls = st.selectbox("Class", ["Nursery", "Prep", "1", "2", "3", "4", "5"])
            pres = st.number_input("Students Present", min_value=0, step=1)
            absent = st.number_input("Students Absent", min_value=0, step=1)
            mdm = st.checkbox("Mid-Day Meal Served?")
            if st.form_submit_button("Submit Daily Log"):
                try:
                    report_df = safe_read("Daily_Reports")
                except Exception:
                    report_df = pd.DataFrame(columns=["Date", "Class", "Present", "Absent", "MDM_Served", "Submitted_By"])

                new_row = pd.DataFrame([{
                    "Date": date.today().strftime("%Y-%m-%d"),
                    "Class": cls,
                    "Present": pres,
                    "Absent": absent,
                    "MDM_Served": "Yes" if mdm else "No",
                    "Submitted_By": st.session_state["name"],
                }])
                updated = pd.concat([report_df, new_row], ignore_index=True)
                if safe_update("Daily_Reports", updated):
                    st.success("Report saved successfully")
