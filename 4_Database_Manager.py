import streamlit as st
import pandas as pd
import sqlite3
from utils.database import get_all_feedback, create_connection

st.set_page_config(page_title="Database Manager", layout="wide")

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

# Database Manager
st.title("🗄️ Database Manager")

# Logout button
if st.button("🚪 Logout", key="logout"):
    st.session_state.authenticated = False
    st.rerun()

# Database statistics
st.subheader("📊 Database Statistics")

df = get_all_feedback()

if not df.empty:
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Records", len(df))
    
    with col2:
        st.metric("Database Size", f"{len(df) * 0.001:.2f} KB")
    
    with col3:
        earliest_date = df['submission_date'].min()
        st.metric("Earliest Submission", earliest_date[:10] if earliest_date else "N/A")
    
    with col4:
        latest_date = df['submission_date'].max()
        st.metric("Latest Submission", latest_date[:10] if latest_date else "N/A")

# Raw data view
st.subheader("📋 Raw Data View")

if not df.empty:
    st.dataframe(df, use_container_width=True)
    
    # Data export options
    st.subheader("📤 Export Options")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Export as CSV"):
            csv = df.to_csv(index=False)
            st.download_button(
                label="📥 Download CSV",
                data=csv,
                file_name=f"feedback_export_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
    
    with col2:
        if st.button("Export as JSON"):
            json_data = df.to_json(orient='records', indent=2)
            st.download_button(
                label="📥 Download JSON",
                data=json_data,
                file_name=f"feedback_export_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
    
    with col3:
        if st.button("Export as Excel"):
            # Note: This would require openpyxl package
            st.info("Excel export requires additional package installation")

# Database maintenance
st.subheader("🔧 Database Maintenance")

col1, col2 = st.columns(2)

with col1:
    st.markdown("**Backup Database**")
    if st.button("Create Backup"):
        # Simple backup by exporting all data
        csv_backup = df.to_csv(index=False)
        st.download_button(
            label="📥 Download Backup",
            data=csv_backup,
            file_name=f"feedback_backup_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )

with col2:
    st.markdown("**Database Info**")
    if st.button("Show Database Schema"):
        conn = create_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("PRAGMA table_info(feedback_submissions)")
            schema = cursor.fetchall()
            schema_df = pd.DataFrame(schema, columns=['cid', 'name', 'type', 'notnull', 'dflt_value', 'pk'])
            st.dataframe(schema_df)
            conn.close()

# Advanced queries
st.subheader("🔍 Advanced Queries")

query_type = st.selectbox("Select Query Type", [
    "Custom SQL Query",
    "Submissions by Date Range",
    "High Priority Items",
    "Anonymous Submissions"
])

if query_type == "Custom SQL Query":
    st.warning("⚠️ Use with caution. Only SELECT queries are recommended.")
    custom_query = st.text_area("Enter SQL Query", height=100, 
                                placeholder="SELECT * FROM feedback_submissions WHERE...")
    
    if st.button("Execute Query"):
        if custom_query.strip().upper().startswith('SELECT'):
            try:
                conn = create_connection()
                result_df = pd.read_sql_query(custom_query, conn)
                st.dataframe(result_df)
                conn.close()
            except Exception as e:
                st.error(f"Query error: {e}")
        else:
            st.error("Only SELECT queries are allowed for security reasons.")

elif query_type == "Submissions by Date Range":
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date")
    with col2:
        end_date = st.date_input("End Date")
    
    if st.button("Filter by Date Range"):
        filtered_df = df[
            (pd.to_datetime(df['submission_date']).dt.date >= start_date) &
            (pd.to_datetime(df['submission_date']).dt.date <= end_date)
        ]
        st.dataframe(filtered_df)

elif query_type == "High Priority Items":
    if st.button("Show High Priority Items"):
        high_priority_df = df[df['priority'] == 'High']
        st.dataframe(high_priority_df)

elif query_type == "Anonymous Submissions":
    if st.button("Show Anonymous Submissions"):
        anonymous_df = df[df['is_anonymous'] == 1]
        st.dataframe(anonymous_df)

else:
    st.info("No feedback submissions found in the database.")

# Footer
st.markdown("---")
st.markdown("*Database Manager - Handle with care*")

