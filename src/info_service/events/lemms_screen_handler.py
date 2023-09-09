import sys
import time

from PyQt5 import QtCore, QtGui, QtWidgets

from info_service import actions


def main(main_window):
    main_window.ButtonClearConsole.clicked.connect(actions.win_clear_console)

    for crud_name in ('TableAllLemms',):

        ButtonFirstPage = getattr(main_window, f'ButtonFirstPage{crud_name}')
        ButtonFirstPage.clicked.connect(lambda: actions.win_CRUD_first_page(main_window, crud_name))

        ButtonLastPage = getattr(main_window, f'ButtonLastPage{crud_name}')
        ButtonLastPage.clicked.connect(lambda: actions.win_CRUD_last_page(main_window, crud_name))

        ButtonNextPage = getattr(main_window, f'ButtonNextPage{crud_name}')
        ButtonNextPage.clicked.connect(lambda: actions.win_CRUD_next_page(main_window, crud_name))

        ButtonsPrevPage = getattr(main_window, f'ButtonsPrevPage{crud_name}')
        ButtonsPrevPage.clicked.connect(lambda: actions.win_CRUD_prev_page(main_window, crud_name))
