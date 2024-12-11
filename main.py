import asyncio
import logging
import uvicorn
from api import app
from epaper_display import EPaperDisplay
from mock_display import MockDisplay
from data_fetcher import DataFetcher
import config
import signal
import sys
from threading import Thread
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StockDisplay:
    def __init__(self):
        try:
            self.display = EPaperDisplay()  # Use the new EPaperDisplay class
            logger.info("Using e-Paper display")
        except Exception as e:
            logger.warning(f"Failed to initialize e-Paper display: {e}")
            logger.info("Falling back to mock display. Check output directory for images.")
            self.display = MockDisplay()
        self.data_fetcher = DataFetcher()
        self.running = True
        self.last_graph_update = datetime.min
        self.current_graph_data = None
        
        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info("Shutdown signal received")
        self.running = False
        self.display.clear_display()  # Use new method name
        self.display.sleep()
        sys.exit(0)

    async def update_price_display(self):
        """Update the display with current price"""
        from api import current_symbol
        
        try:
            # Get current price and stats
            stats = self.data_fetcher.get_stock_data(current_symbol)
            
            # Check if we need to update the graph
            now = datetime.now()
            if self.current_graph_data is None or (now - self.last_graph_update).total_seconds() >= config.GRAPH_UPDATE_INTERVAL:
                self.current_graph_data = self.data_fetcher.get_historical_data(current_symbol)
                self.last_graph_update = now
                logger.info(f"Updated graph data for {current_symbol}")
            
            # Create layout and update display
            self.display.create_stock_layout(current_symbol, stats, self.current_graph_data)
            self.display.display()  # Use new display update method
            
            logger.info(f"Updated display with {current_symbol} price: {stats.current_price}")
        except Exception as e:
            logger.error(f"Error updating display: {str(e)}")

    async def display_loop(self):
        """Main loop for updating the display"""
        while self.running:
            await self.update_price_display()
            await asyncio.sleep(config.PRICE_UPDATE_INTERVAL)

def run_api():
    """Run the FastAPI server"""
    uvicorn.run(app, host=config.API_HOST, port=config.API_PORT)

async def main():
    """Main function to run both the display and API server"""
    stock_display = StockDisplay()
    
    # Start API server in a separate thread
    api_thread = Thread(target=run_api, daemon=True)
    api_thread.start()
    
    # Run display loop
    await stock_display.display_loop()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Application stopped by user")
    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        raise
