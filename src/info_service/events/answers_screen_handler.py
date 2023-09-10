import sys
import time

from PyQt5 import QtCore, QtGui, QtWidgets

from info_service import actions


def main(main_window):
    for crud_name in ('TableAllAnswers',):

        ButtonFirstPage = getattr(main_window, f'ButtonFirstPage{crud_name}')
        ButtonFirstPage.clicked.connect(lambda: actions.win_answers_first_page(main_window))

        ButtonLastPage = getattr(main_window, f'ButtonLastPage{crud_name}')
        ButtonLastPage.clicked.connect(lambda: actions.win_answers_last_page(main_window))

        ButtonNextPage = getattr(main_window, f'ButtonNextPage{crud_name}')
        ButtonNextPage.clicked.connect(lambda: actions.win_answers_next_page(main_window))

        ButtonsPrevPage = getattr(main_window, f'ButtonPrevPage{crud_name}')
        ButtonsPrevPage.clicked.connect(lambda: actions.win_answers_prev_page(main_window))
