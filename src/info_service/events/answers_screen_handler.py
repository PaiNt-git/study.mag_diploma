import sys
import time

from collections import OrderedDict

from PyQt5 import QtCore, QtGui, QtWidgets

from info_service import actions
from info_service.actions._answers_utils import q_k_result_format_override
from info_service.db_utils import togudb_serializator


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

        columns = OrderedDict(
            [
                ('id', 'id'),
                ('questions', 'Вопросы \n(через точку с запятой)'),
                ('abstract', 'Контент\nАбстракт\nОтвет'),
            ])

        actions.win_CRUD_connect_edit(main_window, crud_name, columns, actions.db_list_entries(), row_map_callback=lambda x: q_k_result_format_override(togudb_serializator(x, include=columns.keys())))
