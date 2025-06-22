import pandas as pd
import numpy as np
import re
from collections import Counter
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

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

class TextAnalyzer:
    def __init__(self):
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
    
    def extract_themes(self, texts, top_n=20):
        """Extract common themes from text data"""
        # Clean all texts
        cleaned_texts = [self.clean_text(text) for text in texts if pd.notna(text)]
        
        # Combine all text
        all_text = ' '.join(cleaned_texts)
        
        # Get word frequency
        words = all_text.split()
        word_freq = Counter(words)
        
        return word_freq.most_common(top_n)
    
    def categorize_feedback(self, texts):
        """Categorize feedback into predefined categories"""
        categories = {
            'Academic Issues': ['grade', 'grading', 'exam', 'test', 'assignment', 'homework', 'difficult', 'hard', 'easy', 'content', 'material', 'lecture', 'teaching', 'explain', 'understand', 'professor', 'teacher', 'class', 'course'],
            'Administrative Issues': ['registration', 'enroll', 'schedule', 'office', 'hour', 'response', 'email', 'communication', 'policy', 'requirement', 'staff', 'service', 'process'],
            'Facilities': ['classroom', 'room', 'building', 'equipment', 'technology', 'computer', 'projector', 'space', 'environment', 'library', 'lab', 'facility'],
            'Student Welfare': ['help', 'support', 'care', 'concern', 'stress', 'mental', 'health', 'safety', 'harassment', 'discrimination', 'welfare', 'counseling']
        }
        
        # Initialize category counts
        category_counts = {cat: 0 for cat in categories.keys()}
        
        # Analyze each text
        for text in texts:
            if pd.notna(text):
                cleaned_text = self.clean_text(text)
                text_words = cleaned_text.split()
                
                for category, keywords in categories.items():
                    if any(keyword in text_words for keyword in keywords):
                        category_counts[category] += 1
        
        return category_counts
    
    def sentiment_analysis_simple(self, texts):
        """Simple sentiment analysis based on positive/negative words"""
        positive_words = ['good', 'great', 'excellent', 'amazing', 'awesome', 'love', 'best', 'fantastic', 'wonderful', 'helpful', 'easy', 'clear', 'interesting', 'fun', 'recommend', 'satisfied', 'happy', 'pleased']
        negative_words = ['bad', 'terrible', 'awful', 'hate', 'worst', 'boring', 'difficult', 'hard', 'confusing', 'unclear', 'unhelpful', 'rude', 'unfair', 'poor', 'disappointed', 'frustrated', 'angry']
        
        sentiments = []
        
        for text in texts:
            if pd.notna(text):
                cleaned_text = self.clean_text(text)
                words = cleaned_text.split()
                
                positive_count = sum(1 for word in words if word in positive_words)
                negative_count = sum(1 for word in words if word in negative_words)
                
                if positive_count > negative_count:
                    sentiments.append('Positive')
                elif negative_count > positive_count:
                    sentiments.append('Negative')
                else:
                    sentiments.append('Neutral')
            else:
                sentiments.append('Neutral')
        
        return Counter(sentiments)
    
    def analyze_feedback_data(self, df, text_column='feedback_text'):
        """Comprehensive analysis of feedback data"""
        if df.empty or text_column not in df.columns:
            return {}
        
        texts = df[text_column].tolist()
        
        analysis_results = {
            'total_feedback': len(df),
            'themes': self.extract_themes(texts),
            'categories': self.categorize_feedback(texts),
            'sentiment': self.sentiment_analysis_simple(texts),
            'category_distribution': df['category'].value_counts().to_dict() if 'category' in df.columns else {},
            'priority_distribution': df['priority'].value_counts().to_dict() if 'priority' in df.columns else {},
            'status_distribution': df['status'].value_counts().to_dict() if 'status' in df.columns else {}
        }
        
        return analysis_results

if __name__ == '__main__':
    # Example usage
    analyzer = TextAnalyzer()
    
    # Test with sample data
    sample_texts = [
        "The professor's grading is unfair and unclear",
        "Great class, very helpful teacher",
        "The classroom equipment is outdated",
        "Need better mental health support services"
    ]
    
    themes = analyzer.extract_themes(sample_texts)
    categories = analyzer.categorize_feedback(sample_texts)
    sentiment = analyzer.sentiment_analysis_simple(sample_texts)
    
    print("Themes:", themes)
    print("Categories:", categories)
    print("Sentiment:", sentiment)

