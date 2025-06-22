import sqlite3
import pandas as pd
from datetime import datetime

DATABASE_NAME = 'feedback_system.db'

def create_connection():
    """Create a database connection to the SQLite database"""
    conn = None
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        return conn
    except sqlite3.Error as e:
        print(e)
    return conn

def create_tables():
    """Create tables in the database"""
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS feedback_submissions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id TEXT NOT NULL,
                    student_name TEXT,
                    email TEXT,
                    category TEXT NOT NULL,
                    subject TEXT,
                    feedback_text TEXT NOT NULL,
                    priority TEXT,
                    is_anonymous INTEGER,
                    submission_date TEXT NOT NULL,
                    status TEXT,
                    admin_notes TEXT
                );
            """)
            conn.commit()
            print("Tables created successfully.")
        except sqlite3.Error as e:
            print(e)
        finally:
            conn.close()

def insert_feedback(student_id, student_name, email, category, subject, feedback_text, priority, is_anonymous):
    """Insert a new feedback submission into the database"""
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            submission_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            status = 'Pending'
            cursor.execute("""
                INSERT INTO feedback_submissions (
                    student_id, student_name, email, category, subject, feedback_text, priority, is_anonymous, submission_date, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, (student_id, student_name, email, category, subject, feedback_text, priority, is_anonymous, submission_date, status))
            conn.commit()
            print("Feedback submitted successfully.")
            return True
        except sqlite3.Error as e:
            print(e)
            return False
        finally:
            conn.close()
    return False

def get_all_feedback():
    """Retrieve all feedback submissions"""
    conn = create_connection()
    if conn:
        try:
            df = pd.read_sql_query("SELECT * FROM feedback_submissions", conn)
            return df
        except sqlite3.Error as e:
            print(e)
            return pd.DataFrame()
        finally:
            conn.close()
    return pd.DataFrame()

def update_feedback_status(feedback_id, new_status, admin_notes=None):
    """Update the status and admin notes of a feedback submission"""
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            if admin_notes:
                cursor.execute("UPDATE feedback_submissions SET status = ?, admin_notes = ? WHERE id = ?",
                               (new_status, admin_notes, feedback_id))
            else:
                cursor.execute("UPDATE feedback_submissions SET status = ? WHERE id = ?",
                               (new_status, feedback_id))
            conn.commit()
            print(f"Feedback {feedback_id} status updated to {new_status}.")
            return True
        except sqlite3.Error as e:
            print(e)
            return False
        finally:
            conn.close()
    return False

if __name__ == '__main__':
    create_tables()
    # Example usage:
    # insert_feedback('CU001', 'John Doe', 'john.doe@example.com', 'Academic Issues', 'Grading Policy', 'The grading policy is unclear.', 'High', 0)
    # df = get_all_feedback()
    # print(df.head())
    # update_feedback_status(1, 'Resolved', 'Discussed with professor.')

