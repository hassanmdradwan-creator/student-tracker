import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os
import json
import shutil
from datetime import datetime
from tabulate import tabulate

# --- Configuration & Global Constants ---
DATA_FILE = 'student_analytics_db.csv'
CONFIG_FILE = 'univ_config.json'
REPORT_FILE = 'academic_merit_report.txt'
BACKUP_DIR = 'backups'
LOG_FILE = 'system_audit.log'

PASSING_ATTENDANCE = 75
PER_CREDIT_FEE = 3500
SCHOLARSHIP_THRESHOLD = 3.90  # GPA >= 3.90 qualifies for a waiver

# --- Streamlit Page Configuration ---
st.set_page_config(page_title="University Analytics ERP", layout="wide", page_icon="🎓")

class SmartStudentTrackerWeb:
    def __init__(self):
        self.data_file = DATA_FILE
        self.config_file = CONFIG_FILE
        self.df = pd.DataFrame()
        self.univ_name = "Stamford University Bangladesh"
        self.dept_name = "Computer Science & Engineering"
        
        self._ensure_directories()
        self._setup_system()
        self._load_config()

    def _ensure_directories(self):
        if not os.path.exists(BACKUP_DIR):
            os.makedirs(BACKUP_DIR)

    def _setup_system(self):
        required_cols = [
            'ID', 'Name', 'Email', 'Course_Code', 'Course_Name', 'Course_Type', 
            'Credits', 'Score', 'Attendance', 'GPA', 'Grade', 
            'Tuition_Fee', 'Scholarship_Amount', 'Net_Payable', 'Scholarship', 'Status', 'Timestamp'
        ]
        if not os.path.exists(self.data_file):
            df = pd.DataFrame(columns=required_cols)
            df.to_csv(self.data_file, index=False)
            self._log_event("SYSTEM", "New Database Initialized.")
        
        self._load_data()
        
        updated = False
        for col in required_cols:
            if col not in self.df.columns:
                self.df[col] = None
                updated = True
        if updated: 
            self._save_data()

    def _load_config(self):
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                config = json.load(f)
                self.univ_name = config.get('univ_name', self.univ_name)
                self.dept_name = config.get('dept_name', self.dept_name)

    def _save_config(self):
        with open(self.config_file, 'w') as f:
            json.dump({'univ_name': self.univ_name, 'dept_name': self.dept_name}, f)

    def _load_data(self):
        try:
            if os.path.exists(self.data_file):
                self.df = pd.read_csv(self.data_file)
                numeric_cols = ['Score', 'Attendance', 'Tuition_Fee', 'GPA', 'Credits', 'Net_Payable']
                for col in numeric_cols:
                    if col in self.df.columns:
                        self.df[col] = pd.to_numeric(self.df[col], errors='coerce').fillna(0)
        except Exception as e:
            self._log_event("ERROR", f"Load Data: {str(e)}")

    def _save_data(self):
        self.df.to_csv(self.data_file, index=False)
        if len(self.df) % 5 == 0 and len(self.df) > 0:
            self.create_backup()

    def _log_event(self, user, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(LOG_FILE, "a") as log:
            log.write(f"[{timestamp}] [{user}] {message}\n")

    def _calculate_grade(self, score):
        if score >= 80: return 'A+', 4.00
        elif score >= 75: return 'A', 3.75
        elif score >= 70: return 'A-', 3.50
        elif score >= 65: return 'B+', 3.25
        elif score >= 60: return 'B', 3.00
        elif score >= 55: return 'B-', 2.75
        elif score >= 50: return 'C+', 2.50
        elif score >= 45: return 'C', 2.25
        elif score >= 40: return 'D', 2.00
        else: return 'F', 0.00

    def create_backup(self):
        now = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(BACKUP_DIR, f"db_backup_{now}.csv")
        shutil.copy(self.data_file, backup_path)
        self._log_event("SYSTEM", f"Auto-backup created: {backup_path}")

# --- Initialize Tracker Core ---
tracker = SmartStudentTrackerWeb()

# --- Session State for Authentication ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'username' not in st.session_state:
    st.session_state['username'] = ""

# --- Login Interface ---
if not st.session_state['logged_in']:
    st.markdown("<h2 style='text-align: center;'>🔓 Management & Analytics ERP Login</h2>", unsafe_view=True)
    with st.form("login_form", clear_on_submit=True):
        st.write("Bypass System active. Enter any username & password to enter.")
        u = st.text_input("Username").strip()
        p = st.text_input("Password", type="password").strip()
        submit_login = st.form_submit_button("Access System")
        
        if submit_login:
            st.session_state['username'] = u if u else "Guest_Admin"
            st.session_state['logged_in'] = True
            tracker._log_event(st.session_state['username'], "User Logged in via Web Portal.")
            st.rerun()
    st.stop()

# --- Header Section ---
st.title(f"🎓 {tracker.univ_name.upper()}")
st.caption(f"🏛️ Department of {tracker.dept_name} | Active User: **{st.session_state['username']}**")
st.markdown("---")

# --- Web Navigation Sidebar ---
navigation_menu = [
    "📝 New Admission",
    "📋 Full Information Ledger",
    "🏆 Merit List & Ranking",
    "🔍 Search Student Profile",
    "💰 Financial & Revenue Report",
    "📊 Visual Analytics Dashboard",
    "📄 Official Grading Matrix",
    "📑 Export Text Report",
    "⚙️ System Configuration",
    "🗑️ Remove Student Record"
]

st.sidebar.title("🧭 Navigation")
choice = st.sidebar.radio("Go to:", navigation_menu)

if st.sidebar.button("🚪 Logout & Exit System"):
    st.session_state['logged_in'] = False
    st.session_state['username'] = ""
    st.rerun()

# --- Feature 1: Advanced Admission ---
if choice == "📝 New Admission":
    st.header("📝 Student Enrollment Portal")
    with st.form("enrollment_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            sid = st.text_input("Student ID (Unique)").strip()
            name = st.text_input("Full Name").strip()
            email = st.text_input("Institutional Email").strip()
            c_code = st.text_input("Course Code (e.g., CSE-411)").strip().upper()
            c_name = st.text_input("Course Title").strip()
        with col2:
            c_choice = st.selectbox("Course Type Selection", ["Theory (3.0 Credits)", "Sessional (1.5 Credits)", "Thesis (6.0 Credits)"])
            score = st.number_input("Marks Obtained (0-100)", min_value=0.0, max_value=100.0, step=1.0)
            attendance = st.number_input("Attendance Percentage (%)", min_value=0.0, max_value=100.0, step=1.0)
        
        submit_btn = st.form_submit_button("Enroll & Process Record")
        
        if submit_btn:
            if not sid or not name:
                st.error("❌ Student ID and Name cannot be empty.")
            elif sid in tracker.df['ID'].astype(str).values:
                st.error("⚠️ Duplicate Entry! Student ID already exists in the database.")
            else:
                c_map = {"Theory (3.0 Credits)": ("Theory", 3.0), "Sessional (1.5 Credits)": ("Sessional", 1.5), "Thesis (6.0 Credits)": ("Thesis", 6.0)}
                c_type, credits = c_map[c_choice]
                
                grade, gpa = tracker._calculate_grade(score)
                base_fee = credits * PER_CREDIT_FEE
                
                scholarship_amt = 0
                is_scholar = "No"
                if gpa >= SCHOLARSHIP_THRESHOLD:
                    scholarship_amt = base_fee * 0.25
                    is_scholar = f"Yes (25% Waiver via {grade})"
                
                net_payable = base_fee - scholarship_amt
                status = "Regular" if attendance >= PASSING_ATTENDANCE else "Shortage (Non-Collegiate)"
                
                new_entry = {
                    'ID': sid, 'Name': name, 'Email': email, 'Course_Code': c_code, 
                    'Course_Name': c_name, 'Course_Type': c_type, 'Credits': credits,
                    'Score': score, 'Attendance': attendance, 'GPA': gpa, 
                    'Grade': grade, 'Tuition_Fee': base_fee, 
                    'Scholarship_Amount': scholarship_amt, 'Net_Payable': net_payable,
                    'Scholarship': is_scholar, 'Status': status, 
                    'Timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                
                tracker.df = pd.concat([tracker.df, pd.DataFrame([new_entry])], ignore_index=True)
                tracker._save_data()
                st.success(f"✅ Record Saved Successfully! Calculated Grade: **{grade}** (GPA: **{gpa:.2f}**)")

# --- Feature 2: Full Information Ledger ---
elif choice == "📋 Full Information Ledger":
    st.header("📋 Central Student Information Ledger")
    if tracker.df.empty:
        st.warning("📭 Database is currently empty.")
    else:
        st.write(f"Total Records found: **{len(tracker.df)}**")
        display_df = tracker.df[['ID', 'Name', 'Course_Code', 'Score', 'GPA', 'Grade', 'Attendance', 'Net_Payable', 'Scholarship', 'Status']]
        st.dataframe(display_df, use_container_width=True)

# --- Feature 3: Live Ranked Performance Leaderboard ---
elif choice == "🏆 Merit List & Ranking":
    st.header("🏆 Academic Merit Performance Rankings")
    if tracker.df.empty:
        st.warning("📭 No data available to build the ranking table.")
    else:
        ranked_df = tracker.df.copy().sort_values(by=['GPA', 'Score'], ascending=False).reset_index(drop=True)
        ranked_df.index += 1
        ranked_df.index.name = 'Rank'
        st.dataframe(ranked_df[['ID', 'Name', 'Course_Code', 'Score', 'GPA', 'Grade']], use_container_width=True)

# --- Feature 4: Search & Profile View ---
elif choice == "🔍 Search Student Profile":
    st.header("🔍 Smart Profile Explorer")
    query = st.text_input("Enter Student ID or Name to Search:").strip().lower()
    
    if query:
        results = tracker.df[
            (tracker.df['ID'].astype(str).str.contains(query)) | 
            (tracker.df['Name'].str.lower().str.contains(query))
        ]
        if results.empty:
            st.error("❌ No student found matching the query criteria.")
        else:
            for index, row in results.iterrows():
                with st.expander(f"👤 Profile Matrix: {row['Name']} ({row['ID']})"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Student ID:** {row['ID']}")
                        st.write(f"**Email:** {row['Email']}")
                        st.write(f"**Enrolled Course:** {row['Course_Name']} ({row['Course_Code']})")
                        st.write(f"**Course Type:** {row['Course_Type']} ({row['Credits']} Credits)")
                    with col2:
                        st.write(f"**Score/Marks:** {row['Score']}")
                        st.write(f"**Grade Achieved:** {row['Grade']} (GPA: {row['GPA']:.2f})")
                        st.write(f"**Attendance:** {row['Attendance']}% ({row['Status']})")
                        st.write(f"**Net Accounts Payable:** {row['Net_Payable']:,} BDT")

# --- Feature 5: Financial Analytics ---
elif choice == "💰 Financial & Revenue Report":
    st.header("💰 Institutional Financial Analytics")
    if tracker.df.empty:
        st.warning("📭 Add data to look at revenue structures.")
    else:
        total_revenue = tracker.df['Tuition_Fee'].sum()
        total_waiver = tracker.df['Scholarship_Amount'].sum()
        actual_cash = tracker.df['Net_Payable'].sum()
        avg_gpa = tracker.df['GPA'].mean()
        pass_rate = (len(tracker.df[tracker.df['Grade'] != 'F']) / len(tracker.df)) * 100

        col1, col2, col3 = st.columns(3)
        col1.metric(label="Gross Tuition Revenue", value=f"{total_revenue:,.2f} BDT")
        col2.metric(label="Total Scholarship Waivers", value=f"- {total_waiver:,.2f} BDT")
        col3.metric(label="Net Accounts Receivable", value=f"{actual_cash:,.2f} BDT")

        st.markdown("---")
        col4, col5 = st.columns(2)
        col4.metric(label="Batch Average GPA", value=f"{avg_gpa:.2f} / 4.00")
        col5.metric(label="Academic Success Rate (Pass Rate)", value=f"{pass_rate:.1f} %")

# --- Feature 6: Visual Insights Engine ---
elif choice == "📊 Visual Analytics Dashboard":
    st.header("📊 Interactive Visual Insights")
    if tracker.df.empty:
        st.warning("📭 Graph generation requires structural data entries.")
    else:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Academic Grade Distribution")
            fig1, ax1 = plt.subplots()
            tracker.df['Grade'].value_counts().sort_index().plot(kind='bar', color='teal', edgecolor='black', ax=ax1)
            ax1.set_ylabel("Count")
            st.pyplot(fig1)

            st.subheader("Revenue Contribution by Course Type")
            fig2, ax2 = plt.subplots()
            tracker.df.groupby('Course_Type')['Net_Payable'].sum().plot(kind='pie', autopct='%1.1f%%', startangle=140, colors=['#ff9999','#66b3ff','#99ff99'], ax=ax2)
            ax2.set_ylabel("")
            st.pyplot(fig2)

        with col2:
            st.subheader("Attendance vs GPA Correlation")
            fig3, ax3 = plt.subplots()
            scatter = ax3.scatter(tracker.df['Attendance'], tracker.df['GPA'], alpha=0.7, c=tracker.df['GPA'], cmap='RdYlGn')
            ax3.axvline(75, color='red', linestyle='--', label='Min Attnd.')
            ax3.set_xlabel("Attendance %")
            ax3.set_ylabel("GPA")
            st.pyplot(fig3)

            st.subheader("Top 5 Performance Ranking")
            fig4, ax4 = plt.subplots()
            top_performers = tracker.df.nlargest(5, 'GPA')
            ax4.barh(top_performers['Name'], top_performers['GPA'], color='gold', edgecolor='black')
            ax4.set_xlim(0, 4.0)
            st.pyplot(fig4)

# --- Feature 7: Official Grading Matrix ---
elif choice == "📄 Official Grading Matrix":
    st.header("📄 Official Academic Grading Matrix")
    chart_data = [
        ["80 - 100", "A+", "4.00", "Outstanding / First Class Distinction"],
        ["75 - 79",  "A",  "3.75", "Excellent performance"],
        ["70 - 74",  "A-", "3.50", "Very Good progress"],
        ["65 - 69",  "B+", "3.25", "Good standard achieved"],
        ["60 - 64",  "B",  "3.00", "Satisfactory overall"],
        ["55 - 59",  "B-", "2.75", "Acceptable performance"],
        ["50 - 54",  "C+", "2.50", "Passable framework"],
        ["45 - 49",  "C",  "2.25", "Conditional Pass"],
        ["40 - 44",  "D",  "2.00", "Minimum passing tier"],
        ["Below 40", "F",  "0.00", "Fail / Retake Mandatory"]
    ]
    matrix_df = pd.DataFrame(chart_data, columns=["Marks Range", "Letter Grade", "Grade Point", "Performance Evaluation"])
    st.table(matrix_df)
    st.info(f"💡 Automated Framework: Students scoring a GPA >= {SCHOLARSHIP_THRESHOLD:.2f} trigger an automated 25% Tuition Waiver.")

# --- Feature 8: Flat File Document Exporter ---
elif choice == "📑 Export Text Report":
    st.header("📑 Flat File Document Exporter")
    if tracker.df.empty:
        st.warning("📭 Database contains zero entries. Aborting export.")
    else:
        if st.button("Generate & Structure Global Report File"):
            try:
                with open(REPORT_FILE, "w") as f:
                    f.write(f"{'═'*60}\n")
                    f.write(f"{tracker.univ_name.upper():^60}\n")
                    f.write(f"{'OFFICIAL ACADEMIC AND MERIT STATUS REPORT':^60}\n")
                    f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"{'═'*60}\n\n")
                    
                    clean_string = tabulate(tracker.df[['ID', 'Name', 'Course_Code', 'GPA', 'Grade', 'Status']], headers='keys', tablefmt='grid', showindex=False)
                    f.write(clean_string)
                
                st.success(f"📑 Report compiled and saved locally as `{REPORT_FILE}`")
                
                # Download Button for user
                with open(REPORT_FILE, "r") as file:
                    st.download_button(label="📥 Download Report File", data=file, file_name=REPORT_FILE, mime="text/plain")
            except Exception as e:
                st.error(f"❌ Error during file synthesis: {e}")

# --- Feature 9: System Configuration ---
elif choice == "⚙️ System Configuration":
    st.header("⚙️ System Configuration & Institutional Settings")
    new_univ = st.text_input("Change University Name Setting", value=tracker.univ_name)
    new_dept = st.text_input("Change Department Name Setting", value=tracker.dept_name)
    
    if st.button("Commit Configuration Updates"):
        tracker.univ_name = new_univ if new_univ else tracker.univ_name
        tracker.dept_name = new_dept if new_dept else tracker.dept_name
        tracker._save_config()
        st.success("✅ Global Settings Sync Complete!")

# --- Feature 10: Remove Student Record ---
elif choice == "🗑️ Remove Student Record":
    st.header("🗑️ Database Purge Module")
    if tracker.df.empty:
        st.warning("📭 Database has no targets to remove.")
    else:
        delete_id = st.text_input("Enter Target Student ID to Delete:").strip()
        if st.button("Execute Record Deletion", type="primary"):
            if delete_id in tracker.df['ID'].astype(str).values:
                tracker.df = tracker.df[tracker.df['ID'].astype(str) != delete_id]
                tracker._save_data()
                tracker._log_event(st.session_state['username'], f"Purged Student ID: {delete_id}")
                st.success(f"🗑️ Record for ID {delete_id} successfully deleted from the matrix.")
                st.rerun()
            else:
                st.error("❌ Target ID not found within current database instance.")