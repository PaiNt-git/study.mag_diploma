from PyQt5 import QtCore, QtGui, QtWidgets

from collections import OrderedDict

from info_service.db_base import Session, QuestAnswerBase

from info_service.db_utils import togudb_serializator

from info_service import actions
import json


def main(main_window):

    columns = OrderedDict(
        [
            ('id', 'id'),
            ('category', 'Категория'),
            ('questions', 'Вопросы (через точку с запятой)'),
            ('name', 'Наименование знания'),
            ('abstract', 'Контент-абстракт-ответ'),
            ('keywords', 'Ключевые слова (через запятую)'),
            ('result', 'Результат, ссылка и т.д. (JSON)'),

        ])

    def q_k_result_format_override(row):
        row.name = row.name or ''
        row.questions = '; '.join(row.questions) if row.questions and len(row.questions) else ''
        row.keywords = ', '.join(row.keywords) if row.keywords and len(row.keywords) else ''
        row.result = json.dumps(row.result, ensure_ascii=False) if row.result and len(row.result) else ''
        return row

    def cell_editable(queryset_row, qt_item):
        column_inx = qt_item.column()
        if column_inx > 0:
            return True
        table_widget = qt_item.tableWidget()
        vert = table_widget.horizontalHeaderItem(column_inx)
        column_name = vert.text()
        if column_name == 'id':
            return False
        return True

    actions.win_CRUD_load_page(main_window, 'TableAllAnswers',
                               columns,
                               actions.db_list_entries(),
                               page_num=1,
                               row_map_callback=lambda x: q_k_result_format_override(togudb_serializator(x, include=columns.keys())),
                               cell_editable=cell_editable,
                               )
