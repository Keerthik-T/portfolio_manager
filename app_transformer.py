"""
Financial Portfolio Tracker with Transformer AI
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
from portfolio_manager import PortfolioManager
from transformer_sentiment import TransformerSentimentAnalyzer
import traceback
import logging
from datetime import datetime
import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Initialize managers
portfolio_manager = PortfolioManager()
sentiment_analyzer = TransformerSentimentAnalyzer()

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'model': sentiment_analyzer.model_name if sentiment_analyzer.model_loaded else 'VADER',
        'portfolio_size': len(portfolio_manager.portfolio),
        'model_loaded': sentiment_analyzer.model_loaded
    })

@app.route('/api/portfolio', methods=['GET'])
def get_portfolio():
    try:
        return jsonify(portfolio_manager.get_portfolio_value())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/portfolio/add', methods=['POST'])
def add_to_portfolio():
    try:
        data = request.get_json()
        symbol = data.get('symbol', '').upper().strip()
        shares = float(data.get('shares', 0))
        purchase_price = data.get('purchase_price')
        
        if not symbol or shares <= 0:
            return jsonify({'error': 'Valid symbol and shares required'}), 400
        
        if purchase_price:
            purchase_price = float(purchase_price)
        
        success = portfolio_manager.add_stock(symbol, shares, purchase_price)
        
        return jsonify({
            'success': success,
            'message': f'Added {shares} shares of {symbol}',
            'symbol': symbol,
            'shares': shares
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/portfolio/remove', methods=['POST'])
def remove_from_portfolio():
    try:
        data = request.get_json()
        symbol = data.get('symbol', '').upper().strip()
        shares = float(data.get('shares', 0))
        
        success = portfolio_manager.remove_stock(symbol, shares)
        
        if success:
            return jsonify({'success': True, 'message': f'Removed {shares} shares of {symbol}'})
        return jsonify({'error': 'Stock not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stock/<symbol>', methods=['GET'])
def get_stock(symbol):
    try:
        stock_data = portfolio_manager.get_stock_data(symbol.upper())
        if stock_data:
            return jsonify(stock_data)
        return jsonify({'error': 'Stock not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/sentiment/<symbol>', methods=['GET'])
def get_sentiment(symbol):
    """Get advanced sentiment using Transformer"""
    try:
        symbol = symbol.upper().strip()
        stock_data = portfolio_manager.get_stock_data(symbol)
        sentiment = sentiment_analyzer.get_combined_sentiment(symbol, stock_data)
        return jsonify(sentiment)
    except Exception as e:
        logger.error(f"Error: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/dashboard', methods=['GET'])
def get_dashboard():
    """Get complete dashboard with transformer sentiment"""
    try:
        portfolio_data = portfolio_manager.get_portfolio_value()
        sentiments = {}
        
        print(f"\n📊 Processing {len(portfolio_data['holdings'])} holdings...")
        
        for holding in portfolio_data['holdings']:
            symbol = holding['symbol']
            stock_data = portfolio_manager.get_stock_data(symbol)
            sentiments[symbol] = sentiment_analyzer.get_combined_sentiment(symbol, stock_data)
        
        summary = portfolio_manager.get_portfolio_summary()
        
        return jsonify({
            'portfolio': portfolio_data,
            'sentiments': sentiments,
            'summary': summary,
            'timestamp': datetime.now().isoformat(),
            'ai_model': sentiment_analyzer.model_name if sentiment_analyzer.model_loaded else 'VADER'
        })
    except Exception as e:
        logger.error(f"Error: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/analyze/text', methods=['POST'])
def analyze_text():
    """Analyze custom text with Transformer"""
    try:
        data = request.get_json()
        text = data.get('text', '')
        if not text:
            return jsonify({'error': 'Text required'}), 400
        analysis = sentiment_analyzer.analyze_financial_text(text)
        return jsonify(analysis)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/clear_cache', methods=['POST'])
def clear_cache():
    """Clear sentiment cache"""
    sentiment_analyzer.sentiment_cache = {}
    sentiment_analyzer.save_cache()
    return jsonify({'message': 'Cache cleared'})

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 Portfolio Tracker with Transformer AI")
    print("="*60)
    print(f"✓ Model: {sentiment_analyzer.model_name if sentiment_analyzer.model_loaded else 'VADER'}")
    print(f"✓ Server: http://localhost:5000")
    print("="*60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)
