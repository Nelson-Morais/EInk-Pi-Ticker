import pigpio
import logging
import time

logger = logging.getLogger(__name__)

# Define pins at module level
RST_PIN = 17
DC_PIN = 25
BL_PIN = 24
CS_PIN = 8
BUSY_PIN = 24

class RaspberryPi:
    def __init__(self):
        # Use module level pins
        self.RST_PIN = RST_PIN
        self.DC_PIN = DC_PIN
        self.BL_PIN = BL_PIN
        self.CS_PIN = CS_PIN
        self.BUSY_PIN = BUSY_PIN

        # Initialize pigpio
        self.pi = pigpio.pi()
        if not self.pi.connected:
            raise RuntimeError("Failed to connect to pigpio daemon")

        # Setup pins
        self.pi.set_mode(self.RST_PIN, pigpio.OUTPUT)
        self.pi.set_mode(self.DC_PIN, pigpio.OUTPUT)
        self.pi.set_mode(self.CS_PIN, pigpio.OUTPUT)
        self.pi.set_mode(self.BUSY_PIN, pigpio.INPUT)

        # Initialize SPI with 4MHz baud rate
        self.SPI = self.pi.spi_open(0, 0, baud=4000000)

    def digital_write(self, pin, value):
        self.pi.write(pin, value)

    def digital_read(self, pin):
        return self.pi.read(pin)

    def delay_ms(self, delaytime):
        time.sleep(delaytime / 1000.0)

    def spi_writebyte(self, data):
        if isinstance(data, list):
            for byte in data:
                count, data = self.pi.spi_xfer(self.SPI, [byte])
        else:
            count, data = self.pi.spi_xfer(self.SPI, [data])

    def module_init(self):
        return 0

    def module_exit(self):
        self.pi.spi_close(self.SPI)
        self.pi.stop()

# Create a global instance
implementation = RaspberryPi()

# Expose module-level functions that the Waveshare library expects
def digital_write(pin, value):
    implementation.digital_write(pin, value)

def digital_read(pin):
    return implementation.digital_read(pin)

def delay_ms(delaytime):
    implementation.delay_ms(delaytime)

def spi_writebyte(data):
    implementation.spi_writebyte(data)

def module_init():
    return implementation.module_init()

def module_exit():
    implementation.module_exit()
