import gpiozero
from gpiozero.pins.pigpio import PiGPIOFactory
import spidev

class RaspberryPi:
    def __init__(self):
        self.factory = PiGPIOFactory()
        gpiozero.Device.pin_factory = self.factory
        
        # Pin definitions
        self.RST_PIN = 17
        self.DC_PIN = 25
        self.CS_PIN = 8
        self.BUSY_PIN = 24
        
        # Setup GPIO
        self.GPIO_RST_PIN = gpiozero.DigitalOutputDevice(self.RST_PIN, pin_factory=self.factory)
        self.GPIO_DC_PIN = gpiozero.DigitalOutputDevice(self.DC_PIN, pin_factory=self.factory)
        self.GPIO_CS_PIN = gpiozero.DigitalOutputDevice(self.CS_PIN, pin_factory=self.factory)
        self.GPIO_BUSY_PIN = gpiozero.DigitalInputDevice(self.BUSY_PIN, pull_up=False, pin_factory=self.factory)
        
        # Setup SPI
        self.SPI = spidev.SpiDev(0, 0)
        self.SPI.max_speed_hz = 4000000
        self.SPI.mode = 0b00

    def digital_write(self, pin, value):
        if pin == self.RST_PIN:
            self.GPIO_RST_PIN.value = value
        elif pin == self.DC_PIN:
            self.GPIO_DC_PIN.value = value
        elif pin == self.CS_PIN:
            self.GPIO_CS_PIN.value = value

    def digital_read(self, pin):
        if pin == self.BUSY_PIN:
            return self.GPIO_BUSY_PIN.value
        return 0

    def delay_ms(self, delaytime):
        import time
        time.sleep(delaytime / 1000.0)

    def spi_writebyte(self, data):
        self.SPI.writebytes([data])

    def spi_writebyte2(self, data):
        self.SPI.writebytes2(data)

    def module_init(self):
        return 0

    def module_exit(self):
        self.SPI.close()

# Create the implementation instance
implementation = RaspberryPi()
