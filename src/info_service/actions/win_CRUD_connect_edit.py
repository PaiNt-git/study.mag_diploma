import asyncio
import time

from typing import Callable

from collections import OrderedDict

from PyQt5 import QtCore, QtGui, QtWidgets

from info_service import actions

from ._answers_utils import get_cell_edit_callback, update_entity


def main(main_window, table_widget_name, columns: OrderedDict,
         queryset, row_map_callback=None, cell_edit_callback=None):
    """

    :param main_window:
    :param table_widget_name:
    :param columns:
    :param queryset:
    :param row_map_callback:
    :param cell_edit_callback: вызов будет cell_edit_callback(main_window, rowNum, colNum)
    """

    table_widget = getattr(main_window, f'{table_widget_name}')

    if cell_edit_callback and isinstance(cell_edit_callback, Callable):
        setattr(main_window.__class__, f'{table_widget_name}_cell_edit_callback', cell_edit_callback)
        table_widget.cellChanged[int, int].connect(getattr(main_window, f'{table_widget_name}_cell_edit_callback'))

    elif cell_edit_callback is None:
        cell_edit_callback = get_cell_edit_callback(main_window, table_widget_name, queryset, row_map_callback,
                                                    instance_edit_callback=update_entity)
        setattr(main_window.__class__, f'{table_widget_name}_cell_edit_callback', cell_edit_callback)
        table_widget.cellChanged[int, int].connect(getattr(main_window, f'{table_widget_name}_cell_edit_callback'))
