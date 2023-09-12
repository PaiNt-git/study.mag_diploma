import json

from PyQt5 import QtCore, QtGui, QtWidgets

from collections import OrderedDict

from info_service.db_base import Session, QuestAnswerBase

from info_service.db_utils import togudb_serializator

from info_service import actions

from info_service.actions._answers_utils import *


def main(main_window):

    columns = OrderedDict(
        [
            ('id', 'id'),
            ('category', 'Категория'),
            ('questions', 'Вопросы \n(через точку с запятой)'),
            ('name', 'Наименование \nзнания'),
            ('abstract', 'Контент\nАбстракт\nОтвет'),
            ('keywords', 'Ключевые слова \n(через запятую)'),
            ('result', 'Результат, \nссылка и т.д. (JSON)'),

        ])

    actions.win_CRUD_load_page(main_window, 'TableAllAnswers',
                               columns,
                               actions.db_list_entries(),
                               page_num=1,
                               row_map_callback=lambda x: q_k_result_format_override(togudb_serializator(x, include=columns.keys())),
                               cell_editable=cell_editable,
                               )
