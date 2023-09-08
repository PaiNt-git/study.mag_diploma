from collections import OrderedDict

from PyQt5 import QtCore, QtGui, QtWidgets
import time


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

    print(cur_page)
    print(max_page)

    table_widget = getattr(main_window, f'{table_widget_name}')

    rows_per_page = 100

    limit = rows_per_page
    offset = (page_num - 1) * rows_per_page

    if isinstance(queryset, list):
        queryset = queryset[offset:limit]
    else:
        queryset = queryset.limit(limit).offset(offset).all()

    all_items = len(queryset)

    table_widget.clear()

    time.sleep(0.7)

    table_widget.setColumnCount(len(columns))
    table_widget.setHorizontalHeaderLabels(columns.values())

    for i, item in enumerate(queryset):
        curc = table_widget.rowCount()
        table_widget.insertRow(curc)

        for k, col_key in enumerate(columns.keys()):
            table_widget.setItem(curc, k, QtWidgets.QTableWidgetItem(str(item[col_key])))

    pass
