import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from utils.advanced_database import (
    get_feedback_analytics, 
    get_feedback_by_category, 
    get_feedback_trends,
    get_status_summary,
    get_priority_distribution
)

st.set_page_config(page_title="Analytics & Insights", layout="wide")

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

# Analytics Dashboard
st.title("📊 Analytics & Insights")

# Logout button
if st.button("🚪 Logout", key="logout"):
    st.session_state.authenticated = False
    st.rerun()

# Get analytics data
analytics = get_feedback_analytics()

if not analytics or analytics.get('total_feedback', 0) == 0:
    st.warning("No feedback data available for analysis.")
    st.info("Submit some feedback first to see analytics.")
    st.stop()

# Key Metrics
st.subheader("📈 Key Metrics")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Feedback", analytics.get('total_feedback', 0))

with col2:
    avg_daily = analytics.get('avg_submissions_per_day', 0)
    st.metric("Avg Daily Submissions", f"{avg_daily:.1f}")

with col3:
    anon_pct = analytics.get('anonymous_percentage', 0)
    st.metric("Anonymous Submissions", f"{anon_pct:.1f}%")

with col4:
    # Most common category
    cat_dist = analytics.get('category_distribution', {})
    top_category = max(cat_dist.items(), key=lambda x: x[1])[0] if cat_dist else "N/A"
    st.metric("Top Category", top_category)

# Visualizations
st.subheader("📊 Data Visualizations")

# Create tabs for different visualizations
tab1, tab2, tab3, tab4 = st.tabs(["Category Analysis", "Sentiment Analysis", "Trends", "Word Cloud"])

with tab1:
    st.markdown("### Feedback Distribution by Category")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Category distribution pie chart
        cat_dist = analytics.get('category_distribution', {})
        if cat_dist:
            fig_pie = px.pie(
                values=list(cat_dist.values()), 
                names=list(cat_dist.keys()),
                title="Feedback by Category"
            )
            st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        # Category bar chart
        if cat_dist:
            fig_bar = px.bar(
                x=list(cat_dist.keys()), 
                y=list(cat_dist.values()),
                title="Category Counts",
                labels={'x': 'Category', 'y': 'Count'}
            )
            st.plotly_chart(fig_bar, use_container_width=True)
    
    # Priority distribution by category
    priority_df = get_priority_distribution()
    if not priority_df.empty:
        st.markdown("### Priority Distribution by Category")
        fig_priority = px.bar(
            priority_df, 
            x='category', 
            y='count', 
            color='priority',
            title="Priority Levels by Category"
        )
        st.plotly_chart(fig_priority, use_container_width=True)

with tab2:
    st.markdown("### Sentiment Analysis")
    
    sentiment_dist = analytics.get('sentiment', {})
    if sentiment_dist:
        col1, col2 = st.columns(2)
        
        with col1:
            # Sentiment pie chart
            colors = {'Positive': '#2E8B57', 'Negative': '#DC143C', 'Neutral': '#FFD700'}
            fig_sentiment = px.pie(
                values=list(sentiment_dist.values()),
                names=list(sentiment_dist.keys()),
                title="Sentiment Distribution",
                color=list(sentiment_dist.keys()),
                color_discrete_map=colors
            )
            st.plotly_chart(fig_sentiment, use_container_width=True)
        
        with col2:
            # Sentiment metrics
            total_sentiment = sum(sentiment_dist.values())
            if total_sentiment > 0:
                positive_pct = (sentiment_dist.get('Positive', 0) / total_sentiment) * 100
                negative_pct = (sentiment_dist.get('Negative', 0) / total_sentiment) * 100
                neutral_pct = (sentiment_dist.get('Neutral', 0) / total_sentiment) * 100
                
                st.metric("Positive Feedback", f"{positive_pct:.1f}%")
                st.metric("Negative Feedback", f"{negative_pct:.1f}%")
                st.metric("Neutral Feedback", f"{neutral_pct:.1f}%")

