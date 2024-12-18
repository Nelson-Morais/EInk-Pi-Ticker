import logging
from PIL import Image, ImageDraw, ImageFont
import matplotlib.pyplot as plt
import io
import os
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MockDisplay:
    """
    A mock display class that saves images to disk instead of displaying on e-Paper.
    Follows the same interface as EPaperDisplay for compatibility.
    """
    def __init__(self):
        # Set up dimensions to match e-Paper display
        self.width = 250  # Display width
        self.height = 122  # Display height
        
        # Create image buffer
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
        
        # Ensure output directory exists
        os.makedirs("output", exist_ok=True)

    def init_display(self):
        """Mock initialization"""
        logger.info("Mock display initialized")

    def clear_display(self):
        """Clear the display image"""
        self.draw.rectangle((0, 0, self.width, self.height), fill=255)
        logger.info("Mock display cleared")

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
        """Save the current image to disk"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"output/display_{timestamp}.png"
        self.image.save(filename)
        logger.info(f"Saved display image to {filename}")

    def partial_update(self):
        """Mock partial update - same as full update for mock display"""
        self.display()

    def sleep(self):
        """Mock sleep mode"""
        logger.info("Mock display sleep mode")

    def wake(self):
        """Mock wake from sleep"""
        logger.info("Mock display wake from sleep")
