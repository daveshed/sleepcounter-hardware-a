"""
This module defines the interface for the led matrix and abstracts any low-
level commands to the driver.
"""
from abc import ABC, abstractmethod

# TODO: get rid of this unnecessary interface

class LedMatrixInterface(ABC):
    """
    Abstract interface for an led matrix that may be used by date display
    widgtets
    """
    @abstractmethod
    def show_message(self, text: str, scroll=False):
        """
        Child class should implement a method for showing a message and it
        should scroll

        Keyword arguments:
        text -- A string to display
        scroll -- A bool signifying whether to scroll the message across the
                  display.
        """

    @abstractmethod
    def clear(self):
        """Clear everything from the display"""
