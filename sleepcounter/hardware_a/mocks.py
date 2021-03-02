"""Mock hardware implementation"""
import logging

from stage import exceptions
from unittest.mock import Mock

LOGGER = logging.getLogger("mock")

class MockStage:
    """A mock implemenation of a stepper motor driven linear stage"""
    MAX_POS = 100
    MIN_POS = 0

    def __init__(self):
        self._position = __class__.MIN_POS
        self.home()

    def home(self):
        """Move to home position"""
        LOGGER.info("Homing stage")
        self._position = __class__.MIN_POS

    def end(self):
        """Move to end position"""
        LOGGER.info("Moving to home position")
        self._position = self.max

    @property
    def max(self):
        """Return the maximum position index"""
        return __class__.MAX_POS

    @property
    def position(self):
        """Return the current position index"""
        return self._position

    @position.setter
    def position(self, request):
        LOGGER.info("Setting position to %s", request)
        too_large = request > __class__.MAX_POS
        too_small = request < __class__.MIN_POS
        if too_large or too_small:
            raise exceptions.OutOfRangeError(
                "Cannot go to position {}".format(request))
        self._position = request


class Matrix:
    """
    A mock for an led matrix device
    """
    _width = 32
    _height = 8
    _mode = "1"

    def __init__(self):
        _LOGGER.info("Created mock led matrix device %r", self)
        self.display = Mock()

    @property
    def width(self):
        """
        Width of the display in pixels
        """
        return Matrix._width

    @property
    def height(self):
        """
        Height of the display in pixels
        """
        return Matrix._height

    @property
    def mode(self):
        """
        Returns mode which is needed for image drawing reasons
        """
        return Matrix._mode

    def clear(self):
        """
        Clear the display
        """
        _LOGGER.info("Clearing device %r", self)
