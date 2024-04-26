import time

from collections import OrderedDict

from PyQt5 import QtCore, QtGui, QtWidgets

from info_service import actions
from info_service.db_base import Session
from info_service.db_utils import togudb_serializator
from info_service.actions._answers_utils import q_k_result_format_override

from ._answers_utils import update_entity


def main(main_window, table_widget_name, entity, pk_colNum, dialog_title='Удалить экземпляр'):
    """

    :param main_window:
    :param table_widget_name:
    :param entity:
    :param pk_colNum:
    :param dialog_title:
    """

    session = Session()

    def init_dialog(dialog):
        dialog.setWindowTitle(dialog_title)
        pass

    def ok_dialog(dialog):
        table_widget = getattr(main_window, f'{table_widget_name}')
        cur_row = table_widget.currentRow()
        cur_rows = []

        selected = table_widget.selectedItems()
        if selected:
            for item in selected:
                rrow = item.row()
                pk = int(table_widget.item(rrow, pk_colNum).text())
                if pk and rrow not in cur_rows:
                    cur_rows.append(rrow)

        for cur_row in cur_rows:
            cell_val = int(table_widget.item(cur_row, pk_colNum).text())
            instance = session.query(entity).get(cell_val)
            session.delete(instance)
        session.flush()
        session.commit()
        pass

    main_window.open_second_window(init_callback=init_dialog,
                                   ok_callback=ok_dialog,
                                   dialog_ui='info_service_del_instance.ui',
                                   )
