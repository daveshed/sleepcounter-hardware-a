"""
Led matrix interface implementation which extends the abstract base class and
makes calls to the driver simpler.
"""
from logging import getLogger
from threading import Event, Thread
from time import sleep
from PIL import ImageFont

from luma.core.render import canvas
from luma.core.virtual import viewport
from luma.led_matrix.device import max7219

from sleepcounter.hardware_a.display.interface import LedMatrixInterface
from sleepcounter.hardware_a.fonts.library import AVAILABLE_FONTS

SCROLL_RATE = 40 # pixels per second
VERTICAL_OFFSET = 0

_LOGGER = getLogger("led matrix")


class LedMatrix(LedMatrixInterface):
    """Led matrix implementation - an interface to the luma core library"""
    def __init__(self, device: max7219):
        """Creates the interface from a MAX7219 device instance"""
        _LOGGER.info(
            "Instantiated LED matrix device %r with unit %r ",
            self, device)
        self.device = device
        self.virtual = viewport(device, width=200, height=100)
        self._to_display = []
        self._worker = _DeviceThreadManager(self._activity)

    def show_messages(self, messages: list, scroll=False):
        """
        Shows messages from a list. If a message fits the display, it will be
        shown static. If it's too long, it will be scrolled across the display.
        Scrolling may be forced optionally with the scroll arg.
        """
        self.clear()
        self._to_display = [_Message(text, scroll) for text in messages]
        _LOGGER.info("Showing messages...{}".format(self._to_display))
        self._worker.start()

    def clear(self):
        """
        Clear the display
        """
        _LOGGER.info("Clearing display %r", self)
        self._worker.stop()
        self.device.clear()
        self._to_display = []

    def _activity(self):
        """
        The display's worker activity that should be executed asynchronously.
        """
        for message in self._to_display:
            if message.is_scrolling(self.device):
                _LOGGER.info("Scrolling message <%s>...", message.text)
                self._scroll_text(message)
            else:
                _LOGGER.info("Showing static message <%s>...", message.text)
                self._show_text(message)

    def _show_text(self, message, offset=0):
        _LOGGER.debug(
            "Showing: <text:%s><offset:%d>", message.text, offset)
        with canvas(self.virtual) as draw:
            draw.text(
                (offset, VERTICAL_OFFSET),
                message.text,
                font=_Message.FONT,
                fill="white",
            )

    def _scroll_text(self, message):
        for offset in range(message.length + self.device.width):
            self._show_text(message, (self.device.width - offset))
            sleep(1 / SCROLL_RATE)


class _Message:
    FONT_PATH = AVAILABLE_FONTS['Vera.ttf']
    FONT_SIZE = 9
    FONT = ImageFont.truetype(font=FONT_PATH, size=FONT_SIZE)

    def __init__(self, text: str, scroll: bool):
        """
        Builds a message to display on the device from text
        """
        self._text = text.upper()
        self._scroll = scroll

    @property
    def text(self):
        """
        Returns the text contained in the message
        """
        return self._text

    @property
    def length(self):
        """
        Returns the length of the message in pixels
        """
        length, _ = self.__class__.FONT.getsize(self.text)
        return length

    @property
    def height(self):
        """
        Returns the height of the message in pixels
        """
        _, height = self.__class__.FONT.getsize(self.text)
        return height

    def is_scrolling(self, device):
        return self._scroll or (self.length > device.width)

    def __repr__(self):
        return "{}(text={})".format(type(self).__name__, self.text)

    def __str__(self):
        return self.text


class _DeviceThreadManager:

    def __init__(self, target):
        """
        Manages the device's thread of activity
        """
        self._target = target
        self._active = Event()
        self._thread = None

    def start(self):
        """
        Start the thread of activity
        """
        if self._active:
            _LOGGER.debug("Already active")
            self.stop()
        _LOGGER.debug("Restarting thread...")
        self._thread = Thread(
            target=self._activity,
            daemon=True)
        self._thread.start()

    def stop(self):
        """
        Stop the thread of activity
        """
        if self._thread:
            _LOGGER.debug("Tearing down thread")
            self._active.clear()
            self._thread.join()

    def _activity(self):
        self._active.set()
        while self._active.is_set():
            self._target()
