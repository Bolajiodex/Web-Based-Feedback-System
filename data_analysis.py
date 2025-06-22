import pandas as pd
import numpy as np
import re
from collections import Counter
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    nltk.download('punkt_tab')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet')

class FeedbackAnalyzer:
    def __init__(self, dataset_path):
        self.df = pd.read_csv(dataset_path)
        self.stop_words = set(stopwords.words('english'))
        self.lemmatizer = WordNetLemmatizer()
        
    def clean_text(self, text):
        """Clean and preprocess text data"""
        if pd.isna(text):
            return ""
        
        # Convert to lowercase
        text = str(text).lower()
        
        # Remove special characters and digits
        text = re.sub(r'[^a-zA-Z\s]', '', text)
        
        # Tokenize
        tokens = word_tokenize(text)
        
        # Remove stopwords and lemmatize
        tokens = [self.lemmatizer.lemmatize(token) for token in tokens 
                 if token not in self.stop_words and len(token) > 2]
        
        return ' '.join(tokens)
    
    def extract_themes(self, text_column='comments', top_n=20):
        """Extract common themes from text data"""
        # Clean all comments
        cleaned_comments = self.df[text_column].apply(self.clean_text)
        
        # Combine all text
        all_text = ' '.join(cleaned_comments.dropna())
        
        # Get word frequency
        words = all_text.split()
        word_freq = Counter(words)
        
        return word_freq.most_common(top_n)
    
    def categorize_feedback(self):
        """Categorize feedback into predefined categories"""
        categories = {
            'Academic Issues': ['grade', 'grading', 'exam', 'test', 'assignment', 'homework', 'difficult', 'hard', 'easy', 'content', 'material', 'lecture', 'teaching', 'explain', 'understand'],
            'Administrative Issues': ['registration', 'enroll', 'schedule', 'office', 'hour', 'response', 'email', 'communication', 'policy', 'requirement'],
            'Facilities': ['classroom', 'room', 'building', 'equipment', 'technology', 'computer', 'projector', 'space', 'environment'],
            'Student Welfare': ['help', 'support', 'care', 'concern', 'stress', 'mental', 'health', 'safety', 'harassment', 'discrimination']
        }
        
        # Initialize category counts
        category_counts = {cat: 0 for cat in categories.keys()}
        
        # Analyze each comment
        for comment in self.df['comments'].dropna():
            cleaned_comment = self.clean_text(comment)
            comment_words = cleaned_comment.split()
            
            for category, keywords in categories.items():
                if any(keyword in comment_words for keyword in keywords):
                    category_counts[category] += 1
        
        return category_counts
    
    def sentiment_analysis_simple(self):
        """Simple sentiment analysis based on positive/negative words"""
        positive_words = ['good', 'great', 'excellent', 'amazing', 'awesome', 'love', 'best', 'fantastic', 'wonderful', 'helpful', 'easy', 'clear', 'interesting', 'fun', 'recommend']
        negative_words = ['bad', 'terrible', 'awful', 'hate', 'worst', 'boring', 'difficult', 'hard', 'confusing', 'unclear', 'unhelpful', 'rude', 'unfair', 'poor']
        
        sentiments = []
        
        for comment in self.df['comments'].dropna():
            cleaned_comment = self.clean_text(comment)
            words = cleaned_comment.split()
            
            positive_count = sum(1 for word in words if word in positive_words)
            negative_count = sum(1 for word in words if word in negative_words)
            
            if positive_count > negative_count:
                sentiments.append('Positive')
            elif negative_count > positive_count:
                sentiments.append('Negative')
            else:
                sentiments.append('Neutral')
        
        return Counter(sentiments)
    
    def generate_insights(self):
        """Generate comprehensive insights from the data"""
        insights = {}
        
        # Basic statistics
        insights['total_reviews'] = len(self.df)
        insights['avg_rating'] = self.df['star_rating'].mean()
        insights['avg_difficulty'] = self.df['diff_index'].mean()
        
        # Theme analysis
        insights['top_themes'] = self.extract_themes()
        
        # Category analysis
        insights['category_distribution'] = self.categorize_feedback()
        
        # Sentiment analysis
        insights['sentiment_distribution'] = self.sentiment_analysis_simple()
        
        # Rating distribution
        insights['rating_distribution'] = self.df['star_rating'].value_counts().to_dict()
        
        return insights
    
    def save_processed_data(self, output_path):
        """Save processed data for use in the main application"""
        insights = self.generate_insights()
        
        # Save insights as JSON-like format
        processed_data = {
            'summary_stats': {
                'total_reviews': insights['total_reviews'],
                'avg_rating': round(insights['avg_rating'], 2),
                'avg_difficulty': round(insights['avg_difficulty'], 2)
            },
            'top_themes': insights['top_themes'][:10],
            'category_distribution': insights['category_distribution'],
            'sentiment_distribution': dict(insights['sentiment_distribution']),
            'rating_distribution': insights['rating_distribution']
        }
        
        # Save to CSV for easy loading in Streamlit
        themes_df = pd.DataFrame(insights['top_themes'], columns=['Theme', 'Count'])
        themes_df.to_csv(f"{output_path}_themes.csv", index=False)
        
        categories_df = pd.DataFrame(list(insights['category_distribution'].items()), 
                                   columns=['Category', 'Count'])
        categories_df.to_csv(f"{output_path}_categories.csv", index=False)
        
        sentiment_df = pd.DataFrame(list(insights['sentiment_distribution'].items()), 
                                  columns=['Sentiment', 'Count'])
        sentiment_df.to_csv(f"{output_path}_sentiment.csv", index=False)
        
        return processed_data

if __name__ == "__main__":
    # Initialize analyzer
    analyzer = FeedbackAnalyzer('/home/ubuntu/RMP_sample_data.csv')
    
    # Generate and save insights
    print("Processing RateMyProfessor dataset...")
    insights = analyzer.generate_insights()
    
    print(f"Total reviews analyzed: {insights['total_reviews']}")
    print(f"Average rating: {insights['avg_rating']:.2f}")
    print(f"Average difficulty: {insights['avg_difficulty']:.2f}")
    
    print("\nTop 10 themes:")
    for theme, count in insights['top_themes'][:10]:
        print(f"  {theme}: {count}")
    
    print("\nCategory distribution:")
    for category, count in insights['category_distribution'].items():
        print(f"  {category}: {count}")
    
    print("\nSentiment distribution:")
    for sentiment, count in insights['sentiment_distribution'].items():
        print(f"  {sentiment}: {count}")
    
    # Save processed data
    processed_data = analyzer.save_processed_data('/home/ubuntu/processed_data')
    print("\nProcessed data saved to CSV files for visualization module.")

