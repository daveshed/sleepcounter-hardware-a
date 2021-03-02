import datetime
import logging
import os
import sys
from time import sleep
import unittest
from unittest.mock import Mock, patch

from sleepcounter.core.time.calendar import Calendar
from sleepcounter.core.time.event import Anniversary, SpecialDay
from sleepcounter.core.mocks import mock_datetime
from sleepcounter.core.widget import BaseWidget
from sleepcounter.hardware_a.widget.display import LedMatrixWidget

CHRISTMAS_DAY = Anniversary(name='Christmas', month=12, day=25,)
NEW_YEARS_DAY = Anniversary(name="New Year\'s Day", month=1, day=1,)
RANDOM_EVENT = SpecialDay(name="Something cool", year=2018, month=4, day=10,)
CALENDAR = Calendar([CHRISTMAS_DAY, NEW_YEARS_DAY])
WIDGET_UPDATE_WAIT_SEC = 1
BaseWidget.mins_between_updates = 1 / 120 # 2 updates per second


class TestBase(unittest.TestCase):

    def setUp(self):
        self.mock_matrix = Mock()
        self.display_widget = LedMatrixWidget(self.mock_matrix, CALENDAR)
        self.display_widget.start()

    def tearDown(self):
        self.display_widget.stop()


class DisplayUpdateTests(TestBase):

    def test_display_shows_correct_sleeps(self):
        today = datetime.datetime(
            year=2018,
            month=12,
            day=23,
            hour=12,
            minute=10)
        expected_sleeps_xmas = 2
        expected_sleeps_new_year = 9
        with mock_datetime(target=today):
            sleep(WIDGET_UPDATE_WAIT_SEC)
        show_message_args, _ = self.mock_matrix.show_message.call_args
        (actual_message,) = show_message_args
        self.assertIn(
            'Christmas in %d sleeps' % expected_sleeps_xmas,
            actual_message)
        self.assertIn(
            'New Year\'s Day in %d sleeps' % expected_sleeps_new_year,
            actual_message)

    def test_display_should_not_show_dates_past(self):
        today = datetime.datetime(
            year=2018,
            month=12,
            day=27,
            hour=12,
            minute=10)
        expected_sleeps_new_year = 5
        with mock_datetime(target=today):
            sleep(WIDGET_UPDATE_WAIT_SEC)
        show_message_args, _ = self.mock_matrix.show_message.call_args
        (actual_message,) = show_message_args
        self.assertIn(
            'New Year\'s Day in %d sleeps' % expected_sleeps_new_year,
            actual_message)
        # Special day in the past shouldnot show up...
        self.assertNotIn('Something cool', actual_message)

    def test_display_shows_one_sleep_not_sleeps(self):
        today = datetime.datetime(
            year=2018,
            month=12,
            day=24,
            hour=12,
            minute=10)
        expected_sleeps = 1
        with mock_datetime(target=today):
            sleep(WIDGET_UPDATE_WAIT_SEC)
        show_message_args, _ = self.mock_matrix.show_message.call_args
        (actual_message,) = show_message_args
        self.assertIn('Christmas in 1 sleep', actual_message)

    def test_display_shows_special_day(self):
        today = datetime.datetime(
            year=2018,
            month=12,
            day=25,
            hour=17,
            minute=9)
        with mock_datetime(target=today):
            sleep(WIDGET_UPDATE_WAIT_SEC)
        self.mock_matrix.show_message.assert_called_with("It's Christmas!")
