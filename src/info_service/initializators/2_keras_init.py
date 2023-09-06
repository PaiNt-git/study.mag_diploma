import sys
import time
import asyncio

from PyQt5 import QtCore, QtGui, QtWidgets

from info_service import actions


def main(main_window):

    print('before')

    time.sleep(5)

    print('after')

    actions.keras()

    print('after keras')
