import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from wordcloud import WordCloud
import os
from datetime import datetime

# Set page configuration
st.set_page_config(
    page_title="Student Feedback & Grievance System", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Define file paths
CSV_FILE = 'feedback_submissions.csv'
THEMES_FILE = 'processed_data_themes.csv'
CATEGORIES_FILE = 'processed_data_categories.csv'
SENTIMENT_FILE = 'processed_data_sentiment.csv'

# Define grievance categories
GRIEVANCE_CATEGORIES = [
    "Academic Issues",
    "Administrative Issues",
    "Facilities",
    "Student Welfare"
]

def load_data():
    """Load feedback submissions data"""
    if os.path.exists(CSV_FILE):
        return pd.read_csv(CSV_FILE)
    return pd.DataFrame(columns=['Timestamp', 'Student ID', 'Course', 'Grievance Category', 'Feedback Text'])

def save_data(df):
    """Save feedback submissions data"""
    df.to_csv(CSV_FILE, index=False)

def load_analysis_data():
    """Load preprocessed analysis data"""
    themes_df = pd.read_csv(THEMES_FILE) if os.path.exists(THEMES_FILE) else pd.DataFrame()
    categories_df = pd.read_csv(CATEGORIES_FILE) if os.path.exists(CATEGORIES_FILE) else pd.DataFrame()
    sentiment_df = pd.read_csv(SENTIMENT_FILE) if os.path.exists(SENTIMENT_FILE) else pd.DataFrame()
    return themes_df, categories_df, sentiment_df

def create_wordcloud(themes_df):
    """Create word cloud from themes data"""
    if not themes_df.empty:
        word_freq = dict(zip(themes_df['Theme'], themes_df['Count']))
        wordcloud = WordCloud(width=800, height=400, background_color='white').generate_from_frequencies(word_freq)
        
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.axis('off')
        return fig
    return None

def create_category_chart(categories_df):
    """Create category distribution chart"""
    if not categories_df.empty:
        fig = px.bar(categories_df, x='Category', y='Count', 
                    title='Feedback Distribution by Category',
                    color='Count',
                    color_continuous_scale='viridis')
        fig.update_layout(showlegend=False)
        return fig
    return None

def create_sentiment_chart(sentiment_df):
    """Create sentiment distribution pie chart"""
    if not sentiment_df.empty:
        fig = px.pie(sentiment_df, values='Count', names='Sentiment',
                    title='Sentiment Distribution',
                    color_discrete_map={'Positive': '#2E8B57', 'Negative': '#DC143C', 'Neutral': '#FFD700'})
        return fig
    return None

def create_themes_chart(themes_df):
    """Create top themes horizontal bar chart"""
    if not themes_df.empty:
        top_10 = themes_df.head(10)
        fig = px.bar(top_10, x='Count', y='Theme', orientation='h',
                    title='Top 10 Common Themes',
                    color='Count',
                    color_continuous_scale='blues')
        fig.update_layout(yaxis={'categoryorder':'total ascending'})
        return fig
    return None

# Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.selectbox("Choose a page", ["Submit Feedback", "Analytics Dashboard", "Data Insights"])

if page == "Submit Feedback":
    st.title("Student Feedback & Grievance Redressal System")
    st.header("Submit Your Feedback or Grievance")

    with st.form("feedback_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            student_id = st.text_input("Student ID", help="Enter your student identification number")
            course = st.text_input("Course (Optional)", help="e.g., CSC401, MTH202")
        
        with col2:
            grievance_category = st.selectbox("Grievance Category", options=GRIEVANCE_CATEGORIES, 
                                            help="Select the category that best describes your feedback")
        
        feedback_text = st.text_area("Feedback/Grievance Details", height=150,
                                   help="Please provide detailed information about your feedback or grievance.")

        submitted = st.form_submit_button("Submit", use_container_width=True)

        if submitted:
            if student_id and feedback_text:
                df = load_data()
                new_submission = pd.DataFrame([{
                    'Timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'Student ID': student_id,
                    'Course': course,
                    'Grievance Category': grievance_category,
                    'Feedback Text': feedback_text
                }])
                df = pd.concat([df, new_submission], ignore_index=True)
                save_data(df)
                st.success("✅ Your feedback/grievance has been submitted successfully!")
            else:
                st.error("❌ Please fill in Student ID and Feedback/Grievance Details.")

    # Recent submissions section
    st.subheader("Recent Submissions")
    df_display = load_data()
    if not df_display.empty:
        st.dataframe(df_display.tail(10), use_container_width=True)
    else:
        st.info("No submissions yet.")

elif page == "Analytics Dashboard":
    st.title("📊 Analytics Dashboard")
    st.markdown("### Insights from RateMyProfessor Dataset Analysis")
    
    # Load analysis data
    themes_df, categories_df, sentiment_df = load_analysis_data()
    
    if themes_df.empty:
        st.warning("⚠️ Analysis data not found. Please run the data analysis module first.")
        if st.button("Run Analysis"):
            with st.spinner("Running data analysis..."):
                os.system("python3 data_analysis.py")
                st.success("Analysis completed! Please refresh the page.")
    else:
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Themes", len(themes_df))
        with col2:
            st.metric("Categories Analyzed", len(categories_df))
        with col3:
            st.metric("Most Common Theme", themes_df.iloc[0]['Theme'] if not themes_df.empty else "N/A")
        with col4:
            st.metric("Top Theme Count", themes_df.iloc[0]['Count'] if not themes_df.empty else 0)
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            # Category distribution
            category_chart = create_category_chart(categories_df)
            if category_chart:
                st.plotly_chart(category_chart, use_container_width=True)
        
        with col2:
            # Sentiment distribution
            sentiment_chart = create_sentiment_chart(sentiment_df)
            if sentiment_chart:
                st.plotly_chart(sentiment_chart, use_container_width=True)
        
        # Top themes chart
        themes_chart = create_themes_chart(themes_df)
        if themes_chart:
            st.plotly_chart(themes_chart, use_container_width=True)
        
        # Word cloud
        st.subheader("📝 Word Cloud of Common Themes")
        wordcloud_fig = create_wordcloud(themes_df)
        if wordcloud_fig:
            st.pyplot(wordcloud_fig)

elif page == "Data Insights":
    st.title("🔍 Data Insights")
    st.markdown("### Detailed Analysis and Recommendations")
    
    # Load analysis data
    themes_df, categories_df, sentiment_df = load_analysis_data()
    
    if not themes_df.empty:
        # Summary statistics
        st.subheader("📈 Summary Statistics")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Theme Analysis:**")
            st.write(f"- Total unique themes identified: {len(themes_df)}")
            st.write(f"- Most frequent theme: '{themes_df.iloc[0]['Theme']}' ({themes_df.iloc[0]['Count']} occurrences)")
            st.write(f"- Average theme frequency: {themes_df['Count'].mean():.1f}")
        
        with col2:
            if not categories_df.empty:
                st.markdown("**Category Breakdown:**")
                for _, row in categories_df.iterrows():
                    percentage = (row['Count'] / categories_df['Count'].sum()) * 100
                    st.write(f"- {row['Category']}: {row['Count']} ({percentage:.1f}%)")
        
        # Detailed tables
        st.subheader("📋 Detailed Data Tables")
        
        tab1, tab2, tab3 = st.tabs(["Top Themes", "Category Distribution", "Sentiment Analysis"])
        
        with tab1:
            st.dataframe(themes_df, use_container_width=True)
        
        with tab2:
            if not categories_df.empty:
                st.dataframe(categories_df, use_container_width=True)
        
        with tab3:
            if not sentiment_df.empty:
                st.dataframe(sentiment_df, use_container_width=True)
        
        # Recommendations
        st.subheader("💡 Recommendations for University Administration")
        
        if not categories_df.empty:
            top_category = categories_df.loc[categories_df['Count'].idxmax()]
            
            recommendations = {
                "Academic Issues": [
                    "Review grading policies and ensure consistency across departments",
                    "Provide additional faculty training on effective teaching methods",
                    "Implement regular feedback mechanisms between students and faculty"
                ],
                "Administrative Issues": [
                    "Streamline registration and enrollment processes",
                    "Improve communication channels between administration and students",
                    "Enhance online systems for better user experience"
                ],
                "Facilities": [
                    "Conduct regular facility maintenance and upgrades",
                    "Invest in modern classroom technology and equipment",
                    "Improve campus infrastructure based on student needs"
                ],
                "Student Welfare": [
                    "Expand mental health and counseling services",
                    "Implement comprehensive anti-harassment policies",
                    "Create more support programs for student well-being"
                ]
            }
            
            st.markdown(f"**Priority Area: {top_category['Category']} ({top_category['Count']} issues identified)**")
            
            for recommendation in recommendations.get(top_category['Category'], []):
                st.write(f"• {recommendation}")
    
    else:
        st.warning("⚠️ No analysis data available. Please run the data analysis module first.")

# Footer
st.markdown("---")
st.markdown("**Student Feedback & Grievance Redressal System** | Caleb University | Powered by Streamlit")

