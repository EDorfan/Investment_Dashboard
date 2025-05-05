import os
import sys
# Add the project root directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.models import get_all_transactions
from app.extensions import mysql
import yfinance as yf
from datetime import datetime, timedelta
import logging

# Set up logging
logging.basicConfig(
    filename='portfolio_updater.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def verify_updates():
    """Verify the most recent updates in the database"""
    try:
        app = create_app()
        with app.app_context():
            cursor = mysql.connection.cursor()
            # Get the most recent update for each ticker
            cursor.execute("""
                SELECT ticker, price, timestamp 
                FROM stock_prices 
                WHERE timestamp >= DATE_SUB(NOW(), INTERVAL 1 HOUR)
                ORDER BY timestamp DESC
            """)
            recent_updates = cursor.fetchall()
            cursor.close()
            
            if recent_updates:
                print("\nRecent Price Updates:")
                print("Ticker | Price | Timestamp")
                print("-" * 40)
                for update in recent_updates:
                    print(f"{update[0]:6} | ${update[1]:6.2f} | {update[2]}")
            else:
                print("No updates found in the last hour")
                
    except Exception as e:
        print(f"Error verifying updates: {str(e)}")

def update_stock_prices():
    try:
        app = create_app()
        with app.app_context():
            # Get all unique tickers from transactions
            cursor = mysql.connection.cursor()
            cursor.execute("SELECT DISTINCT ticker FROM transactions")
            tickers = cursor.fetchall()
            cursor.close()

            # Get current timestamp
            now = datetime.now()
            timestamp = now.strftime('%Y-%m-%d %H:%M:%S')

            for ticker_data in tickers:
                ticker = ticker_data[0]
                try:
                    # Get stock data
                    stock = yf.Ticker(ticker)
                    # Get current price
                    current_price = stock.info.get('regularMarketPrice')
                    
                    if current_price:
                        # Store the price
                        cursor = mysql.connection.cursor()
                        cursor.execute("""
                            INSERT INTO stock_prices (ticker, price, timestamp)
                            VALUES (%s, %s, %s)
                            ON DUPLICATE KEY UPDATE price = %s
                        """, (ticker, current_price, timestamp, current_price))
                        mysql.connection.commit()
                        cursor.close()
                        
                        logging.info(f"Updated {ticker} price: ${current_price:.2f} at {timestamp}")
                    else:
                        logging.warning(f"Could not get current price for {ticker}")
                except Exception as e:
                    logging.error(f"Error fetching data for {ticker}: {str(e)}")
                    continue

    except Exception as e:
        logging.error(f"Error in update_stock_prices: {str(e)}")

if __name__ == "__main__":
    update_stock_prices()
    verify_updates()  # Add verification after update 