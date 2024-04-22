import sys
import time

from PyQt5 import QtCore, QtGui, QtWidgets

from info_service import actions


def main(main_window):
    main_window.MAINWINDOW_LOCAL_STORAGE['only_questions'] = True
    main_window.OnlyQuestionsCheckBox.clicked.connect(lambda: actions.win_toggle_only_questions(main_window))
