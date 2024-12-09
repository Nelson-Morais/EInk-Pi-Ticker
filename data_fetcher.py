import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class StockStats:
    current_price: float
    day_high: float
    day_low: float

class DataFetcher:
    def __init__(self):
        self.cache = {}
        self.cache_timestamp = {}

    def get_stock_data(self, symbol: str) -> StockStats:
        """Fetch current price and daily stats for the given symbol."""
        try:
            # Try to get data from cache first
            if symbol in self.cache and (datetime.now() - self.cache_timestamp.get(symbol, datetime.min)).seconds < 60:
                return self.cache[symbol]

            # Get the daily data
            # For crypto (symbols ending in -USD), we get data from midnight
            is_crypto = symbol.endswith('-USD')
            if is_crypto:
                # Get data since midnight of current day
                today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                df = yf.download(symbol, start=today, interval='1m', progress=False)
            else:
                # For stocks, use regular 1d period
                df = yf.download(symbol, period='1d', interval='1m', progress=False)

            if df.empty:
                raise ValueError(f"No data available for {symbol}")
            
            stats = StockStats(
                current_price=float(df['Close'].iloc[-1]),
                day_high=float(df['High'].max()),
                day_low=float(df['Low'].min())
            )
            
            # Update cache
            self.cache[symbol] = stats
            self.cache_timestamp[symbol] = datetime.now()
            
            return stats
        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {str(e)}")
            # If we have cached data, return it as fallback
            if symbol in self.cache:
                logger.info(f"Using cached data for {symbol}")
                return self.cache[symbol]
            raise

    def get_historical_data(self, symbol: str) -> pd.DataFrame:
        """Fetch last 24h of price data for the given symbol."""
        try:
            # Get 1-day data with 1-minute intervals
            df = yf.download(symbol, period='1d', interval='1m', progress=False)
            
            if df.empty:
                raise ValueError(f"No historical data available for {symbol}")
            
            return df[['Close']]
        except Exception as e:
            logger.error(f"Error fetching historical data for {symbol}: {str(e)}")
            raise
