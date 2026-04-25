"""
Financial Portfolio Tracker API
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
from portfolio_manager import PortfolioManager
from sentiment_analyzer import SentimentAnalyzer
from datetime import datetime
import traceback

app = Flask(__name__)
CORS(app)

portfolio = PortfolioManager()
sentiment = SentimentAnalyzer()

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'portfolio_size': len(portfolio.portfolio)
    })

@app.route('/api/portfolio', methods=['GET'])
def get_portfolio():
    try:
        return jsonify(portfolio.get_portfolio_value())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/portfolio/add', methods=['POST'])
def add_stock():
    try:
        data = request.get_json()
        symbol = data.get('symbol', '').upper()
        shares = float(data.get('shares', 0))
        price = data.get('purchase_price')
        
        if not symbol or shares <= 0:
            return jsonify({'error': 'Valid symbol and shares required'}), 400
        
        if price:
            price = float(price)
        
        portfolio.add_stock(symbol, shares, price)
        
        return jsonify({
            'success': True,
            'message': f'Added {shares} shares of {symbol}'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/portfolio/remove', methods=['POST'])
def remove_stock():
    try:
        data = request.get_json()
        symbol = data.get('symbol', '').upper()
        shares = float(data.get('shares', 0))
        
        if not symbol or shares <= 0:
            return jsonify({'error': 'Valid symbol and shares required'}), 400
        
        success = portfolio.remove_stock(symbol, shares)
        
        if success:
            return jsonify({'success': True, 'message': f'Removed {shares} shares of {symbol}'})
        return jsonify({'error': 'Stock not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stock/<symbol>', methods=['GET'])
def get_stock(symbol):
    try:
        data = portfolio.get_stock_data(symbol.upper())
        if data:
            return jsonify(data)
        return jsonify({'error': 'Stock not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/sentiment/<symbol>', methods=['GET'])
def get_sentiment(symbol):
    try:
        result = sentiment.get_combined_sentiment(symbol.upper())
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/dashboard', methods=['GET'])
def dashboard():
    try:
        portfolio_data = portfolio.get_portfolio_value()
        sentiments = {}
        
        for holding in portfolio_data['holdings']:
            try:
                sentiments[holding['symbol']] = sentiment.get_combined_sentiment(holding['symbol'])
            except:
                sentiments[holding['symbol']] = {'overall_sentiment': 'NEUTRAL', 'overall_score': 0}
        
        return jsonify({
            'portfolio': portfolio_data,
            'sentiments': sentiments,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 Financial Portfolio Tracker API")
    print("="*60)
    print(f"📍 Server: http://localhost:5000")
    print(f"🔍 Health: http://localhost:5000/api/health")
    print("="*60 + "\n")
    app.run(debug=True, host='0.0.0.0', port=5000)

print("✅ app.py created successfully")
