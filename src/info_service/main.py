#!/usr/bin/env python

import sys

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5 import uic

from info_service import actions


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        uic.loadUi('info_service.ui', self)
        self._init_program_event()

    def _init_program_event(self):
        lemms = actions.db_list_all_lemms()

        col_keys = ('word', 'weight', 'weight_norm', 'ndoc', 'nentry', 'col_name',)
        for lemm in actions.db_list_all_lemms():
            curc = self.AllLemmsTable.rowCount()
            self.AllLemmsTable.insertRow(curc)
            for i, col_key in enumerate(col_keys):
                self.AllLemmsTable.setItem(curc, i, QtWidgets.QTableWidgetItem(str(lemm[col_key])))


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
