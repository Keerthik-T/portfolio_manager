from database import db
from datetime import datetime

class PortfolioItem(db.Model):
    __tablename__ = 'portfolio_items'
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(10), unique=True, nullable=False)
    shares = db.Column(db.Float, default=0.0)
    avg_price = db.Column(db.Float, default=0.0)
    target_profit_pct = db.Column(db.Float, default=15.0)  # Default 15%
    target_entry = db.Column(db.Float, nullable=True)
    volatility_threshold = db.Column(db.Float, default=5.0) # Default max daily volatility %
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class SentimentCache(db.Model):
    __tablename__ = 'sentiment_cache'
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(10), unique=True, nullable=False)
    score = db.Column(db.Float, nullable=False)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
