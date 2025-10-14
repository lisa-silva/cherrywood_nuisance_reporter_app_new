"""
Cherrywood Apartments - Nuisance Reporting System
Powered by AI Transform

This application streamlines nuisance reporting for apartment complexes,
enabling tenants to submit reports and management to view all submissions.
"""

import streamlit as st
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configuration
REPORTS_FILE = "reports.csv"
TENANT_USERNAME = "tenant"
TENANT_PASSWORD = "password123"

# Email configuration (loaded from environment variables)
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD", "")
SECURITY_EMAIL = os.getenv("SECURITY_EMAIL", "")

# Page configuration
st.set_page_config(
    page_title="Cherrywood Apartments - Nuisance Reporting",
    page_icon="🏢",
    layout="wide"
)

# Custom CSS for professional styling with green tones
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stButton>button {
        background-color: #2d5016;
        color: white;
        border-radius: 5px;
        padding: 0.5rem 2rem;
        border: none;
        font-weight: 600;
    }
    .stButton>button:hover {
        background-color: #3d6b1f;
    }
    h1, h2, h3 {
        color: #2d5016;
    }
    .footer {
        text-align: center;
        padding: 2rem;
        color: #6c757d;
        font-size: 0.9rem;
    }
    .logo-container {
        text-align: center;
        padding: 1rem;
    }
    </style>
""", unsafe_allow_html=True)


def initialize_csv():
    """
    Initialize the CSV file if it doesn't exist.
    Creates a file with headers for storing nuisance reports.
    """
    if not os.path.exists(REPORTS_FILE):
        df = pd.DataFrame(columns=[
            "Timestamp", "Issue Type", "Description", "Location", "Status"
        ])
        df.to_csv(REPORTS_FILE, index=False)


def save_report(issue_type, description, location):
    """
    Save a nuisance report to the CSV file.
    
    Args:
        issue_type: Type of nuisance (Car Alarm, Noise Complaint, Other)
        description: Detailed description of the issue
        location: Location where the issue occurred
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_report = pd.DataFrame([{
        "Timestamp": timestamp,
        "Issue Type": issue_type,
        "Description": description,
        "Location": location,
        "Status": "Pending"
    }])
    
    # Append to existing CSV
    if os.path.exists(REPORTS_FILE):
        df = pd.read_csv(REPORTS_FILE)
        df = pd.concat([df, new_report], ignore_index=True)
    else:
        df = new_report
    
    df.to_csv(REPORTS_FILE, index=False)


