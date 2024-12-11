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

# Override the waveshare_epd.epdconfig module with our implementation
sys.modules['waveshare_epd.epdconfig'] = sys.modules['epdconfig_override']

from waveshare_epd import epd2in13_V4

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EPaperDisplay:
    """
    A class to handle the e-Paper display operations using the Waveshare library.
    This implementation follows the Waveshare example code structure more closely.
    """
    def __init__(self):
        # Initialize the display
        self.epd = epd2in13_V4.EPD()
        
        # The display dimensions (using natural orientation like example)
        self.width = self.epd.height  # Match example code orientation
        self.height = self.epd.width  # Match example code orientation
        logger.info(f"Display dimensions: {self.width}x{self.height}")
        
        # Create initial image buffer (255 for white background)
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

        # Initialize the display after setting up image and draw objects
        self.init_display()
        
    def init_display(self):
        """Initialize the e-Paper display with proper error handling"""
        try:
            logger.info("Starting display initialization...")
            self.epd.init()  # V4 doesn't use FULL_UPDATE parameter
            logger.info("Display init complete, clearing display...")
            self.clear_display()  # Start with a clean display
            
            # Draw a test pattern
            logger.info("Drawing test pattern...")
            self.draw.rectangle([(0,0),(50,50)], outline=0)  # 0 for black
            self.draw.rectangle([(55,0),(100,50)], fill=0)   # 0 for black
            self.draw.line([(0,0),(50,50)], fill=0, width=1) # 0 for black
            self.draw.text((10, 60), 'Test Pattern', font=self.symbol_font, fill=0) # 0 for black
            
            logger.info("Getting buffer for test pattern...")
            buffer = self.epd.getbuffer(self.image)
            logger.info(f"Buffer size: {len(buffer)} bytes")
            
            logger.info("Sending buffer to display...")
            self.epd.display(buffer)
            logger.info("Test pattern sent to display")
            
            time.sleep(2)
            logger.info("E-Paper display initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize display: {str(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    def clear_display(self):
        """Clear the display to white"""
        try:
            self.epd.Clear(0xFF)  # 0xFF for white
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
        # Create a new figure with the correct size for the display
        graph_height = self.height - 60  # Leave space for text above
        dpi = 100
        fig_width = self.width / dpi
        fig_height = graph_height / dpi
        
        plt.figure(figsize=(fig_width, fig_height), dpi=dpi)
        plt.plot(data, color='black', linewidth=1)
        plt.axis('off')  # Hide axes
        
        # Set margins to 0 to use full space
        plt.margins(0)
        plt.tight_layout(pad=0)
        
        # Convert plot to PIL Image
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=dpi, bbox_inches='tight', pad_inches=0)
        plt.close()
        buf.seek(0)
        graph_image = Image.open(buf).convert('L')  # Convert to grayscale
        
        # Resize to fit the display
        graph_image = graph_image.resize((self.width, graph_height))
        
        # Convert to black and white (1-bit)
        graph_image = graph_image.point(lambda x: 0 if x < 128 else 255, '1')
        
        return graph_image

    def update_display(self):
        """Update the display with the current image buffer"""
        try:
            logger.info(f"Display buffer size: {len(self.epd.getbuffer(self.image))} bytes")
            self.epd.init()  # V4 doesn't use FULL_UPDATE parameter
            self.epd.display(self.epd.getbuffer(self.image))
            time.sleep(2)  # Give the display time to update
            logger.info("Display updated successfully")
        except Exception as e:
            logger.error(f"Failed to update display: {str(e)}")
            raise

    def sleep(self):
        """Put the display to sleep"""
        try:
            self.epd.init()  # V4 doesn't use FULL_UPDATE parameter
            self.epd.sleep()
            logger.info("Display entered sleep mode")
        except Exception as e:
            logger.error(f"Failed to put display to sleep: {str(e)}")
            raise
