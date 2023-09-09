import asyncio

from collections import OrderedDict

from PyQt5 import QtCore, QtGui, QtWidgets
import time

from info_service import actions


def main(main_window, table_widget_name, columns: OrderedDict, queryset, page_num=1):
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

    for i, item in enumerate(queryset):
        curc = table_widget.rowCount()
        table_widget.insertRow(curc)

        for k, col_key in enumerate(columns.keys()):
            table_widget.setItem(curc, k, QtWidgets.QTableWidgetItem(str(getattr(item, col_key, ''))))

    table_widget.setVerticalHeaderLabels(list(map(str, range(offset + 1, len(queryset) + offset + 1))))

    cur_page_widget.setText(str(page_num))
    max_page_widget.setText(str(max_page))

    pass
