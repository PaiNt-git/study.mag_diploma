from PyQt5 import QtCore, QtGui, QtWidgets

from collections import OrderedDict

from info_service import actions

from info_service.actions._lemms_utils import *


def main(main_window):
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
    )
