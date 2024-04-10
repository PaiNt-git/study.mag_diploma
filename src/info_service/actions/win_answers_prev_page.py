import json
import asyncio

from collections import OrderedDict

from PyQt5 import QtCore, QtGui, QtWidgets
import time

from info_service.db_base import Session, QuestAnswerBase

from info_service.db_utils import togudb_serializator

from info_service import actions

from info_service.actions._answers_utils import *


def main(main_window):

    table_widget_name = 'TableAllAnswers'

    cur_page_widget = getattr(main_window, f'CurPage{table_widget_name}')
    cur_page = int(cur_page_widget.text())

    max_page_widget = getattr(main_window, f'MaxPage{table_widget_name}')
    max_page = int(max_page_widget.text())

    columns = OrderedDict(
        [
            ('id', 'id'),
            ('questions', 'Вопросы \n(через точку с запятой)'),
            ('abstract', 'Контент\nАбстракт\nОтвет'),
        ])

    actions.win_CRUD_load_page(main_window, 'TableAllAnswers',
                               columns,
                               actions.db_list_entries(),
                               page_num=cur_page - 1,
                               row_map_callback=lambda x: q_k_result_format_override(togudb_serializator(x, include=columns.keys())),
                               cell_editable=lambda q, i: False,
                               )
