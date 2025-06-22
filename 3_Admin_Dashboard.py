import streamlit as st
import pandas as pd
import plotly.express as px
from utils.database import get_all_feedback, update_feedback_status

st.set_page_config(page_title="Admin Dashboard", layout="wide")

# Simple authentication
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔐 Admin Authentication")
    
    with st.form("auth_form"):
        admin_code = st.text_input("Admin Code", type="password", help="Enter the admin access code")
        login_button = st.form_submit_button("Login")
        
        if login_button:
            if admin_code == "admin123":  # Simple authentication - change in production
                st.session_state.authenticated = True
                st.success("✅ Authentication successful!")
                st.rerun()
            else:
                st.error("❌ Invalid admin code. Please try again.")
    
    st.info("💡 Default admin code: admin123 (Change this in production)")
    st.stop()

# Admin Dashboard
st.title("📊 Admin Dashboard")

# Logout button
if st.button("🚪 Logout", key="logout"):
    st.session_state.authenticated = False
    st.rerun()

# Load feedback data
df = get_all_feedback()

if df.empty:
    st.warning("No feedback submissions found.")
    st.stop()

# Dashboard metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    total_submissions = len(df)
    st.metric("Total Submissions", total_submissions)

with col2:
    pending_count = len(df[df['status'] == 'Pending'])
    st.metric("Pending", pending_count)

with col3:
    resolved_count = len(df[df['status'] == 'Resolved'])
    st.metric("Resolved", resolved_count)

with col4:
    high_priority = len(df[df['priority'] == 'High'])
    st.metric("High Priority", high_priority)

# Charts
col1, col2 = st.columns(2)

with col1:
    # Status distribution
    status_counts = df['status'].value_counts()
    fig_status = px.pie(values=status_counts.values, names=status_counts.index, 
                       title="Submission Status Distribution")
    st.plotly_chart(fig_status, use_container_width=True)

with col2:
    # Category distribution
    category_counts = df['category'].value_counts()
    fig_category = px.bar(x=category_counts.index, y=category_counts.values,
                         title="Feedback by Category")
    st.plotly_chart(fig_category, use_container_width=True)

# Feedback management
st.subheader("📋 Manage Feedback Submissions")

# Filter options
col1, col2, col3 = st.columns(3)

with col1:
    status_filter = st.selectbox("Filter by Status", ["All"] + list(df['status'].unique()))

with col2:
    category_filter = st.selectbox("Filter by Category", ["All"] + list(df['category'].unique()))

with col3:
    priority_filter = st.selectbox("Filter by Priority", ["All"] + list(df['priority'].unique()))

# Apply filters
filtered_df = df.copy()

if status_filter != "All":
    filtered_df = filtered_df[filtered_df['status'] == status_filter]

if category_filter != "All":
    filtered_df = filtered_df[filtered_df['category'] == category_filter]

if priority_filter != "All":
    filtered_df = filtered_df[filtered_df['priority'] == priority_filter]

# Display filtered data
st.dataframe(filtered_df, use_container_width=True)

# Update feedback status
st.subheader("🔄 Update Feedback Status")

if not filtered_df.empty:
    selected_id = st.selectbox("Select Feedback ID", filtered_df['id'].tolist())
    
    col1, col2 = st.columns(2)
    
    with col1:
        new_status = st.selectbox("New Status", ["Pending", "In Progress", "Resolved", "Closed"])
    
    with col2:
        admin_notes = st.text_area("Admin Notes", height=100)
    
    if st.button("Update Status"):
        if update_feedback_status(selected_id, new_status, admin_notes):
            st.success(f"✅ Feedback {selected_id} status updated to {new_status}")
            st.rerun()
        else:
            st.error("❌ Failed to update status")

# Export data
st.subheader("📤 Export Data")

if st.button("Download CSV"):
    csv = df.to_csv(index=False)
    st.download_button(
        label="📥 Download Feedback Data",
        data=csv,
        file_name=f"feedback_data_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )

