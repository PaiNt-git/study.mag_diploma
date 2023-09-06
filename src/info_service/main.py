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

            print(' ')
            pass


_LOG_LAST_TIMESTAMP = 0
_LOG_SAFE_QT_BUFFER = ''
_LOG_SAFE_QT_BUFFER_INFIELD = ''
_clearing_field_flag = False


async def write_to_window(qtmain_wind, message, set_to_field=False):
    global _LOG_LAST_TIMESTAMP, _LOG_SAFE_QT_BUFFER, _LOG_SAFE_QT_BUFFER_INFIELD, _clearing_field_flag
    if not message or message == '\n':
        return

    message = (message + '\n') if message != '\n' else '\n'

    if _LOG_SAFE_QT_BUFFER.count('\n') > 1000:
        _clearing_field_flag = True
        _LOG_SAFE_QT_BUFFER = ''
        _LOG_SAFE_QT_BUFFER_INFIELD = ''
        qtmain_wind.ConsoleView.clear()
        await asyncio.sleep(6.0)
        _clearing_field_flag = False

    _LOG_SAFE_QT_BUFFER = f'{_LOG_SAFE_QT_BUFFER}{message}'
    if set_to_field and not _clearing_field_flag:
        _LOG_LAST_TIMESTAMP = time.time()

        allen = len(_LOG_SAFE_QT_BUFFER)
        inflen = len(_LOG_SAFE_QT_BUFFER_INFIELD)
        if allen > inflen:
            insert = _LOG_SAFE_QT_BUFFER[-(allen - inflen):]

            chunks = [insert[i:i + 120] for i in range(0, len(insert), 120)]

            for cnk in chunks:
                if not cnk:
                    continue
                _LOG_SAFE_QT_BUFFER_INFIELD = f'{_LOG_SAFE_QT_BUFFER_INFIELD}{cnk}'
                qtmain_wind.ConsoleView.insertPlainText((' ' if cnk == '\n' else '') + cnk)

                await asyncio.sleep(2.0)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    time.sleep(0.1)

    stdout_write_loop = asyncio.new_event_loop()
    program_event_loop = asyncio.new_event_loop()

    def forever_run_stdout_write_thread_target():
        asyncio.set_event_loop(stdout_write_loop)
        stdout_write_loop.run_forever()

    def program_event_thread_target():
        program_event_loop.run_until_complete(window._init_program_event())

    class SysRedirect(object):
        def __init__(self, qtmain_wind):
            self.main_thread = threading.currentThread()
            self.write_thread = self.main_thread
            self.qtmain_wind = qtmain_wind
            self.terminal = sys.stdout       # To continue writing to terminal

        def write(self, message):
            global _LOG_LAST_TIMESTAMP
            self.write_thread = threading.currentThread()
            self.terminal.write(message)

            if message:
                try:
                    message = str(message)

                    set_to_field = False
                    if time.time() - _LOG_LAST_TIMESTAMP > 1:
                        set_to_field = True

                    future = asyncio.run_coroutine_threadsafe(write_to_window(self.qtmain_wind, message, set_to_field=set_to_field), stdout_write_loop)
                    # future.result()

                except Exception as e:
                    self.terminal.write(repr(e))

        def flush(self):
            # this flush method is needed for python 3 compatibility.
            # this handles the flush command by doing nothing.
            # you might want to specify some extra behavior here.
            stdout_write_loop.call_soon_threadsafe(stdout_write_loop.stop)
            pass

    sys.stdout = SysRedirect(window)

    logger = logging.getLogger('info_service')
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler(stream=sys.stdout))

    threading.Thread(target=forever_run_stdout_write_thread_target).start()
    threading.Thread(target=program_event_thread_target).start()

    sys.exit(app.exec())
