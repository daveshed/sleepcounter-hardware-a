"""
Main entry-point module for the sleepcounter. All instances are created here
and the application is started.
"""
import logging
from sys import stdout
from time import sleep

from stage.stage import Stage
from stage.factory.config import Configurator
from stage.factory.rpi import RPiMonopolarStepperStageFactory

from sleepcounter.core.application import Application
# FIXME: The diary is a configuration detail and should not be part of the
#        package. It should be passed as a path when starting the app.
from sleepcounter.core.diary import CUSTOM_DIARY
from sleepcounter.hardware_a.display.display import LedMatrix
from sleepcounter.hardware_a.display.factory import DISPLAY
from sleepcounter.hardware_a.widget.display import LedMatrixWidget
from sleepcounter.hardware_a.widget.stage import SleepsStageWidget

logging.basicConfig(
    format='%(asctime)s[%(name)s]:%(levelname)s:%(message)s',
    stream=stdout,
    level=logging.INFO)

CONFIG = Configurator(
    motor_pins=(
        26, # a1 orange
        19, # b1 yellow
        13, # a2 pink
        6,  # b2 blue
    ),
    end_stop_pin=22,
    end_stop_active_low=True,
    maximum_position=4400,
    minimum_position=0)
STAGE = Stage(RPiMonopolarStepperStageFactory(CONFIG))


def main():
    """Application main function. Instantiates some widgets and runs the app"""
    display_widget = LedMatrixWidget(
        display=LedMatrix(DISPLAY),
        calendar=CUSTOM_DIARY)
    stage_widget = SleepsStageWidget(
        stage=STAGE,
        calendar=CUSTOM_DIARY)
    app = Application(widgets=[display_widget, stage_widget])
    app.start()
    while True:
        try:
            sleep(1)
        except KeyboardInterrupt:
            app.stop()
            break

if __name__ == "__main__":
    main()
