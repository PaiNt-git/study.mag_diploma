import sys
import time

from collections import OrderedDict

from PyQt5 import QtCore, QtGui, QtWidgets


from info_service.db_base import Session, QuestAnswerBase
from info_service import actions
from info_service.actions._answers_utils import q_k_result_format_override
from info_service.db_utils import togudb_serializator


def main(main_window):

    def del_answer():
        actions.win_CRUD_del_instance(main_window, 'TableAllAnswers', QuestAnswerBase, 0, dialog_title='Удалить экземпляр')
        actions.win_answers_first_page(main_window)
        actions.win_lemms_first_page(main_window)
        pass
    ButtonDelAnswer = getattr(main_window, f'ButtonDelAnswer')
    ButtonDelAnswer.clicked.connect(del_answer)

    def new_answer():
        columns_ = OrderedDict(
            [
                ('questions', 'Вопросы \n(через точку с запятой)'),
                ('abstract', 'Контент\nАбстракт\nОтвет'),
            ])
        actions.win_CRUD_new_instance(main_window, QuestAnswerBase, columns_, 'Новое знание')
        actions.win_answers_first_page(main_window)
        actions.win_lemms_first_page(main_window)
        pass
    ButtonNewAnswer = getattr(main_window, f'ButtonNewAnswer')
    ButtonNewAnswer.clicked.connect(new_answer)

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
