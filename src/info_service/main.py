#!/usr/bin/env python

import sys
import logging

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5 import uic

from info_service import actions

_old_stdout = sys.stdout
_override_stdout = sys.stdout


class _CustomFileLike():
    def __init__(self, qtmain_wind):
        self.qtmain_wind = qtmain_wind

    def write(self, string):

        text = self.qtmain_wind.ConsoleView.toPlainText()
        if text.count('\n') > 800:
            self.qtmain_wind.ConsoleView.setPlainText('')
        self.qtmain_wind.ConsoleView.insertPlainText(string)
        pass

    def flush(self):
        global _old_stdout
        sys.stdout = _old_stdout
        logger = logging.getLogger('info_service')
        logger.addHandler(logging.StreamHandler(stream=sys.stdout))


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        global _override_stdout
        super(MainWindow, self).__init__()
        uic.loadUi('info_service.ui', self)

        _override_stdout = _CustomFileLike(self)

        sys.stdout = _override_stdout

        logger = logging.getLogger('info_service')
        logger.setLevel(logging.DEBUG)
        logger.addHandler(logging.StreamHandler(stream=sys.stdout))

        self._init_program_event()

    def _init_program_event(self):

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
