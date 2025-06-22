import pandas as pd
import sqlite3
from utils.database import create_connection
from utils.text_analysis import TextAnalyzer

def get_feedback_analytics():
    """Get comprehensive analytics from feedback data"""
    conn = create_connection()
    if not conn:
        return {}
    
    try:
        # Get all feedback data
        df = pd.read_sql_query("SELECT * FROM feedback_submissions", conn)
        
        if df.empty:
            return {}
        
        # Initialize text analyzer
        analyzer = TextAnalyzer()
        
        # Perform analysis
        analytics = analyzer.analyze_feedback_data(df)
        
        # Add time-based analytics
        df['submission_date'] = pd.to_datetime(df['submission_date'])
        
        # Monthly submission trends
        monthly_trends = df.groupby(df['submission_date'].dt.to_period('M')).size().to_dict()
        monthly_trends = {str(k): v for k, v in monthly_trends.items()}
        
        # Daily submission trends (last 30 days)
        recent_df = df[df['submission_date'] >= (pd.Timestamp.now() - pd.Timedelta(days=30))]
        daily_trends = recent_df.groupby(recent_df['submission_date'].dt.date).size().to_dict()
        daily_trends = {str(k): v for k, v in daily_trends.items()}
        
        analytics.update({
            'monthly_trends': monthly_trends,
            'daily_trends': daily_trends,
            'avg_submissions_per_day': len(df) / max(1, (df['submission_date'].max() - df['submission_date'].min()).days),
            'anonymous_percentage': (df['is_anonymous'].sum() / len(df)) * 100 if len(df) > 0 else 0
        })
        
        return analytics
        
    except Exception as e:
        print(f"Error in analytics: {e}")
        return {}
    finally:
        conn.close()

def get_feedback_by_category():
    """Get feedback grouped by category"""
    conn = create_connection()
    if not conn:
        return pd.DataFrame()
    
    try:
        query = """
        SELECT category, COUNT(*) as count, 
               AVG(CASE WHEN priority = 'High' THEN 3 
                        WHEN priority = 'Medium' THEN 2 
                        ELSE 1 END) as avg_priority_score
        FROM feedback_submissions 
        GROUP BY category
        ORDER BY count DESC
        """
        df = pd.read_sql_query(query, conn)
        return df
    except Exception as e:
        print(f"Error getting category data: {e}")
        return pd.DataFrame()
    finally:
        conn.close()

def get_feedback_trends():
    """Get feedback submission trends over time"""
    conn = create_connection()
    if not conn:
        return pd.DataFrame()
    
    try:
        query = """
        SELECT DATE(submission_date) as date, 
               COUNT(*) as submissions,
               SUM(CASE WHEN priority = 'High' THEN 1 ELSE 0 END) as high_priority
        FROM feedback_submissions 
        GROUP BY DATE(submission_date)
        ORDER BY date DESC
        LIMIT 30
        """
        df = pd.read_sql_query(query, conn)
        return df
    except Exception as e:
        print(f"Error getting trends data: {e}")
        return pd.DataFrame()
    finally:
        conn.close()

def get_status_summary():
    """Get summary of feedback status"""
    conn = create_connection()
    if not conn:
        return pd.DataFrame()
    
    try:
        query = """
        SELECT status, COUNT(*) as count,
               AVG(julianday('now') - julianday(submission_date)) as avg_days_open
        FROM feedback_submissions 
        GROUP BY status
        """
        df = pd.read_sql_query(query, conn)
        return df
    except Exception as e:
        print(f"Error getting status summary: {e}")
        return pd.DataFrame()
    finally:
        conn.close()

def search_feedback(search_term, category=None, status=None, priority=None):
    """Search feedback with filters"""
    conn = create_connection()
    if not conn:
        return pd.DataFrame()
    
    try:
        query = "SELECT * FROM feedback_submissions WHERE 1=1"
        params = []
        
        if search_term:
            query += " AND (feedback_text LIKE ? OR subject LIKE ? OR student_name LIKE ?)"
            search_pattern = f"%{search_term}%"
            params.extend([search_pattern, search_pattern, search_pattern])
        
        if category:
            query += " AND category = ?"
            params.append(category)
        
        if status:
            query += " AND status = ?"
            params.append(status)
        
        if priority:
            query += " AND priority = ?"
            params.append(priority)
        
        query += " ORDER BY submission_date DESC"
        
        df = pd.read_sql_query(query, conn, params=params)
        return df
    except Exception as e:
        print(f"Error searching feedback: {e}")
        return pd.DataFrame()
    finally:
        conn.close()

def get_priority_distribution():
    """Get distribution of feedback by priority"""
    conn = create_connection()
    if not conn:
        return pd.DataFrame()
    
    try:
        query = """
        SELECT priority, category, COUNT(*) as count
        FROM feedback_submissions 
        GROUP BY priority, category
        ORDER BY priority, count DESC
        """
        df = pd.read_sql_query(query, conn)
        return df
    except Exception as e:
        print(f"Error getting priority distribution: {e}")
        return pd.DataFrame()
    finally:
        conn.close()

if __name__ == '__main__':
    # Test the functions
    analytics = get_feedback_analytics()
    print("Analytics:", analytics)
    
    category_data = get_feedback_by_category()
    print("Category data:", category_data)
    
    trends = get_feedback_trends()
    print("Trends:", trends)

