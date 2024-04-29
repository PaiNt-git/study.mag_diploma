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
    only_questions = main_window.MAINWINDOW_LOCAL_STORAGE['only_questions']

    table_widget_name = 'TableRelevQueryManage'

    cur_page_widget = getattr(main_window, f'CurPage{table_widget_name}')
    cur_page = int(cur_page_widget.text())

    max_page_widget = getattr(main_window, f'MaxPage{table_widget_name}')
    max_page = int(max_page_widget.text())

    columns = OrderedDict(
        [
            ('id', 'id'),
            ('query', 'Запрос'),
        ])

    actions.win_CRUD_load_page(main_window, table_widget_name,
                               columns,
                               actions.db_list_queries(),
                               page_num=cur_page + 1,
                               )
