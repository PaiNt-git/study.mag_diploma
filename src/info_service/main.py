#!/usr/bin/env python

import os
import sys
import glob
import logging

from importlib import import_module

from inspect import isfunction

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5 import uic  # , pyrcc


MAIN_PACKAGE_DIR = os.path.abspath(os.path.join(os.path.split(str(__file__))[0]))
PACKAGE_NAME = os.path.basename(MAIN_PACKAGE_DIR)
sys.path.append(MAIN_PACKAGE_DIR)
sys.path.append(os.path.abspath(os.path.join(os.path.split(str(__file__))[0], '..')))


# Импорт корневых модулей программы

import info_service.db_base
import info_service.db_utils

# / Импорт корневых модулей программы

# Импорт динамических провайдеров, и их доимпортирование специально для pyInstaller

from info_service.actions import DYN_FUNC_PROVIDERS as ACTION_PROVIDERS
if not len(ACTION_PROVIDERS):
    _modules_actions = glob.glob(os.path.join(MAIN_PACKAGE_DIR, 'actions') + "/*.py")
    _modules_actions = [os.path.basename(x)[:-3] for x in _modules_actions if os.path.isfile(x)]
    _modules_actions = [x for x in _modules_actions if not x.startswith('_')]
    for _module_name in _modules_actions:
        _modul = import_module(f'{PACKAGE_NAME}.actions.{_module_name}')
        _provider = getattr(_modul, str('main'), None)
        if not _provider:
            _provider = getattr(_modul, str(_module_name), None)

        if isfunction(_provider):
            ACTION_PROVIDERS[_module_name] = _provider
            setattr(sys.modules[f'{PACKAGE_NAME}.actions'], _module_name, _provider)

from info_service.initializators import DYN_FUNC_PROVIDERS as INIT_PROVIDERS
if not len(INIT_PROVIDERS):
    _modules_initializators = glob.glob(os.path.join(MAIN_PACKAGE_DIR, 'initializators') + "/*.py")
    _modules_initializators = [os.path.basename(x)[:-3] for x in _modules_initializators if os.path.isfile(x)]
    _modules_initializators = [x for x in _modules_initializators if not x.startswith('_')]

    for _module_name in _modules_initializators:
        _modul = import_module(f'{PACKAGE_NAME}.initializators.{_module_name}')
        _provider = getattr(_modul, str('main'), None)
        if not _provider:
            _provider = getattr(_modul, str(_module_name), None)

        if isfunction(_provider):
            INIT_PROVIDERS[_module_name] = _provider
            setattr(sys.modules[f'{PACKAGE_NAME}.initializators'], _module_name, _provider)

# / Импорт динамических провайдеров, и их доимпортирование специально для pyInstaller


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
        for initializator, callable_ in INIT_PROVIDERS.items():
            callable_(self)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
