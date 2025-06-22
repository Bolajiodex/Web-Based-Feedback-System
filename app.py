import streamlit as st

st.set_page_config(
    page_title="Caleb University Feedback System",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for university branding
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1e3a8a 0%, #3b82f6 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
    }
    .university-motto {
        font-style: italic;
        font-size: 1.2rem;
        margin-top: 0.5rem;
    }
    .contact-info {
        background-color: #f8fafc;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #3b82f6;
    }
</style>
""", unsafe_allow_html=True)

# Main header
st.markdown("""
<div class="main-header">
    <h1>🎓 Caleb University</h1>
    <h2>Feedback & Grievance Redressal System</h2>
    <p class="university-motto">"For God and Humanity"</p>
</div>
""", unsafe_allow_html=True)

# Add the logo
st.image("assets/caleb_university_logo.png", width=150)

# Welcome message
st.markdown("""
## Welcome to the Caleb University Feedback System

This system enables students to submit feedback and grievances while providing administrators 
with comprehensive tools to manage and track all submissions.

### 🚀 Getting Started

Use the sidebar navigation to:
- **📝 Submit Feedback**: Submit your feedback or grievances securely
- **📊 Admin Dashboard**: Administrative interface for managing submissions (Admin access required)
- **🗄️ Database Manager**: Advanced database management tools (Admin access required)

### 📋 Features

**For Students:**
- 📝 Submit feedback securely with categorization
- 🔍 Track submission status
- 📱 User-friendly interface with university branding

**For Administrators:**
- 📈 Review and manage all submissions
- 📊 Track resolution status and progress
- 🗄️ Advanced analytics and data export capabilities
- 🔐 Secure authentication system
""")

# Contact information
st.markdown("""
<div class="contact-info">
    <h3>📞 Contact Information</h3>
    <p><strong>Caleb University</strong></p>
    <p>📍 Address: Imota, Lagos State, Nigeria</p>
    <p>📧 Email: feedback@calebuniversity.edu.ng</p>
    <p>🌐 Website: www.calebuniversity.edu.ng</p>
</div>
""", unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("*Developed with ❤️ for Caleb University*")

