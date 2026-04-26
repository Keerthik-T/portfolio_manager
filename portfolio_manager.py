"""
Quantamental Portfolio Manager Engine
Optimizes holdings based on target profit %, yfinance volatility, and NLP sentiment.
"""
import logging
import yfinance as yf
import numpy as np
from database import db
from models import PortfolioItem
from sentiment_analyzer import SentimentAnalyzer

logger = logging.getLogger(__name__)

class PortfolioManager:
    def __init__(self):
        self.sentiment_analyzer = SentimentAnalyzer()

    def get_stock_data(self, symbol: str) -> dict:
        """Fetch current price, history, and calculate volatility via yfinance."""
        try:
            ticker = yf.Ticker(symbol)
            # Fetch 1 month of historical data to calculate volatility
            hist = ticker.history(period="1mo")
            
            if hist.empty:
                return None
            
            current_price = float(hist['Close'].iloc[-1])
            
            # Calculate daily returns
            daily_returns = hist['Close'].pct_change().dropna()
            
            # Annualized volatility (standard deviation of daily returns * sqrt(252 trading days))
            # Or simpler: max daily volatility % over the last month for the threshold check
            volatility_pct = float(daily_returns.std() * 100 * np.sqrt(252))
            
            # Let's also grab a 52-week high/low or just rely on entry price
            info = ticker.info
            name = info.get('longName', info.get('shortName', symbol))
            
            return {
                'symbol': symbol,
                'name': name,
                'current_price': current_price,
                'volatility': volatility_pct
            }
        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {e}")
            return None

    def add_or_update_holding(self, symbol: str, shares: float, avg_price: float, target_profit_pct: float = 15.0, volatility_threshold: float = 30.0, target_entry: float = None) -> bool:
        """Add a new holding or update an existing one in the SQLite database."""
        symbol = symbol.upper().strip()
        item = PortfolioItem.query.filter_by(symbol=symbol).first()
        
        if item:
            # Update existing
            total_shares = item.shares + shares
            if total_shares > 0:
                # Weighted average price
                item.avg_price = ((item.shares * item.avg_price) + (shares * avg_price)) / total_shares
                item.shares = total_shares
            item.target_profit_pct = target_profit_pct
            item.volatility_threshold = volatility_threshold
            if target_entry:
                item.target_entry = target_entry
        else:
            # Create new
            item = PortfolioItem(
                symbol=symbol,
                shares=shares,
                avg_price=avg_price,
                target_profit_pct=target_profit_pct,
                volatility_threshold=volatility_threshold,
                target_entry=target_entry
            )
            db.session.add(item)
            
        try:
            db.session.commit()
            return True
        except Exception as e:
            logger.error(f"Failed to save holding {symbol}: {e}")
            db.session.rollback()
            return False

    def remove_holding(self, symbol: str, shares_to_remove: float = None) -> bool:
        symbol = symbol.upper().strip()
        item = PortfolioItem.query.filter_by(symbol=symbol).first()
        
        if not item:
            return False
            
        if shares_to_remove is None or shares_to_remove >= item.shares:
            db.session.delete(item)
        else:
            item.shares -= shares_to_remove
            
        try:
            db.session.commit()
            return True
        except Exception as e:
            logger.error(f"Failed to remove holding {symbol}: {e}")
            db.session.rollback()
            return False

    def evaluate_holding(self, item: PortfolioItem, stock_data: dict, sentiment_score: float) -> dict:
        """Apply Quantamental logic to determine the suggested action."""
        current_price = stock_data['current_price']
        volatility = stock_data['volatility']
        
        profit_loss_pct = ((current_price - item.avg_price) / item.avg_price * 100) if item.avg_price > 0 else 0
        
        action = "HOLD"
        reason = "Metrics within normal bounds."

        # Rule 1: Take Profit Rule
        if profit_loss_pct >= item.target_profit_pct:
            action = "SELL / TAKE PROFIT"
            reason = f"Target profit of {item.target_profit_pct}% reached (+{profit_loss_pct:.2f}%)."
            
        # Rule 2: Quantamental Sell
        # If Sentiment < -0.4 AND Volatility > User_Threshold → Suggest Sell/Reduce.
        elif sentiment_score < -0.4 and volatility > item.volatility_threshold:
            action = "SELL / REDUCE"
            reason = f"High risk detected: Sentiment is very negative ({sentiment_score:.2f}) and volatility ({volatility:.2f}%) exceeds threshold ({item.volatility_threshold}%)."

        # Rule 3: Quantamental Buy
        # If Sentiment > 0.4 AND Price < Target_Entry → Suggest Buy/Increase.
        elif sentiment_score > 0.4 and item.target_entry and current_price < item.target_entry:
            action = "BUY / INCREASE"
            reason = f"Bullish signal: Sentiment is positive ({sentiment_score:.2f}) and price (${current_price:.2f}) is below target entry (${item.target_entry:.2f})."
            
        return {
            'action': action,
            'reason': reason,
            'profit_loss_pct': profit_loss_pct,
            'current_value': current_price * item.shares
        }

    def get_portfolio_dashboard(self) -> dict:
        """Generate the full dashboard state."""
        items = PortfolioItem.query.all()
        
        holdings = []
        total_value = 0.0
        total_cost = 0.0
        
        for item in items:
            stock_data = self.get_stock_data(item.symbol)
            if not stock_data:
                continue
                
            sentiment_score = self.sentiment_analyzer.get_sentiment(item.symbol)
            eval_data = self.evaluate_holding(item, stock_data, sentiment_score)
            
            cost_basis = item.avg_price * item.shares
            current_value = eval_data['current_value']
            
            total_value += current_value
            total_cost += cost_basis
            
            holdings.append({
                'symbol': item.symbol,
                'name': stock_data['name'],
                'shares': item.shares,
                'avg_price': item.avg_price,
                'current_price': stock_data['current_price'],
                'current_value': current_value,
                'profit_loss_pct': eval_data['profit_loss_pct'],
                'profit_loss_usd': current_value - cost_basis,
                'volatility': stock_data['volatility'],
                'sentiment_score': sentiment_score,
                'suggested_action': eval_data['action'],
                'action_reason': eval_data['reason'],
                'target_profit_pct': item.target_profit_pct,
                'target_entry': item.target_entry,
                'volatility_threshold': item.volatility_threshold
            })
            
        return {
            'total_value': total_value,
            'total_cost': total_cost,
            'total_gain_loss': total_value - total_cost,
            'total_gain_loss_pct': ((total_value - total_cost) / total_cost * 100) if total_cost > 0 else 0,
            'holdings': holdings
        }
