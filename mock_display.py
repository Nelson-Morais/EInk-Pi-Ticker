import logging
from PIL import Image, ImageDraw, ImageFont
import matplotlib.pyplot as plt
import io
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MockDisplay:
    def __init__(self):
        self.width = 250  # Same dimensions as epd2in13_V2
        self.height = 122
        self.init_display()
        
        # Load fonts - using Arial for Windows
        try:
            self.price_font = ImageFont.truetype("arial.ttf", 24)
            self.symbol_font = ImageFont.truetype("arial.ttf", 16)
        except OSError:
            logger.warning("Arial font not found, using default font")
            self.price_font = ImageFont.load_default()
            self.symbol_font = ImageFont.load_default()
        
        # Create output directory if it doesn't exist
        os.makedirs("output", exist_ok=True)
    
    def init_display(self):
        logger.info("Initializing mock display")
        self.clear()
    
    def clear(self):
        logger.info("Clearing mock display")
        # Create a new white image
        self.image = Image.new('1', (self.width, self.height), 255)
        self.draw = ImageDraw.Draw(self.image)
        self._save_current_image()

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
        self.image = image
        self._save_current_image()
        logger.info("Display updated successfully")

    def sleep(self):
        """Mock sleep function"""
        logger.info("Mock display going to sleep")

    def _save_current_image(self):
        """Save the current image to a file"""
        self.image.save("output/current_display.png")
        logger.info("Saved display to output/current_display.png")
