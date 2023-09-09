import asyncio

from collections import OrderedDict

from PyQt5 import QtCore, QtGui, QtWidgets
import time

from info_service import actions


def main(main_window, table_widget_name):

    cur_page_widget = getattr(main_window, f'CurPage{table_widget_name}')
    cur_page = int(cur_page_widget.text())

    max_page_widget = getattr(main_window, f'MaxPage{table_widget_name}')
    max_page = int(max_page_widget.text())

    actions.win_CRUD_load_page(main_window, 'TableAllLemms', OrderedDict(
        [
            ('word', 'Лемма'),
            ('weight', 'Вес (Pg)'),
            ('weight_norm', 'Вес'),
            ('ndoc', 'Вхождений в ответе'),
            ('nentry', 'Вхождений за всю базу'),
            ('col_name', 'Колонка'),

        ]),
        actions.db_list_all_lemms(),
        page_num=1,
    )