def send_email_alert(issue_type, description, location):
    """
    Send an email alert to security when a report is submitted.
    
    Args:
        issue_type: Type of nuisance reported
        description: Detailed description of the issue
        location: Location where the issue occurred
    
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    # Check if email credentials are configured
    if not SENDER_EMAIL or not SENDER_PASSWORD or not SECURITY_EMAIL:
        return False
    
    try:
        # Create email message
        message = MIMEMultipart()
        message["From"] = SENDER_EMAIL
        message["To"] = SECURITY_EMAIL
        message["Subject"] = f"🚨 Nuisance Report: {issue_type}"
        
        # Email body
        body = f"""
        A new nuisance report has been submitted at Cherrywood Apartments.
        
        Issue Type: {issue_type}
        Location: {location}
        Time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        
        Description:
        {description}
        
        Please address this issue promptly.
        
        ---
        This alert was generated automatically by the Cherrywood Apartments Nuisance Reporting System.
        Powered by AI Transform
        """
        
        message.attach(MIMEText(body, "plain"))
        
        # Connect to SMTP server and send email
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(message)
        
        return True
    except Exception as e:
        st.error(f"Failed to send email alert: {str(e)}")
        return False


def tenant_interface():
    """
    Display the tenant interface for submitting nuisance reports.
    """
    st.title("🏢 Cherrywood Apartments")
    st.subheader("Nuisance Reporting System")
    st.markdown("*Powered by AI Transform*")
    
    # Display placeholder logo
    st.markdown("""
        <div class="logo-container">
            <img src="https://via.placeholder.com/300x100/2d5016/ffffff?text=Cherrywood+Apartments" 
                 alt="Cherrywood Logo" style="max-width: 300px;">
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.write("""
    Welcome to the Cherrywood Apartments Nuisance Reporting System. 
    Please use this form to report any disturbances or issues that require attention from our security team.
    """)
    
    # Report submission form
    with st.form("report_form"):
        st.subheader("Submit a Report")
        
        issue_type = st.selectbox(
            "Issue Type *",
            ["Car Alarm", "Noise Complaint", "Other"],
            help="Select the type of nuisance you are reporting"
        )
        
        location = st.text_input(
            "Location *",
            placeholder="e.g., Parking Lot B, Building 3 Unit 205",
            help="Specify where the issue is occurring"
        )
        
        description = st.text_area(
            "Description *",
            placeholder="Please provide details about the issue...",
            height=150,
            help="Describe the nuisance in detail"
        )
        
        submit_button = st.form_submit_button("Submit Report")
        
        if submit_button:
            # Validate inputs
            if not location or not description:
                st.error("Please fill in all required fields.")
            else:
                # Save report to CSV
                save_report(issue_type, description, location)
                
                # Send email alert
                email_sent = send_email_alert(issue_type, description, location)
                
                # Show success message
                st.success("✅ Report submitted successfully!")
                
                if email_sent:
                    st.info("📧 Security team has been notified via email.")
                else:
                    st.warning("⚠️ Report saved, but email notification could not be sent. Please check email configuration.")
                
                st.balloons()


def management_dashboard():
    """
    Display the management dashboard showing all submitted reports.
    """
    st.title("📊 Management Dashboard")
    st.subheader("All Nuisance Reports")
    st.markdown("*Powered by AI Transform*")
    st.markdown("---")
    
    # Load and display reports
    if os.path.exists(REPORTS_FILE):
        df = pd.read_csv(REPORTS_FILE)
        
        if len(df) > 0:
            st.write(f"**Total Reports:** {len(df)}")
            
            # Display reports in a table
            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True
            )
            
            # Download button for reports
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Reports as CSV",
                data=csv,
                file_name=f"cherrywood_reports_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        else:
            st.info("No reports have been submitted yet.")
    else:
        st.info("No reports have been submitted yet.")


def login_page():
    """
    Display the login page for tenant authentication.
    """
    st.title("🏢 Cherrywood Apartments")
    st.subheader("Nuisance Reporting System - Login")
    st.markdown("*Powered by AI Transform*")
    
    # Display placeholder logo
    st.markdown("""
        <div class="logo-container">
            <img src="https://via.placeholder.com/300x100/2d5016/ffffff?text=Cherrywood+Apartments" 
                 alt="Cherrywood Logo" style="max-width: 300px;">
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        login_button = st.form_submit_button("Login")
        
        if login_button:
            if username == TENANT_USERNAME and password == TENANT_PASSWORD:
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("Invalid username or password. Please try again.")
    
    st.info("**Demo Credentials:** Username: `tenant` | Password: `password123`")


def main():
    """
    Main application function that handles navigation and page rendering.
    """
    # Initialize CSV file
    initialize_csv()
    
    # Initialize session state for login
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    
    # Show login page if not logged in
    if not st.session_state.logged_in:
        login_page()
        return
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio(
        "Go to",
        ["Submit Report", "View Dashboard"]
    )
    
    # Logout button
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("""
        ### About
        This system streamlines nuisance reporting for Cherrywood Apartments,
        enabling efficient communication between tenants and security.
        
        **Powered by AI Transform**
    """)
    
    # Display selected page
    if page == "Submit Report":
        tenant_interface()
    elif page == "View Dashboard":
        management_dashboard()
    
    # Footer
    st.markdown("---")
    st.markdown("""
        <div class="footer">
            <p>© 2025 Cherrywood Apartments | Powered by <strong>AI Transform</strong></p>
            <p>Modernizing apartment complex operations through intelligent automation</p>
        </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
