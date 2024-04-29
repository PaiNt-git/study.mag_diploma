import sys
import time

from collections import OrderedDict

from PyQt5 import QtCore, QtGui, QtWidgets


from info_service.db_base import Session, QuestAnswerBase,\
    QuestAnswerBaseRelevQuery, QuestAnswerBaseRelevQueryRel
from info_service import actions
from info_service.actions._answers_utils import q_k_result_format_override
from info_service.db_utils import togudb_serializator


def main(main_window):

    def del_query():
        actions.win_CRUD_del_instance(main_window, 'TableRelevQueryManage', QuestAnswerBaseRelevQuery, 0, dialog_title='Удалить экземпляр')
        actions.win_relev_first_page(main_window)
        actions.win_relev_query_first_page(main_window)
        pass
    ButtonDelRelevQuery = getattr(main_window, f'ButtonDelRelevQuery')
    ButtonDelRelevQuery.clicked.connect(del_query)

    def new_query():
        columns_ = OrderedDict(
            [
                ('query', 'Запрос'),
            ])
        actions.win_CRUD_new_instance(main_window, QuestAnswerBaseRelevQuery, columns_, 'Новый запрос')
        actions.win_relev_first_page(main_window)
        actions.win_relev_query_first_page(main_window)
        pass
    ButtonNewRelevQuery = getattr(main_window, f'ButtonNewRelevQuery')
    ButtonNewRelevQuery.clicked.connect(new_query)

    def del_relev():
        actions.win_CRUD_del_instance(main_window, 'TableRelevManage', QuestAnswerBaseRelevQueryRel, 0, dialog_title='Удалить экземпляр')
        actions.win_relev_first_page(main_window)
        pass
    ButtonDelRelev = getattr(main_window, f'ButtonDelRelev')
    ButtonDelRelev.clicked.connect(del_relev)

    def new_relev():
        columns_1 = OrderedDict(
            [
                ('query_id', 'query_id'),
                ('answer_id', 'answer_id'),
                ('relevantion_part', 'Доля релевантности'),
            ])
        actions.win_CRUD_new_instance(main_window, QuestAnswerBaseRelevQueryRel, columns_1, 'Новая релевантная связь')
        actions.win_relev_first_page(main_window)
        pass
    ButtonNewRelev = getattr(main_window, f'ButtonNewRelev')
    ButtonNewRelev.clicked.connect(new_relev)

    for crud_name in ('TableRelevQueryManage', 'TableRelevManage'):

        if crud_name == 'TableRelevQueryManage':

            ButtonFirstPage = getattr(main_window, f'ButtonFirstPage{crud_name}')
            ButtonFirstPage.clicked.connect(lambda: actions.win_relev_query_first_page(main_window))

            ButtonLastPage = getattr(main_window, f'ButtonLastPage{crud_name}')
            ButtonLastPage.clicked.connect(lambda: actions.win_relev_query_last_page(main_window))

            ButtonNextPage = getattr(main_window, f'ButtonNextPage{crud_name}')
            ButtonNextPage.clicked.connect(lambda: actions.win_relev_query_next_page(main_window))

            ButtonsPrevPage = getattr(main_window, f'ButtonPrevPage{crud_name}')
            ButtonsPrevPage.clicked.connect(lambda: actions.win_relev_query_prev_page(main_window))

            columns = OrderedDict(
                [
                    ('id', 'id'),
                    ('query', 'Запрос'),
                ])

            actions.win_CRUD_connect_edit(main_window, crud_name, columns, actions.db_list_queries())

        if crud_name == 'TableRelevManage':

            ButtonFirstPage = getattr(main_window, f'ButtonFirstPage{crud_name}')
            ButtonFirstPage.clicked.connect(lambda: actions.win_relev_first_page(main_window))

            ButtonLastPage = getattr(main_window, f'ButtonLastPage{crud_name}')
            ButtonLastPage.clicked.connect(lambda: actions.win_relev_last_page(main_window))

            ButtonNextPage = getattr(main_window, f'ButtonNextPage{crud_name}')
            ButtonNextPage.clicked.connect(lambda: actions.win_relev_next_page(main_window))

            ButtonsPrevPage = getattr(main_window, f'ButtonPrevPage{crud_name}')
            ButtonsPrevPage.clicked.connect(lambda: actions.win_relev_prev_page(main_window))

            columns = OrderedDict(
                [
                    ('id', 'id'),
                    ('query_id', 'query_id'),
                    ('answer_id', 'answer_id'),
                    ('answer_name', 'Ответ'),
                    ('relevantion_part', 'Доля релевантности'),
                ])

            actions.win_CRUD_connect_edit(main_window, crud_name, columns, actions.db_list_relevantion())
