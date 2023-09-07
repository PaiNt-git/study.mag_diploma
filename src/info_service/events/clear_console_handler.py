import sys
import time

from PyQt5 import QtCore, QtGui, QtWidgets

from info_service import actions


def main(main_window):
    main_window.ButtonClearConsole.clicked.connect(actions.win_clear_console)
