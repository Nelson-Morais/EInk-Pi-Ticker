import pigpio
import logging
import time

logger = logging.getLogger(__name__)

# Define pins at module level
RST_PIN = 17
DC_PIN = 25
CS_PIN = 8
BUSY_PIN = 24

class RaspberryPi:
    def __init__(self):
        # Use module level pins
        self.RST_PIN = RST_PIN
        self.DC_PIN = DC_PIN
        self.CS_PIN = CS_PIN
        self.BUSY_PIN = BUSY_PIN

        # Initialize pigpio
        self.pi = pigpio.pi()
        if not self.pi.connected:
            raise RuntimeError("Failed to connect to pigpio daemon")

        # Setup pins
        logger.info("Setting up GPIO pins...")
        self.pi.set_mode(self.RST_PIN, pigpio.OUTPUT)
        self.pi.set_mode(self.DC_PIN, pigpio.OUTPUT)
        self.pi.set_mode(self.CS_PIN, pigpio.OUTPUT)
        self.pi.set_mode(self.BUSY_PIN, pigpio.INPUT)

        # Initialize SPI with 4MHz baud rate
        logger.info("Setting up SPI...")
        self.SPI = self.pi.spi_open(0, 4000000, 0)  # channel 0 (CE0), 4MHz baud rate, default flags
        logger.info("Setup complete!")

    def digital_write(self, pin, value):
        logger.debug(f"Writing pin {pin} = {value}")
        self.pi.write(pin, value)

    def digital_read(self, pin):
        value = self.pi.read(pin)
        logger.debug(f"Reading pin {pin} = {value}")
        return value

    def delay_ms(self, delaytime):
        time.sleep(delaytime / 1000.0)

    def spi_writebyte(self, data):
        logger.debug(f"SPI write: {data if isinstance(data, int) else [hex(b) for b in data]}")
        try:
            if isinstance(data, (list, bytearray)):
                for byte in data:
                    count, _ = self.pi.spi_xfer(self.SPI, [byte])
                    logger.debug(f"SPI write result: count={count}")
            else:
                count, _ = self.pi.spi_xfer(self.SPI, [data])
                logger.debug(f"SPI write result: count={count}")
        except Exception as e:
            logger.error(f"SPI write failed: {str(e)}")
            raise

    def spi_writebyte2(self, data):
        logger.debug(f"SPI write2: {data if isinstance(data, int) else [hex(b) for b in data]}")
        try:
            if isinstance(data, (list, bytearray)):
                # Convert bytearray to list of integers for spi_xfer
                data_list = [int(b) for b in data]
                count, _ = self.pi.spi_xfer(self.SPI, data_list)
                logger.debug(f"SPI write2 result: count={count}")
            else:
                count, _ = self.pi.spi_xfer(self.SPI, [data])
                logger.debug(f"SPI write2 result: count={count}")
        except Exception as e:
            logger.error(f"SPI write2 failed: {str(e)}")
            raise

    def module_init(self):
        logger.info("Module initialized")
        return 0

    def module_exit(self):
        logger.info("Module exiting...")
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

def spi_writebyte2(data):
    implementation.spi_writebyte2(data)

def module_init():
    return implementation.module_init()

def module_exit():
    implementation.module_exit()
