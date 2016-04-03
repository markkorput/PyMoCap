"""
Usage:
    python py2app-play.py py2app
"""

from setuptools import setup

APP = ['playgui.py']
DATA_FILES = ['walk-198frames.binary.recording']
OPTIONS = {'argv_emulation': False}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
