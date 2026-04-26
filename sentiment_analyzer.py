"""
Sentiment Analyzer using DistilBERT and yfinance news.
Features SQLite caching via SQLAlchemy.
"""
import logging
from transformers import pipeline
import yfinance as yf
from datetime import datetime, timedelta
from database import db
from models import SentimentCache
from flask import current_app

logger = logging.getLogger(__name__)

class SentimentAnalyzer:
    def __init__(self):
        # Force CPU inference for stability and speed on 5600G (device=-1)
        self.analyzer = pipeline(
            "sentiment-analysis", 
            model="distilbert-base-uncased-finetuned-sst-2-english", 
            device=-1
        )
        logger.info("DistilBERT Sentiment Analyzer initialized (CPU).")

    def _fetch_yfinance_news(self, symbol: str) -> list:
        try:
            ticker = yf.Ticker(symbol)
            news = ticker.news
            if not news:
                return []
            
            texts = []
            for item in news:
                title = item.get('title', '')
                publisher = item.get('publisher', '')
                texts.append(f"{title} ({publisher})")
            return texts
        except Exception as e:
            logger.error(f"Error fetching news for {symbol}: {e}")
            return []

    def get_sentiment(self, symbol: str) -> float:
        """
        Calculates sentiment score for a symbol. Uses database cache if recent (under 4 hours).
        Returns a score between -1.0 (Very Negative) and 1.0 (Very Positive).
        """
        symbol = symbol.upper().strip()
        
        # Check SQLite Cache via SQLAlchemy
        cached = SentimentCache.query.filter_by(symbol=symbol).first()
        if cached:
            # If cache is less than 4 hours old, return it
            if datetime.utcnow() - cached.last_updated < timedelta(hours=4):
                return cached.score

        # Fetch fresh news
        news_texts = self._fetch_yfinance_news(symbol)
        
        if not news_texts:
            # Neutral if no news found
            score = 0.0
        else:
            scores = []
            for text in news_texts:
                try:
                    result = self.analyzer(text[:512])[0] # Truncate to 512 tokens max
                    label = result['label']
                    conf = result['score']
                    
                    if label == 'POSITIVE':
                        scores.append(conf)
                    elif label == 'NEGATIVE':
                        scores.append(-conf)
                    else:
                        scores.append(0.0)
                except Exception as e:
                    logger.warning(f"Failed to analyze text: {text} - {e}")
                    
            if scores:
                score = sum(scores) / len(scores)
            else:
                score = 0.0

        # Update or Insert Cache
        if cached:
            cached.score = score
        else:
            new_cache = SentimentCache(symbol=symbol, score=score)
            db.session.add(new_cache)
            
        try:
            db.session.commit()
        except Exception as e:
            logger.error(f"Failed to save sentiment cache: {e}")
            db.session.rollback()

        return float(score)
