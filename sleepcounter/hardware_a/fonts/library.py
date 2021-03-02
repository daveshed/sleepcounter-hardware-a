"""
A library of all ttf fonts available for the display widget

module constants:
FONT_DIR -- directory containing fonts
AVAILABLE_FONTS -- a dictionary of all available fonts
"""
from os import path, listdir

FONT_DIR = path.dirname(path.realpath(__file__))

AVAILABLE_FONTS = {}
for file in listdir(FONT_DIR):
    if file.endswith('.ttf'):
        AVAILABLE_FONTS[file] = path.join(FONT_DIR, file)