with tab3:
    st.markdown("### Submission Trends")
    
    # Get trends data
    trends_df = get_feedback_trends()
    
    if not trends_df.empty:
        # Daily submissions trend
        fig_trends = px.line(
            trends_df, 
            x='date', 
            y='submissions',
            title="Daily Submissions (Last 30 Days)",
            markers=True
        )
        st.plotly_chart(fig_trends, use_container_width=True)
        
        # High priority trends
        if 'high_priority' in trends_df.columns:
            fig_priority_trend = px.bar(
                trends_df, 
                x='date', 
                y='high_priority',
                title="High Priority Submissions Over Time"
            )
            st.plotly_chart(fig_priority_trend, use_container_width=True)
    
    # Status summary
    status_df = get_status_summary()
    if not status_df.empty:
        st.markdown("### Status Summary")
        col1, col2 = st.columns(2)
        
        with col1:
            fig_status = px.bar(
                status_df, 
                x='status', 
                y='count',
                title="Feedback by Status"
            )
            st.plotly_chart(fig_status, use_container_width=True)
        
        with col2:
            st.dataframe(status_df, use_container_width=True)

with tab4:
    st.markdown("### Word Cloud - Common Themes")
    
    themes = analytics.get('themes', [])
    if themes:
        # Create word cloud
        word_freq = dict(themes[:50])  # Top 50 words
        
        if word_freq:
            wordcloud = WordCloud(
                width=800, 
                height=400, 
                background_color='white',
                colormap='viridis'
            ).generate_from_frequencies(word_freq)
            
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.imshow(wordcloud, interpolation='bilinear')
            ax.axis('off')
            st.pyplot(fig)
        
        # Top themes table
        st.markdown("### Top Themes")
        themes_df = pd.DataFrame(themes[:20], columns=['Theme', 'Frequency'])
        st.dataframe(themes_df, use_container_width=True)
    else:
        st.info("No themes data available. Submit more feedback to generate word cloud.")

# Recommendations
st.subheader("💡 Automated Recommendations")

if analytics:
    # Generate recommendations based on data
    recommendations = []
    
    # Category-based recommendations
    cat_dist = analytics.get('category_distribution', {})
    if cat_dist:
        top_category = max(cat_dist.items(), key=lambda x: x[1])
        recommendations.append(f"**Priority Focus**: {top_category[0]} has the highest number of submissions ({top_category[1]}). Consider reviewing policies and procedures in this area.")
    
    # Sentiment-based recommendations
    sentiment_dist = analytics.get('sentiment', {})
    if sentiment_dist:
        total_sentiment = sum(sentiment_dist.values())
        negative_pct = (sentiment_dist.get('Negative', 0) / total_sentiment) * 100 if total_sentiment > 0 else 0
        
        if negative_pct > 30:
            recommendations.append(f"**Attention Needed**: {negative_pct:.1f}% of feedback is negative. Consider implementing improvement measures.")
        elif negative_pct < 15:
            recommendations.append(f"**Good Performance**: Only {negative_pct:.1f}% of feedback is negative. Maintain current standards.")
    
    # Anonymous submissions
    anon_pct = analytics.get('anonymous_percentage', 0)
    if anon_pct > 50:
        recommendations.append(f"**Trust Building**: {anon_pct:.1f}% of submissions are anonymous. Consider building more trust to encourage open feedback.")
    
    # Display recommendations
    for i, rec in enumerate(recommendations, 1):
        st.markdown(f"{i}. {rec}")

# Export options
st.subheader("📤 Export Analytics")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("Export Summary Report"):
        # Create summary report
        summary_data = {
            'Metric': ['Total Feedback', 'Avg Daily Submissions', 'Anonymous %', 'Top Category'],
            'Value': [
                analytics.get('total_feedback', 0),
                f"{analytics.get('avg_submissions_per_day', 0):.1f}",
                f"{analytics.get('anonymous_percentage', 0):.1f}%",
                max(cat_dist.items(), key=lambda x: x[1])[0] if cat_dist else "N/A"
            ]
        }
        summary_df = pd.DataFrame(summary_data)
        
        csv = summary_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Summary",
            data=csv,
            file_name=f"analytics_summary_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )

with col2:
    if st.button("Export Themes Data"):
        if themes:
            themes_df = pd.DataFrame(themes, columns=['Theme', 'Frequency'])
            csv = themes_df.to_csv(index=False)
            st.download_button(
                label="📥 Download Themes",
                data=csv,
                file_name=f"themes_data_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )

with col3:
    if st.button("Export Category Data"):
        if cat_dist:
            cat_df = pd.DataFrame(list(cat_dist.items()), columns=['Category', 'Count'])
            csv = cat_df.to_csv(index=False)
            st.download_button(
                label="📥 Download Categories",
                data=csv,
                file_name=f"category_data_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )

# Footer
st.markdown("---")
st.markdown("*Analytics powered by advanced text analysis and data visualization*")

