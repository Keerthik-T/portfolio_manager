# 📊 AI Financial Portfolio Tracker

A professional-grade financial portfolio manager with advanced AI-powered sentiment intelligence.

## ✨ Features
- **Real-time Tracking**: Live price updates via Yahoo Finance.
- **AI Sentiment Engine**: Multi-tier sentiment analysis (FinBERT → VADER → TextBlob).
- **Hybrid Analytics**: Combines news sentiment with technical price action.
- **Modern UI**: Clean, responsive dashboard built with modern CSS and Inter typography.
- **Persistence**: Transactions and portfolio state managed efficiently.

## 📂 Project Structure
- `app.py`: Unified Flask API entry point.
- `portfolio_manager.py`: Core logic for asset tracking and history.
- `sentiment_engine.py`: Advanced AI sentiment analysis engine.
- `index.html`: Premium frontend dashboard.
- `requirements.txt`: Project dependencies.

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Application
```bash
python app.py
```
Then open `index.html` in your browser.

## 🤖 Sentiment Engine Tiers
1. **Tier 1 (FinBERT)**: Specialized financial transformer model for highest accuracy.
2. **Tier 2 (VADER)**: Rule-based sentiment analysis for social media context.
3. **Tier 3 (TextBlob)**: General-purpose NLP for semantic fallback.

## 🛠️ Requirements
- Python 3.9+
- Internet connection (for live data and model downloads)
