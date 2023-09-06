import sys
import time
import asyncio

from PyQt5 import QtCore, QtGui, QtWidgets

from info_service import actions


def main(main_window):

    time.sleep(15)

    actions.keras()
