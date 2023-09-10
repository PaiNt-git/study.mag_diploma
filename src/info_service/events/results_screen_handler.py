import sys
import time

from PyQt5 import QtCore, QtGui, QtWidgets

from info_service import actions


def main(main_window):
    for crud_name in ('TableInitialAllResults',):

        ButtonFirstPage = getattr(main_window, f'ButtonFirstPage{crud_name}')
        ButtonFirstPage.clicked.connect(lambda: actions.win_initial_query_first_page(main_window))

        ButtonLastPage = getattr(main_window, f'ButtonLastPage{crud_name}')
        ButtonLastPage.clicked.connect(lambda: actions.win_initial_query_last_page(main_window))

        ButtonNextPage = getattr(main_window, f'ButtonNextPage{crud_name}')
        ButtonNextPage.clicked.connect(lambda: actions.win_initial_query_next_page(main_window))

        ButtonsPrevPage = getattr(main_window, f'ButtonPrevPage{crud_name}')
        ButtonsPrevPage.clicked.connect(lambda: actions.win_initial_query_prev_page(main_window))

    for crud_name in ('TableModifiedAllResults',):

        ButtonFirstPage = getattr(main_window, f'ButtonFirstPage{crud_name}')
        ButtonFirstPage.clicked.connect(lambda: actions.win_modified_query_first_page(main_window))

        ButtonLastPage = getattr(main_window, f'ButtonLastPage{crud_name}')
        ButtonLastPage.clicked.connect(lambda: actions.win_modified_query_last_page(main_window))

        ButtonNextPage = getattr(main_window, f'ButtonNextPage{crud_name}')
        ButtonNextPage.clicked.connect(lambda: actions.win_modified_query_next_page(main_window))

        ButtonsPrevPage = getattr(main_window, f'ButtonPrevPage{crud_name}')
        ButtonsPrevPage.clicked.connect(lambda: actions.win_modified_query_prev_page(main_window))
