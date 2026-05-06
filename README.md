# 📊 Quantamental AI Portfolio Manager

A professional-grade financial portfolio manager that optimizes your holdings using a blend of quantitative metrics (volatility, target entries) and AI-powered sentiment intelligence.

## ✨ Features
- **Real-time Tracking**: Live price updates via Yahoo Finance.
- **Quantamental Engine**: Balances Target Profit %, Risk Score (Volatility), and NLP Sentiment.
- **AI Sentiment Intelligence**: Uses `distilbert-base-uncased-finetuned-sst-2-english` to analyze live news.
- **Hardware Safe**: Forced CPU inference for compatibility on standard integrated graphics or server CPUs.
- **Modern UI**: Clean, responsive dashboard built with modern CSS, Inter typography, and Chart.js.
- **Persistence**: Transactions and portfolio state managed efficiently using a local SQLite database (`Flask-SQLAlchemy`).
- **Production Ready**: Native serving via `Waitress` WSGI server and automated data polling via `APScheduler`.

## 📂 Project Structure
- `app.py`: Unified Flask API and Waitress production server. Serves the UI directly.
- `portfolio_manager.py`: Quantamental logic engine and portfolio tracking.
- `sentiment_analyzer.py`: HuggingFace NLP pipeline and SQLite caching layer.
- `database.py` & `models.py`: SQLAlchemy database configuration.
- `index.html` & `script.js`: Frontend dashboard and Chart.js integration.
- `requirements.txt`: Project dependencies.
- `Dockerfile` & `.dockerignore`: For containerized deployment.

## 🚀 Quick Start (Local Setup)

### 1. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 2. Run the Application
Start the production server:
```powershell
python app.py
```
Open your browser and navigate to **[http://localhost:5000](http://localhost:5000)** to view your dashboard!

---

## 🐳 Quick Start (Docker)

If you prefer to run the application in a container without installing Python dependencies on your host machine, you can use Docker. The provided Dockerfile is optimized to pre-download the AI models during the build phase for lightning-fast container startup.

### 1. Build the Docker Image
Run this command in the project directory:
```powershell
docker build -t quantamental-portfolio .
```
*(Note: Building the image may take a few minutes as it downloads PyTorch and the HuggingFace AI models.)*

### 2. Run the Container
Spin up the application and map port 5000:
```powershell
docker run -p 5000:5000 quantamental-portfolio
```

**Persistent Database (Optional):** If you want your portfolio database to survive container restarts, you can mount a local volume:
```powershell
docker run -p 5000:5000 -v ${PWD}/portfolio.db:/app/portfolio.db quantamental-portfolio
```

Once running, navigate to **[http://localhost:5000](http://localhost:5000)** in your browser!

## 🛠️ Requirements
- Python 3.10+ (If running locally)
- Docker (If running containerized)
- Internet connection (for live `yfinance` data and initial AI model download)
