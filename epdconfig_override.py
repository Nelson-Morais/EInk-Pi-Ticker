import pigpio
import spidev

class RaspberryPi:
    def __init__(self):
        self.RST_PIN = 17
        self.DC_PIN = 25
        self.BL_PIN = 24
        self.CS_PIN = 8
        self.BUSY_PIN = 24

        # Initialize pigpio
        self.pi = pigpio.pi()
        if not self.pi.connected:
            raise RuntimeError("Failed to connect to pigpio daemon")

        # Setup pins
        self.pi.set_mode(self.RST_PIN, pigpio.OUTPUT)
        self.pi.set_mode(self.DC_PIN, pigpio.OUTPUT)
        self.pi.set_mode(self.CS_PIN, pigpio.OUTPUT)
        self.pi.set_mode(self.BUSY_PIN, pigpio.INPUT)

        # Setup SPI
        self.SPI = spidev.SpiDev(0, 0)
        self.SPI.max_speed_hz = 4000000
        self.SPI.mode = 0b00

    def digital_write(self, pin, value):
        self.pi.write(pin, value)

    def digital_read(self, pin):
        return self.pi.read(pin)

    def delay_ms(self, delaytime):
        self.pi.time_sleep(delaytime / 1000.0)

    def spi_writebyte(self, data):
        self.SPI.writebytes([data])

    def spi_writebyte2(self, data):
        self.SPI.writebytes2(data)

    def module_init(self):
        return 0

    def module_exit(self):
        self.SPI.close()
        self.pi.stop()

# Create the implementation instance
implementation = RaspberryPi()
