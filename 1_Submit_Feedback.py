import streamlit as st
from datetime import datetime
from utils.database import insert_feedback

st.set_page_config(page_title="Submit Feedback", layout="centered")
st.title("📝 Submit Your Feedback or Grievance")

# Define grievance categories
GRIEVANCE_CATEGORIES = [
    "Academic Issues",
    "Administrative Issues",
    "Facilities",
    "Student Welfare"
]

with st.form("feedback_form", clear_on_submit=True):
    st.subheader("Student Information")
    col1, col2 = st.columns(2)
    with col1:
        student_id = st.text_input("Student ID", help="Enter your student identification number (e.g., CU2021001)")
        student_name = st.text_input("Full Name (Optional)", help="Your full name")
    with col2:
        email = st.text_input("Email (Optional)", help="Your email address for follow-up")
        is_anonymous = st.checkbox("Submit Anonymously", value=False)

    st.subheader("Feedback Details")
    category = st.selectbox("Grievance Category", options=GRIEVANCE_CATEGORIES, help="Select the category that best describes your feedback")
    subject = st.text_input("Subject", help="A brief summary of your feedback or grievance")
    feedback_text = st.text_area("Detailed Feedback/Grievance", height=150, help="Please provide detailed information about your feedback or grievance.")
    priority = st.selectbox("Priority Level", options=["Low", "Medium", "High"], help="How urgent is this feedback?")

    submitted = st.form_submit_button("Submit Feedback", use_container_width=True)

    if submitted:
        if not student_id:
            st.error("❌ Student ID is required.")
        elif not feedback_text:
            st.error("❌ Detailed Feedback/Grievance is required.")
        else:
            # Convert boolean to integer for SQLite
            anon_status = 1 if is_anonymous else 0
            
            if insert_feedback(student_id, student_name, email, category, subject, feedback_text, priority, anon_status):
                st.success("✅ Your feedback/grievance has been submitted successfully!")
            else:
                st.error("❌ An error occurred during submission. Please try again.")

st.markdown("---")
st.info("Your feedback is important to us. Thank you for helping Caleb University improve!")

