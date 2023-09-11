import sys
import time

from PyQt5 import QtCore, QtGui, QtWidgets

from info_service import actions


def main(main_window):

    ButtonExecuteInitialQuery = main_window.ButtonExecuteInitialQuery

    def _execute_initial_query():
        actions.win_initial_query_pg_stemming(main_window)
        actions.win_initial_query_refresh_label(main_window)
        actions.win_initial_query_first_page(main_window)
    ButtonExecuteInitialQuery.clicked.connect(_execute_initial_query)

    ButtonExecuteModifiedQuery = main_window.ButtonExecuteModifiedQuery

    def _execute_modified_query():
        actions.win_modified_query_refresh_label(main_window)
        actions.win_modified_query_first_page(main_window)
    ButtonExecuteModifiedQuery.clicked.connect(_execute_modified_query)

    ButtonClearAllQueryScreen = main_window.ButtonClearAllQueryScreen

    def _clear_all_queries():
        initial_query_text_widget = main_window.TextInitialQuery
        initial_query_text_widget.setPlainText('')

        modified_query_text_widget = main_window.TextModifiedQuery
        modified_query_text_widget.setPlainText('')

        _execute_initial_query()
        _execute_modified_query()
    ButtonClearAllQueryScreen.clicked.connect(_clear_all_queries)
