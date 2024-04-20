import asyncio
import time

from typing import Callable

from collections import OrderedDict

from PyQt5 import QtCore, QtGui, QtWidgets

from info_service import actions

from ._answers_utils import get_cell_edit_callback, update_entity


def main(main_window, table_widget_name, columns: OrderedDict,
         queryset, page_num=1, row_map_callback=None,
         cell_editable=(lambda queryset_row, qt_item: False)):
    """

    :param main_window:
    :param table_widget_name:
    :param columns:
    :param queryset:
    :param page_num:
    :param row_map_callback:
    :param cell_editable:
    """
    main_window.MAINWINDOW_LOCAL_STORAGE[f'_{table_widget_name}_paginate'] = 1

    cur_page_widget = getattr(main_window, f'CurPage{table_widget_name}')
    cur_page = int(cur_page_widget.text())

    max_page_widget = getattr(main_window, f'MaxPage{table_widget_name}')
    max_page = int(max_page_widget.text())

    if cur_page < 1:
        cur_page = 1

    if max_page < 1:
        max_page = 1

    if page_num > max_page:
        page_num = max_page

    if page_num < 1:
        page_num = 1

    table_widget = getattr(main_window, f'{table_widget_name}')

    rows_per_page = 100

    limit = rows_per_page
    offset = (page_num - 1) * rows_per_page

    if isinstance(queryset, list):
        all_items = len(queryset)
    else:
        all_items = queryset.count()

    max_page = (all_items // 100) + 1

    if isinstance(queryset, list):
        queryset = queryset[offset:limit + offset]
    else:
        queryset = queryset.limit(limit).offset(offset).all()

    table_widget.clear()
    time.sleep(0.2)
    table_widget.setRowCount(0)

    table_widget.setColumnCount(len(columns))

    table_widget.setHorizontalHeaderLabels(columns.values())

    table_widget.verticalHeader().setDefaultSectionSize(60)

    for i, row in enumerate(queryset):

        if row_map_callback:
            row = row_map_callback(row)

        curc = table_widget.rowCount()
        table_widget.insertRow(curc)

        for k, col_key in enumerate(columns.keys()):

            qtcell = QtWidgets.QTableWidgetItem(str(getattr(row, col_key, '')))

            #===============================================================================
            # The ** operator does exponentiation. a ** b is a raised to the b power. The same ** symbol is also used in function argument and calling notations, with a different meaning (passing and receiving arbitrary keyword arguments).
            # The ^ operator does a binary xor. a ^ b will return a value with only the bits set in a or in b but not both. This one is simple!
            # The % operator is mostly to find the modulus of two integers. a % b returns the remainder after dividing a by b. Unlike the modulus operators in some other programming languages (such as C), in Python a modulus it will have the same sign as b, rather than the same sign as a. The same operator is also used for the "old" style of string formatting, so a % b can return a string if a is a format string and b is a value (or tuple of values) which can be inserted into a.
            # The // operator does Python's version of integer division. Python's integer division is not exactly the same as the integer division offered by some other languages (like C), since it rounds towards negative infinity, rather than towards zero. Together with the modulus operator, you can say that a == (a // b)*b + (a % b).
            #===============================================================================

            table_widget.setItem(curc, k, qtcell)

            if cell_editable(row, qtcell):
                qtcell.setFlags(qtcell.flags() | QtCore.Qt.ItemIsEditable)
            else:
                qtcell.setFlags(qtcell.flags() & ~QtCore.Qt.ItemIsEditable)

    table_widget.setVerticalHeaderLabels(list(map(str, range(offset + 1, len(queryset) + offset + 1))))

    cur_page_widget.setText(str(page_num))
    max_page_widget.setText(str(max_page))

    table_widget.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
    table_widget.setWordWrap(True)
    table_widget.resizeColumnsToContents()
    table_widget.horizontalHeader().setStretchLastSection(True)

    for i in range(table_widget.columnCount()):
        if table_widget.columnWidth(i) > 200:
            if i <= len(columns) - 1:
                table_widget.setColumnWidth(i, 200)
                table_widget.verticalHeader().setDefaultSectionSize(100)

    main_window.MAINWINDOW_LOCAL_STORAGE[f'_{table_widget_name}_paginate'] = 0
