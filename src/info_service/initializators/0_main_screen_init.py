from PyQt5 import QtCore, QtGui, QtWidgets

from info_service import actions


def main(main_window):

    main_window.ClearConsole.clicked.connect(actions.win_clear_console)

    pass
