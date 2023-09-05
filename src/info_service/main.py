#!/usr/bin/env python

import threading
import asyncio
import time
import os
import sys
import glob
import logging

from importlib import import_module

from inspect import isfunction, iscoroutinefunction

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


class SysRedirect(object):
    def __init__(self, qtmain_wind):
        self.qtmain_wind = qtmain_wind
        self.terminal = sys.stdout       # To continue writing to terminal

    def write(self, message):
        text = self.qtmain_wind.ConsoleView.toPlainText()
        if text.count('\n') > 800:
            self.qtmain_wind.ConsoleView.setPlainText('')
        self.qtmain_wind.ConsoleView.insertPlainText(message)

    def flush(self):
        # this flush method is needed for python 3 compatibility.
        # this handles the flush command by doing nothing.
        # you might want to specify some extra behavior here.
        pass


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        uic.loadUi('info_service.ui', self)

    async def _init_program_event(self):

        # Импорт динамических провайдеров, и их доимпортирование специально для pyInstaller

        from info_service.actions import DYN_FUNC_PROVIDERS as ACTION_PROVIDERS
        if not len(ACTION_PROVIDERS):
            _modules_actions = glob.glob(os.path.join(MAIN_PACKAGE_DIR, 'actions', "*.py"))
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
            _modules_initializators = glob.glob(os.path.join(MAIN_PACKAGE_DIR, 'initializators', "*.py"))
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

        for initializator, callable_ in INIT_PROVIDERS.items():
            if iscoroutinefunction(callable_):
                await callable_(self)
            else:
                callable_(self)
            pass


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    time.sleep(0.1)

    sys.stdout = SysRedirect(window)

    logger = logging.getLogger('info_service')
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler(stream=sys.stdout))

    time.sleep(0.2)

    program_event_loop = asyncio.new_event_loop()

    def thread_target():
        program_event_loop.run_until_complete(window._init_program_event())

    threading.Thread(target=thread_target).start()

    sys.exit(app.exec())
