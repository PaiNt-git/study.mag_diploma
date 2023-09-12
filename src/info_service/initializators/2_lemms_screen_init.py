from PyQt5 import QtCore, QtGui, QtWidgets

from collections import OrderedDict

from info_service import actions

from info_service.actions._lemms_utils import *


def main(main_window):

    columns = OrderedDict(
        [

            ('word', 'Отстемленная \nЛемма'),
            ('weight', 'Вес (Pg)'),
            ('weight_norm', 'Вес'),
            ('ndoc', 'Вхождений \nв ответе'),
            ('nentry', 'Вхождений \nза всю базу'),
            ('col_name', 'Колонка'),

        ])

    actions.win_CRUD_load_page(main_window, 'TableAllLemms', columns,
                               actions.db_list_all_lemms(),
                               )
