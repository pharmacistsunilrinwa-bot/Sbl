from textblob import TextBlob

class SentimentService:
    @staticmethod
    def analyze_text(text: str) -> dict:
        blob = TextBlob(text)
        sentiment = blob.sentiment
        
        # Polarity: -1 (negative) to 1 (positive)
        # Subjectivity: 0 (objective) to 1 (subjective)
        return {
            "polarity": sentiment.polarity,
            "subjectivity": sentiment.subjectivity,
            "label": "positive" if sentiment.polarity > 0 else "negative" if sentiment.polarity < 0 else "neutral"
        }

sentiment_service = SentimentService()
