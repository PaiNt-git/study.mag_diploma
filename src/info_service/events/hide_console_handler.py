import sys
import time

from PyQt5 import QtCore, QtGui, QtWidgets

from info_service import actions


def main(main_window):
    main_window.HideConsoleCheckBox.clicked.connect(lambda: actions.win_toggle_hide_console(main_window))
