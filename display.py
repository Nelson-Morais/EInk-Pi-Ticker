import logging
from PIL import Image, ImageDraw, ImageFont
import matplotlib.pyplot as plt
import io
from waveshare_epd import epd2in13_V2
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Display:
    def __init__(self):
        self.epd = epd2in13_V2.EPD()
        self.width = self.epd.height  # Display is rotated 90°
        self.height = self.epd.width
        self.init_display()
        
        # Load fonts
        try:
            self.price_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
            self.symbol_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
        except OSError:
            # Fallback to default font if custom font not found
            self.price_font = ImageFont.load_default()
            self.symbol_font = ImageFont.load_default()

    def init_display(self):
        """Initialize the e-Paper display"""
        try:
            self.epd.init(self.epd.FULL_UPDATE)
            self.epd.Clear(0xFF)  # Clear to white
            logger.info("Display initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize display: {str(e)}")
            raise

    def create_price_image(self, symbol: str, stats, graph_data=None):
        """Create image with price and optional graph"""
        image = Image.new('1', (self.width, self.height), 255)  # 255: white
        draw = ImageDraw.Draw(image)

        # Draw symbol
        draw.text((5, 5), symbol, font=self.symbol_font, fill=0)

        # Draw current price
        price_text = f"${stats.current_price:.2f}" if stats.current_price < 1000 else f"${stats.current_price:,.0f}"
        draw.text((5, 30), price_text, font=self.price_font, fill=0)

        # Draw stats on the top right
        stats_x = self.width - 80  # Position stats 80 pixels from right edge
        
        # Draw high price
        high_text = f"H: ${stats.day_high:.2f}"
        draw.text((stats_x, 5), high_text, font=self.symbol_font, fill=0)
        
        # Draw low price
        low_text = f"L: ${stats.day_low:.2f}"
        draw.text((stats_x, 20), low_text, font=self.symbol_font, fill=0)

        # Draw graph if data is provided
        if graph_data is not None:
            graph_image = self.create_graph(graph_data)
            # Paste graph below price
            image.paste(graph_image, (0, 60))

        return image

    def create_graph(self, data):
        """Create a simple line graph of price history"""
        # Create figure with transparent background
        fig, ax = plt.subplots(figsize=(2.5, 0.6), dpi=100)
        fig.patch.set_alpha(0)
        ax.patch.set_alpha(0)

        # Plot line
        ax.plot(data.index, data['Close'], color='black', linewidth=1)

        # Remove axes and grid
        ax.axis('off')

        # Convert plot to image
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0)
        plt.close()
        buf.seek(0)
        graph = Image.open(buf).convert('L')
        
        # Convert to binary image (black and white only)
        graph = graph.point(lambda x: 0 if x < 128 else 255, '1')
        
        return graph

    def update(self, image):
        """Update the display with new image"""
        try:
            self.epd.display(self.epd.getbuffer(image))
            logger.info("Display updated successfully")
        except Exception as e:
            logger.error(f"Failed to update display: {str(e)}")
            raise

    def clear(self):
        """Clear the display"""
        try:
            self.epd.Clear(0xFF)
            logger.info("Display cleared successfully")
        except Exception as e:
            logger.error(f"Failed to clear display: {str(e)}")
            raise

    def sleep(self):
        """Put display to sleep to save power"""
        try:
            self.epd.sleep()
            logger.info("Display went to sleep")
        except Exception as e:
            logger.error(f"Failed to put display to sleep: {str(e)}")
            raise
