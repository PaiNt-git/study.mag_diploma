from PyQt5 import QtCore, QtGui, QtWidgets

from info_service import actions


def main(main_window):

    col_keys = ('word', 'weight', 'weight_norm', 'ndoc', 'nentry', 'col_name',)
    for lemm in actions.db_list_all_lemms():
        curc = main_window.AllLemmsTable.rowCount()
        main_window.AllLemmsTable.insertRow(curc)
        for i, col_key in enumerate(col_keys):
            main_window.AllLemmsTable.setItem(curc, i, QtWidgets.QTableWidgetItem(str(lemm[col_key])))

    pass
