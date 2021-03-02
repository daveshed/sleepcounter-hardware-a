import datetime
import os
import sys
from time import sleep
import unittest
from unittest.mock import Mock

from sleepcounter.core.mocks import mock_datetime
from sleepcounter.hardware_a.mocks import MockStage
from sleepcounter.core.time.calendar import Calendar
from sleepcounter.core.time.event import Anniversary
from sleepcounter.core.widget import BaseWidget
from sleepcounter.hardware_a.widget.stage import (
    SecondsStageWidget,
    SleepsStageWidget,
    DEFAULT_RECOVERY_FILE)

JUST_BEFORE_XMAS = datetime.datetime(
    year=2018,
    month=12,
    day=3,
    hour=8,
    minute=5)
CHRISTMAS_DAY = Anniversary(name='xmas', month=12, day=25,)
NEW_YEARS_DAY = Anniversary(name="New Year\'s Day", month=1, day=1,)
CALENDAR = Calendar([CHRISTMAS_DAY, NEW_YEARS_DAY])
DIR_PATH = os.path.dirname(os.path.realpath(__file__))
ALTERNATIVE_FILE_PATH = DIR_PATH + '/tmp'
WIDGET_UPDATE_WAIT_SEC = 1
BaseWidget.mins_between_updates = 1 / 120 # 2 updates per second


class TestBase(unittest.TestCase):

    def _clean_up_tmp_files(self):
        try:
            os.remove(DEFAULT_RECOVERY_FILE)
        except OSError:
            pass
        try:
            os.remove(ALTERNATIVE_FILE_PATH)
        except OSError:
            pass

    def setUp(self):
        self._clean_up_tmp_files()
        self.mock_stage = MockStage()
        self.stage_widget = None

    def tearDown(self):
        self._clean_up_tmp_files()
        self.stage_widget.stop()


class StageWidgetStoresPerisistentData(TestBase):

    def test_reinitialise_to_stored_position(self):
        self.recovery_file = ALTERNATIVE_FILE_PATH
        self.stage_widget = SecondsStageWidget(
            stage=self.mock_stage,
            calendar=CALENDAR,
            recovery_file=self.recovery_file)
        self.stage_widget.start()
        today = JUST_BEFORE_XMAS
        with mock_datetime(target=today):
            sleep(WIDGET_UPDATE_WAIT_SEC)
        today += datetime.timedelta(days=1)
        with mock_datetime(target=today):
            sleep(WIDGET_UPDATE_WAIT_SEC)
        # store the position in the test before going down
        pos_before = self.mock_stage.position
        # system goes down which resets the stage, widget is reinitialised
        self.stage_widget.stop()
        self.mock_stage = MockStage()
        self.stage_widget = SecondsStageWidget(
            stage=self.mock_stage,
            calendar=CALENDAR,
            recovery_file=self.recovery_file)
        self.stage_widget.start()
        with mock_datetime(target=today):
            sleep(WIDGET_UPDATE_WAIT_SEC)
        # get the position after restarting
        pos_after = self.mock_stage.position
        # the position should be same as before it went down
        self.assertEqual(pos_after, pos_before)

    def test_reinitialise_to_stored_position_default_file(self):
        self.stage_widget = SecondsStageWidget(
            self.mock_stage,
            calendar=CALENDAR)
        self.stage_widget.start()
        today = JUST_BEFORE_XMAS
        with mock_datetime(target=today):
            sleep(WIDGET_UPDATE_WAIT_SEC)
        today += datetime.timedelta(days=1)
        with mock_datetime(target=today):
            sleep(WIDGET_UPDATE_WAIT_SEC)
        # store the position in the test before going down
        pos_before = self.mock_stage.position
        # system goes down which resets the stage, widget is reinitialised
        self.stage_widget.stop()
        self.mock_stage = MockStage()
        self.stage_widget = SecondsStageWidget(
            stage=self.mock_stage,
            calendar=CALENDAR)
        self.stage_widget.start()
        with mock_datetime(target=today):
            sleep(WIDGET_UPDATE_WAIT_SEC)
        # get the position after restarting
        pos_after = self.mock_stage.position
        # the position should be same as before it went down
        self.assertEqual(pos_after, pos_before)

    def test_reinitialised_after_event_should_reset(self):
        self.stage_widget = SecondsStageWidget(
            stage=self.mock_stage,
            calendar=CALENDAR)
        today = JUST_BEFORE_XMAS
        with mock_datetime(target=today):
            sleep(WIDGET_UPDATE_WAIT_SEC)
        today += datetime.timedelta(days=1)
        with mock_datetime(target=today):
            sleep(WIDGET_UPDATE_WAIT_SEC)
        pos_before = self.mock_stage.position
        # system goes down which resets the stage, widget is reinitialised
        self.stage_widget.stop()
        self.mock_stage = MockStage()
        self.stage_widget = SecondsStageWidget(
            stage=self.mock_stage,
            calendar=CALENDAR)
        self.stage_widget.start()
        # system is brought back up after an event so should restart counting
        just_after_christmas = datetime.datetime(
            year=2018,
            month=12,
            day=26,
            hour=7,
            minute=55)
        with mock_datetime(target=just_after_christmas):
            sleep(WIDGET_UPDATE_WAIT_SEC)
        # stage should home to restart counting
        self.assertEqual(0, self.mock_stage.position)


