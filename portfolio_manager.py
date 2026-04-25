"""
Portfolio Manager for Stock Tracking
"""
import yfinance as yf
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import warnings
warnings.filterwarnings("ignore")

class PortfolioManager:
    def __init__(self):
        self.portfolio: Dict[str, Dict[str, Any]] = {}
        self.transactions: List[Dict[str, Any]] = []
        print("✓ Portfolio manager ready")
    
    def add_stock(self, symbol: str, shares: float, purchase_price: Optional[float] = None) -> bool:
        """Add stock to portfolio"""
        symbol = symbol.upper().strip()
        
        if purchase_price is None:
            stock_data = self.get_stock_data(symbol)
            purchase_price = stock_data['current_price'] if stock_data else 0.0
        
        shares = float(shares)
        purchase_price = float(purchase_price)
        
        if symbol in self.portfolio:
            current = self.portfolio[symbol]
            total_shares = current['shares'] + shares
            total_cost = (current['shares'] * current['avg_price']) + (shares * purchase_price)
            new_avg = total_cost / total_shares if total_shares > 0 else 0
            
            self.portfolio[symbol] = {
                'shares': total_shares,
                'avg_price': new_avg
            }
        else:
            self.portfolio[symbol] = {
                'shares': shares,
                'avg_price': purchase_price
            }
        
        # Record transaction
        self.transactions.insert(0, {
            'symbol': symbol,
            'shares': shares,
            'price': purchase_price,
            'type': 'BUY',
            'date': datetime.now().isoformat(),
            'total': shares * purchase_price
        })
        
        self.transactions = self.transactions[:50]
        return True
    
    def remove_stock(self, symbol: str, shares: float, sell_price: Optional[float] = None) -> bool:
        """Remove stock from portfolio"""
        symbol = symbol.upper().strip()
        
        if symbol not in self.portfolio:
            return False
        
        if sell_price is None:
            stock_data = self.get_stock_data(symbol)
            sell_price = stock_data['current_price'] if stock_data else 0.0
        
        current_shares = self.portfolio[symbol]['shares']
        
        if shares >= current_shares:
            del self.portfolio[symbol]
        else:
            self.portfolio[symbol]['shares'] = current_shares - shares
        
        self.transactions.insert(0, {
            'symbol': symbol,
            'shares': shares,
            'price': sell_price,
            'type': 'SELL',
            'date': datetime.now().isoformat(),
            'total': shares * sell_price
        })
        
        return True
    
    def get_stock_data(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Fetch real-time stock data"""
        symbol = symbol.upper().strip()
        
        try:
            stock = yf.Ticker(symbol)
            hist = stock.history(period="5d")
            
            if hist.empty:
                return None
            
            current = float(hist['Close'].iloc[-1])
            prev = float(hist['Close'].iloc[-2]) if len(hist) > 1 else current
            
            info = stock.info
            name = info.get('longName', info.get('shortName', symbol))
            
            hist_30 = stock.history(period="1mo")
            prices = hist_30['Close'].tolist() if not hist_30.empty else [current]
            dates = hist_30.index.strftime('%Y-%m-%d').tolist() if not hist_30.empty else [datetime.now().strftime('%Y-%m-%d')]
            
            return {
                'symbol': symbol,
                'name': name,
                'current_price': current,
                'change': current - prev,
                'change_percent': ((current - prev) / prev) * 100 if prev != 0 else 0,
                'historical_prices': [float(p) for p in prices],
                'dates': dates
            }
        except Exception as e:
            print(f"⚠️ Error fetching {symbol}: {e}")
            return None
    
    def get_portfolio_value(self) -> Dict[str, Any]:
        """Calculate portfolio value"""
        total = 0.0
        total_cost = 0.0
        holdings = []
        
        for symbol, data in self.portfolio.items():
            stock = self.get_stock_data(symbol)
            if stock:
                value = stock['current_price'] * data['shares']
                cost = data['avg_price'] * data['shares']
                total += value
                total_cost += cost
                
                holdings.append({
                    'symbol': symbol,
                    'name': stock['name'],
                    'shares': data['shares'],
                    'avg_price': data['avg_price'],
                    'current_price': stock['current_price'],
                    'current_value': value,
                    'gain_loss': value - cost,
                    'gain_loss_percent': ((value - cost) / cost) * 100 if cost > 0 else 0
                })
        
        holdings.sort(key=lambda x: x['current_value'], reverse=True)
        
        return {
            'total_value': total,
            'total_cost': total_cost,
            'total_gain_loss': total - total_cost,
            'total_gain_loss_percent': ((total - total_cost) / total_cost) * 100 if total_cost > 0 else 0,
            'holdings': holdings,
            'holdings_count': len(holdings),
            'transactions': self.transactions[:10]
        }

print("✅ portfolio_manager.py created successfully")
