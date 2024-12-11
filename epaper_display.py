import logging
import time
from PIL import Image, ImageDraw, ImageFont
import matplotlib.pyplot as plt
import io
import sys
import os

# Override the epdconfig implementation before importing waveshare_epd
import epdconfig_override
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "venv/lib/python3.11/site-packages/waveshare_epd"))
sys.modules['waveshare_epd.epdconfig'] = epdconfig_override

from waveshare_epd import epd2in13_V2

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EPaperDisplay:
    """
    A class to handle the e-Paper display operations using the Waveshare library.
    This implementation follows the Waveshare example code structure more closely.
    """
    def __init__(self):
        # Initialize the display
        self.epd = epd2in13_V2.EPD()
        self.init_display()
        
        # The display dimensions (note: rotated 90° in our setup)
        self.width = self.epd.height  
        self.height = self.epd.width
        
        # Create initial image buffer
        self.image = Image.new('1', (self.width, self.height), 255)
        self.draw = ImageDraw.Draw(self.image)
        
        # Load fonts
        try:
            self.price_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
            self.symbol_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
        except OSError:
            logger.warning("Custom fonts not found, using default font")
            self.price_font = ImageFont.load_default()
            self.symbol_font = ImageFont.load_default()

    def init_display(self):
        """Initialize the e-Paper display with proper error handling"""
        try:
            self.epd.init(self.epd.FULL_UPDATE)
            self.clear_display()  # Start with a clean display
            logger.info("E-Paper display initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize display: {str(e)}")
            raise

    def clear_display(self):
        """Clear the display to white"""
        try:
            self.epd.Clear(0xFF)  # 0xFF = white
            logger.info("Display cleared")
        except Exception as e:
            logger.error(f"Failed to clear display: {str(e)}")
            raise

    def create_stock_layout(self, symbol: str, stats, graph_data=None):
        """Create the stock display layout"""
        # Clear the image buffer
        self.draw.rectangle((0, 0, self.width, self.height), fill=255)
        
        # Draw symbol at top left
        self.draw.text((5, 5), symbol, font=self.symbol_font, fill=0)

        # Draw current price below symbol
        price_text = f"${stats.current_price:.2f}" if stats.current_price < 1000 else f"${stats.current_price:,.0f}"
        self.draw.text((5, 30), price_text, font=self.price_font, fill=0)

        # Draw high/low stats on top right
        stats_x = self.width - 80
        self.draw.text((stats_x, 5), f"H: ${stats.day_high:.2f}", font=self.symbol_font, fill=0)
        self.draw.text((stats_x, 20), f"L: ${stats.day_low:.2f}", font=self.symbol_font, fill=0)

        # Add graph if data is provided
        if graph_data is not None:
            graph_image = self._create_graph(graph_data)
            self.image.paste(graph_image, (0, 60))

    def _create_graph(self, data):
        """Create a price history graph"""
        # Set up the plot
        fig, ax = plt.subplots(figsize=(2.5, 0.6), dpi=100)
        fig.patch.set_alpha(0)
        ax.patch.set_alpha(0)

        # Plot the line
        ax.plot(data.index, data['Close'], color='black', linewidth=1)
        ax.axis('off')

        # Convert to image
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0)
        plt.close()
        buf.seek(0)
        
        # Convert to binary image
        graph = Image.open(buf).convert('L')
        graph = graph.point(lambda x: 0 if x < 128 else 255, '1')
        
        return graph

    def display(self):
        """Update the physical display with current image buffer"""
        try:
            self.epd.display(self.epd.getbuffer(self.image))
            logger.info("Display updated successfully")
        except Exception as e:
            logger.error(f"Failed to update display: {str(e)}")
            raise

    def partial_update(self):
        """Perform a partial update of the display"""
        try:
            self.epd.displayPartial(self.epd.getbuffer(self.image))
            logger.info("Partial display update completed")
        except Exception as e:
            logger.error(f"Failed to perform partial update: {str(e)}")
            raise

    def sleep(self):
        """Put the display into sleep mode"""
        try:
            self.epd.sleep()
            logger.info("Display entered sleep mode")
        except Exception as e:
            logger.error(f"Failed to put display to sleep: {str(e)}")
            raise

    def wake(self):
        """Wake the display from sleep mode"""
        try:
            self.epd.init(self.epd.FULL_UPDATE)
            logger.info("Display woken from sleep")
        except Exception as e:
            logger.error(f"Failed to wake display: {str(e)}")
            raise
