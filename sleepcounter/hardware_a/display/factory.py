"""The max7219 display instance is created here as DISPLAY"""
from luma.core.interface.serial import spi, noop
from luma.led_matrix.device import max7219

SERIAL = spi(port=0, device=0, gpio=noop())
DISPLAY = max7219(SERIAL, cascaded=4, block_orientation=-90, rotate=2)
DISPLAY.contrast(25)
