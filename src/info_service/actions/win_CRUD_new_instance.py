import time

from collections import OrderedDict

from PyQt5 import QtCore, QtGui, QtWidgets

from info_service import actions
from info_service.db_base import Session
from info_service.db_utils import togudb_serializator
from info_service.actions._answers_utils import q_k_result_format_override

from ._answers_utils import update_entity


def main(main_window, entity, columns, dialog_title='Новый экземпляр'):
    """

    :param main_window:
    :param entity:
    :param columns:
    :param dialog_title:
    """

    session = Session()

    table_widget_name = 'NewInstanceFields'

    def init_dialog(dialog):
        table_widget = getattr(dialog, f'{table_widget_name}')

        dialog.setWindowTitle(dialog_title)

        table_widget.clear()
        time.sleep(0.2)
        table_widget.setRowCount(0)

        table_widget.setColumnCount(len(columns))

        table_widget.setHorizontalHeaderLabels(columns.values())

        table_widget.verticalHeader().setDefaultSectionSize(120)

        table_widget.insertRow(0)

        for k, col_key in enumerate(columns.keys()):

            qtcell = QtWidgets.QTableWidgetItem('')

            #===============================================================================
            # The ** operator does exponentiation. a ** b is a raised to the b power. The same ** symbol is also used in function argument and calling notations, with a different meaning (passing and receiving arbitrary keyword arguments).
            # The ^ operator does a binary xor. a ^ b will return a value with only the bits set in a or in b but not both. This one is simple!
            # The % operator is mostly to find the modulus of two integers. a % b returns the remainder after dividing a by b. Unlike the modulus operators in some other programming languages (such as C), in Python a modulus it will have the same sign as b, rather than the same sign as a. The same operator is also used for the "old" style of string formatting, so a % b can return a string if a is a format string and b is a value (or tuple of values) which can be inserted into a.
            # The // operator does Python's version of integer division. Python's integer division is not exactly the same as the integer division offered by some other languages (like C), since it rounds towards negative infinity, rather than towards zero. Together with the modulus operator, you can say that a == (a // b)*b + (a % b).
            #===============================================================================

            table_widget.setItem(0, k, qtcell)

            qtcell.setFlags(qtcell.flags() | QtCore.Qt.ItemIsEditable)

        # table_widget.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
        table_widget.setWordWrap(True)
        table_widget.resizeColumnsToContents()
        table_widget.horizontalHeader().setStretchLastSection(True)

        for i in range(table_widget.columnCount()):
            if table_widget.columnWidth(i) > 200:
                if i <= len(columns) - 1:
                    table_widget.setColumnWidth(i, 200)
                    table_widget.verticalHeader().setDefaultSectionSize(120)
        pass

    def ok_dialog(dialog):
        table_widget = getattr(dialog, f'{table_widget_name}')
        instance = entity()

        def row_map_callback(x): return q_k_result_format_override(togudb_serializator(x, include=columns.keys(), exclude=['id']))

        has_notempty = False
        for i, key in enumerate(columns.keys()):
            try:
                ret = update_entity(table_widget, session, instance, row_map_callback, 0, i, session_add=False)
                if ret:
                    has_notempty = True
            except Exception as e:
                print(e)

        try:
            if has_notempty:
                session.add(instance)
                session.flush()
                session.commit()
        except Exception as e:
            print(e)

        main_window = dialog.main_window
        pass

    def cancel_dialog(dialog):
        pass

    main_window.open_second_window(init_callback=init_dialog,
                                   ok_callback=ok_dialog,
                                   cancel_callback=cancel_dialog,
                                   dialog_ui='info_service_new_instance.ui',
                                   )
