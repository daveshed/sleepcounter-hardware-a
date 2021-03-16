import datetime
import logging
import os
import sys
from time import sleep
from unittest import TestCase, skip
from unittest.mock import Mock, patch, call

from sleepcounter.core.application import Application
from sleepcounter.core.time.calendar import Calendar
from sleepcounter.core.time.event import Anniversary
from sleepcounter.core.time.bedtime import SleepChecker
from sleepcounter.core.mocks import mock_datetime

from sleepcounter.core.widget import BaseWidget
from sleepcounter.hardware_a.mocks import MockStage
from sleepcounter.hardware_a.widget.display import LedMatrixWidget
from sleepcounter.hardware_a.widget.stage import (
    SecondsStageWidget,
    SleepsStageWidget,
    DEFAULT_RECOVERY_FILE)

BONFIRE_NIGHT = Anniversary(name='Bonfire Night', month=11, day=5,)
HALLOWEEN = Anniversary(name='Halloween', month=10, day=31,)
CHRISTMAS = Anniversary(name='Christmas', month=12, day=25,)
EVENTS = [BONFIRE_NIGHT, HALLOWEEN, CHRISTMAS]
MAX_STAGE_LIMIT = 1000
APP_UPDATE_WAIT_SEC = 1
BaseWidget.mins_between_updates = 1 / 120 # 2 updates per second


class TestBase(TestCase):

    def _clean_up_tmp_files(self):
        if os.path.exists(DEFAULT_RECOVERY_FILE):
            os.remove(DEFAULT_RECOVERY_FILE)

    def setUp(self):
        self._clean_up_tmp_files()
        self.calendar = Calendar(EVENTS)
        self.mock_matrix = Mock()
        self.display_widget = LedMatrixWidget(self.mock_matrix, self.calendar)
        self.stage = MockStage()
        self.seconds_stage_widget = SecondsStageWidget(
            stage=self.stage, calendar=self.calendar)
        self.sleeps_stage_widget = SleepsStageWidget(
            stage=self.stage, calendar=self.calendar)
        self.app = None

    def tearDown(self):
        self._clean_up_tmp_files()
        self.app.stop()


class IntegrationSecondCounterWithDisplay(TestBase):

    def setUp(self):
        super().setUp()
        self.app = Application(
            widgets=[self.display_widget, self.seconds_stage_widget])
        self.app.start()

    @skip("second stage counter deprecated")
    def test_linear_stage_updates_position(self):
        today = datetime.datetime(
            year=2018,
            month=12,
            day=23,
            hour=12,
            minute=10)
        with mock_datetime(target=today):
            sleep(APP_UPDATE_WAIT_SEC)
        # stage should home first
        self.assertEqual(MockStage.MIN_POS, self.stage.position)
        xmas = datetime.date(year=2018, month=12, day=25)
        deadline = datetime.datetime.combine(xmas, SleepChecker.WAKE_UP_TIME)
        time_to_event = deadline - today
        time_elapsed = datetime.timedelta(days=1)
        tomorrow = today + time_elapsed
        with mock_datetime(target=tomorrow):
            sleep(APP_UPDATE_WAIT_SEC)
        expected_position = \
            int(time_elapsed / time_to_event * MockStage.MAX_POS)
        self.assertEqual(expected_position, self.stage.position)

    @skip("second stage counter deprecated")
    def test_led_matrix_updates_display(self):
        today = datetime.datetime(
            year=2018,
            month=12,
            day=23,
            hour=12,
            minute=10)
        with mock_datetime(target=today):
            sleep(APP_UPDATE_WAIT_SEC)
        self.assertIn(
            call('Christmas in 2 sleeps'),
            self.mock_matrix.show_message.call_args_list)


class IntegrationSleepsCounterWithDisplay(TestBase):

    def setUp(self):
        super().setUp()
        self.app = Application(
            widgets=[self.display_widget, self.sleeps_stage_widget])
        self.app.start()

    def test_linear_stage_updates_position(self):
        reset_time = datetime.datetime(
            year=2018,
            month=12,
            day=23,
            hour=12,
            minute=10)
        with mock_datetime(target=reset_time):
            sleep(APP_UPDATE_WAIT_SEC)
        # stage should reset and move to minimum position
        self.assertEqual(MockStage.MIN_POS, self.stage.position)
        expected_sleeps = 2
        # another sleep elapses
        sleeps_elapsed = 1
        tomorrow = reset_time + datetime.timedelta(days=1)
        with mock_datetime(target=tomorrow):
            sleep(APP_UPDATE_WAIT_SEC)
        expected_position = \
            int(sleeps_elapsed / expected_sleeps * MockStage.MAX_POS)
        self.assertEqual(expected_position, self.stage.position)

    def test_led_matrix_updates_display(self):
        today = datetime.datetime(
            year=2018,
            month=12,
            day=23,
            hour=12,
            minute=10)
        with mock_datetime(target=today):
            sleep(APP_UPDATE_WAIT_SEC)
        show_message_args, _ = self.mock_matrix.show_messages.call_args
        (actual_messages,) = show_message_args
        self.assertIn('Christmas in 2 sleeps . . . ', actual_messages)
