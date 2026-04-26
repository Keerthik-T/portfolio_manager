"""
Main Flask Application for Quantamental AI Portfolio Manager.
Uses Waitress for production serving and APScheduler for automated fetching.
"""
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
from database import db
from models import PortfolioItem, SentimentCache
from portfolio_manager import PortfolioManager
from apscheduler.schedulers.background import BackgroundScheduler
from waitress import serve
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Configure SQLite Database
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'portfolio.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Initialize Engine (Must be done after db.init_app, inside app context)
with app.app_context():
    db.create_all()
    manager = PortfolioManager()

# Background Task
def refresh_sentiment_cache():
    """Background job to refresh sentiment cache every 4 hours."""
    with app.app_context():
        logger.info("Running scheduled sentiment cache refresh...")
        items = PortfolioItem.query.all()
        for item in items:
            logger.info(f"Refreshing sentiment for {item.symbol}...")
            # Calling get_sentiment will fetch new data if cache is older than 4 hrs
            manager.sentiment_analyzer.get_sentiment(item.symbol)
        logger.info("Scheduled refresh complete.")

# Setup Scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(func=refresh_sentiment_cache, trigger="interval", hours=4)
scheduler.start()


@app.route('/api/dashboard', methods=['GET'])
def get_dashboard():
    try:
        data = manager.get_portfolio_dashboard()
        return jsonify(data)
    except Exception as e:
        logger.error(f"Dashboard error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/portfolio/add', methods=['POST'])
def add_stock():
    try:
        data = request.json
        symbol = data.get('symbol')
        shares = float(data.get('shares', 0))
        avg_price = float(data.get('avg_price', 0))
        target_profit_pct = float(data.get('target_profit_pct', 15.0))
        volatility_threshold = float(data.get('volatility_threshold', 5.0))
        target_entry = data.get('target_entry')
        if target_entry:
            target_entry = float(target_entry)
            
        if not symbol or shares <= 0:
            return jsonify({'error': 'Invalid symbol or shares'}), 400
            
        success = manager.add_or_update_holding(
            symbol=symbol, 
            shares=shares, 
            avg_price=avg_price, 
            target_profit_pct=target_profit_pct, 
            volatility_threshold=volatility_threshold,
            target_entry=target_entry
        )
        
        if success:
            return jsonify({'success': True, 'message': f'Added/Updated {symbol}'})
        return jsonify({'error': 'Failed to save to database'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/portfolio/remove', methods=['POST'])
def remove_stock():
    try:
        data = request.json
        symbol = data.get('symbol')
        shares = data.get('shares') # Optional
        if shares:
            shares = float(shares)
            
        success = manager.remove_holding(symbol, shares)
        if success:
            return jsonify({'success': True})
        return jsonify({'error': 'Failed to remove or not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    logger.info("Starting Waitress Production Server on http://0.0.0.0:5000")
    # Shutdown scheduler gracefully on exit
    import atexit
    atexit.register(lambda: scheduler.shutdown())
    
    # Run with waitress for production readiness
    serve(app, host='0.0.0.0', port=5000)
