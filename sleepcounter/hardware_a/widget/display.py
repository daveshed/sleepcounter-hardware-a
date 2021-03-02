"""
Module defining the LedMatrixWidget that represents sleep information using
an LED display.
"""
# pylint: disable=invalid-name
import logging

from sleepcounter.core.time.calendar import Calendar
from sleepcounter.core.widget import BaseWidget
from sleepcounter.hardware_a.display.interface import LedMatrixInterface

LOGGER = logging.getLogger("display widget")


class LedMatrixWidget(BaseWidget):
    """
    Represents the date using an led matrix.
    """
    # pylint: disable=too-few-public-methods
    def __init__(
            self,
            display: LedMatrixInterface,
            calendar: Calendar,
            label=None):
        self._display = display
        self._message = ""
        super().__init__(calendar, label)

    def update(self):
        """Updates the display using data from the current calendar instance"""
        self._display.clear()
        if self._calendar.special_day_today:
            self._handle_special_day()
        else:
            self._handle_regular_day()

    def _handle_special_day(self):
        self._message = "It's {}!".format(self._calendar.todays_event.name)
        LOGGER.info(
            "Updating with calendar %s. Setting message to <%s>",
            self._calendar, self._message)
        self._display.show_message(self._message)

    def _handle_regular_day(self):
        self._message = ""
        for event in self._calendar.events:
            n_sleeps = self._calendar.sleeps_to_event(event)
            unit = 'sleeps' if n_sleeps > 1 else 'sleep'
            self._message += "%s in %s %s . . . " % (event.name, n_sleeps, unit)
        LOGGER.info("Setting message to <%s>", self._message)
        self._display.show_message(self._message)