class StageWidgetDisplaysTime(TestBase):

    def test_stage_at_end_on_special_day(self):
        self.stage_widget = SecondsStageWidget(
            self.mock_stage,
            CALENDAR)
        self.stage_widget.start()
        today = JUST_BEFORE_XMAS
        with mock_datetime(target=today):
            sleep(WIDGET_UPDATE_WAIT_SEC)
        today += datetime.timedelta(days=1)
        with mock_datetime(target=today):
            sleep(WIDGET_UPDATE_WAIT_SEC)
        today = datetime.datetime(
            year=2018,
            month=12,
            day=25,
            hour=8,
            minute=12,
        )
        with mock_datetime(target=today):
            sleep(WIDGET_UPDATE_WAIT_SEC)
        self.assertEqual(MockStage.MAX_POS, self.mock_stage.position)


class SleepsStageWidgetDisplaysTime(TestBase):

    def test_stage_at_end_on_special_day(self):
        self.stage_widget = SleepsStageWidget(
            self.mock_stage,
            CALENDAR)
        self.stage_widget.start()
        today = JUST_BEFORE_XMAS
        with mock_datetime(target=today):
            sleep(WIDGET_UPDATE_WAIT_SEC)
        today += datetime.timedelta(days=1)
        with mock_datetime(target=today):
            sleep(WIDGET_UPDATE_WAIT_SEC)
        today = datetime.datetime(
            year=2018,
            month=12,
            day=25,
            hour=8,
            minute=12,
        )
        with mock_datetime(target=today):
            sleep(WIDGET_UPDATE_WAIT_SEC)
        self.assertEqual(MockStage.MAX_POS, self.mock_stage.position)
        # a bit more timme passes but the widget should not move
        today = datetime.datetime(
            year=2018,
            month=12,
            day=25,
            hour=10,
            minute=7,
        )
        with mock_datetime(target=today):
            sleep(WIDGET_UPDATE_WAIT_SEC)
        self.assertEqual(MockStage.MAX_POS, self.mock_stage.position)

    def test_stage_homed_after_special_day(self):
        self.stage_widget = SleepsStageWidget(
            self.mock_stage,
            CALENDAR)
        self.stage_widget.start()
        today = JUST_BEFORE_XMAS
        with mock_datetime(target=today):
            sleep(WIDGET_UPDATE_WAIT_SEC)
        xmas_day = datetime.datetime(
            year=2018,
            month=12,
            day=25,
            hour=8,
            minute=12,
        )
        with mock_datetime(target=xmas_day):
            sleep(WIDGET_UPDATE_WAIT_SEC)
        today = xmas_day + datetime.timedelta(days=1)
        with mock_datetime(target=today):
            sleep(WIDGET_UPDATE_WAIT_SEC)
        self.assertEqual(MockStage.MIN_POS, self.mock_stage.position)

    @unittest.skip("Flakey test")
    def test_stage_moves_forward_after_sleep(self):
        self.stage_widget = SleepsStageWidget(
            self.mock_stage,
            CALENDAR)
        self.stage_widget.start()
        just_before_bedtime = datetime.datetime(
            year=2018,
            month=12,
            day=3,
            hour=18,
            minute=5)
        with mock_datetime(target=just_before_bedtime):
            sleep(WIDGET_UPDATE_WAIT_SEC)
        # stage should be homed initially
        self.assertEqual(MockStage.MIN_POS, self.mock_stage.position)
        just_after_bedtime = datetime.datetime(
            year=2018,
            month=12,
            day=3,
            hour=21,
            minute=19)
        # stage should not move yet.
        with mock_datetime(target=just_after_bedtime):
            sleep(WIDGET_UPDATE_WAIT_SEC)
        self.assertEqual(MockStage.MIN_POS, self.mock_stage.position)
        wake_up_time = datetime.datetime(
            year=2018,
            month=12,
            day=4,
            hour=8,
            minute=1)
        # stage should have moved now.
        with mock_datetime(target=wake_up_time):
            sleep(WIDGET_UPDATE_WAIT_SEC)
        self.assertGreater(self.mock_stage.position, MockStage.MIN_POS)