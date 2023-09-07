#!/usr/bin/env python

import threading
import asyncio
import time
import os
import sys
import glob
import logging
import pathlib

from importlib import import_module

from inspect import isfunction, iscoroutinefunction

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5 import uic  # , pyrcc


if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    os.environ["PYMORPHY2_DICT_PATH"] = str(pathlib.Path(sys._MEIPASS).joinpath('pymorphy2_dicts_ru/data'))


MAIN_PACKAGE_DIR = os.path.abspath(os.path.join(os.path.split(str(__file__))[0]))
PACKAGE_NAME = os.path.basename(MAIN_PACKAGE_DIR)
sys.path.append(MAIN_PACKAGE_DIR)
sys.path.append(os.path.abspath(os.path.join(os.path.split(str(__file__))[0], '..')))


# Импорт корневых модулей программы

import info_service.db_base
import info_service.db_utils

# / Импорт корневых модулей программы


_LOG_LAST_TIMESTAMP = 0
_LOG_SAFE_QT_BUFFER = ''
_LOG_SAFE_QT_BUFFER_INFIELD = ''
_clearing_field_flag = False


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


from info_service.events import DYN_FUNC_PROVIDERS as EVENT_PROVIDERS
if not len(EVENT_PROVIDERS):
    _modules_events = glob.glob(os.path.join(MAIN_PACKAGE_DIR, 'events', "*.py"))
    _modules_events = [os.path.basename(x)[:-3] for x in _modules_events if os.path.isfile(x)]
    _modules_events = [x for x in _modules_events if not x.startswith('_')]

    for _module_name in _modules_events:
        _modul = import_module(f'{PACKAGE_NAME}.events.{_module_name}')
        _provider = getattr(_modul, str('main'), None)
        if not _provider:
            _provider = getattr(_modul, str(_module_name), None)

        if isfunction(_provider):
            EVENT_PROVIDERS[_module_name] = _provider
            setattr(sys.modules[f'{PACKAGE_NAME}.events'], _module_name, _provider)


# / Импорт динамических провайдеров, и их доимпортирование специально для pyInstaller


class MainWindow(QtWidgets.QMainWindow):
    """
    Основное универсальное окно програмы
    """

    def __init__(self):
        """
        Загрузка инфтерфейса, присоединение обработчиков событий
        """
        super(MainWindow, self).__init__()
        uic.loadUi(f'{PACKAGE_NAME}.ui', self)
        self._load_events_handlers()

    def closeEvent(self, event):
        """
        Закрытие программы, закрытие потоков, плохо работает
        :param event:
        """
        print('closing...')
        #self._forever_run_stdout_write_thread.join()
        event.accept()

    def _load_events_handlers(self):
        """
        Присоединение обработчиков событий к окну
        """
        for event_name, callable_ in EVENT_PROVIDERS.items():
            callable_(self)
            print(f'\n+++>"{event_name}" init connected to MainWindow... ')

    async def _init_program_event(self):
        """
        Инициализаторы исполняющиеся в параллельном потоке программы
        """
        global _LOG_LAST_TIMESTAMP

        for init_name, callable_ in INIT_PROVIDERS.items():
            if iscoroutinefunction(callable_):
                await callable_(self)
            else:
                clcor = asyncio.coroutine(callable_)
                await clcor(self)

            _LOG_LAST_TIMESTAMP = 0
            print(f'\n---> "{init_name}" init executed... \n')

        _LOG_LAST_TIMESTAMP = 0
        print(f'\n--->>> ALL init executed... \n')


def write_to_window_s(qtmain_wind, message, set_to_field=False):
    """
    Функция обработки sys.stdout.write(), перегрузка глобальная перегрузка вывода для присоединенных процедур

    :param qtmain_wind:
    :param message:
    :param set_to_field:
    """
    assert message

    global _LOG_LAST_TIMESTAMP, _LOG_SAFE_QT_BUFFER, _LOG_SAFE_QT_BUFFER_INFIELD, _clearing_field_flag
    if not message:
        return

    # Очитка поле после 1000 строк. После стирания в виджете QT подождем
    if _LOG_SAFE_QT_BUFFER_INFIELD.count('\n') > 1000 or message == '[main_window.clear_console]':
        _clearing_field_flag = True
        _LOG_SAFE_QT_BUFFER = ''
        _LOG_SAFE_QT_BUFFER_INFIELD = ''
        qtmain_wind.TextConsoleView.clear()
        time.sleep(6.0)
        _clearing_field_flag = False

    _LOG_SAFE_QT_BUFFER = f'{_LOG_SAFE_QT_BUFFER}{message}'
    if set_to_field and not _clearing_field_flag:
        _LOG_LAST_TIMESTAMP = time.time()

        allen = len(_LOG_SAFE_QT_BUFFER)
        inflen = len(_LOG_SAFE_QT_BUFFER_INFIELD)
        if allen > inflen:
            insert = _LOG_SAFE_QT_BUFFER[-(allen - inflen):]

            # Не забивать в insertPlainText больше 800 символов за раз
            chunks = [insert[i:i + 800] for i in range(0, len(insert), 800)]

            for cnk in chunks:
                if not cnk:
                    continue
                _LOG_SAFE_QT_BUFFER_INFIELD = f'{_LOG_SAFE_QT_BUFFER_INFIELD}{cnk}'
                qtmain_wind.TextConsoleView.insertPlainText((' ' if cnk == '\n' else '') + cnk)

                # Кажется что без задержек у меня все вылетает, но это стоит потом отладить, заебался уже. работает - не трогай!
                time.sleep(0.5)

    if _LOG_SAFE_QT_BUFFER.strip() != _LOG_SAFE_QT_BUFFER_INFIELD.strip():
        ui_disable_clear_console = ACTION_PROVIDERS.get('ui_disable_clear_console', None)
        if ui_disable_clear_console:
            ui_disable_clear_console(qtmain_wind)
    elif set_to_field:
        ui_enable_clear_console = ACTION_PROVIDERS.get('ui_enable_clear_console', None)
        if ui_enable_clear_console:
            ui_enable_clear_console(qtmain_wind)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    time.sleep(0.1)

    stdout_write_loop = asyncio.new_event_loop()
    program_event_loop = asyncio.new_event_loop()

    window.stdout_write_loop = stdout_write_loop
    window.program_event_loop = program_event_loop

    window._forever_run_stdout_write_thread = None
    window._program_event_thread = None

    def forever_run_stdout_write_thread_target():
        """
        Евентлуп треда для принта
        https://stackoverflow.com/questions/29692250/restarting-a-thread-in-python
        """
        while True:
            try:
                asyncio.set_event_loop(stdout_write_loop)
                stdout_write_loop.run_forever()
            except BaseException as e:
                print('{!r}; restarting thread'.format(e))
            else:
                print('exited normally, bad thread; restarting')

            ui_enable_clear_console = ACTION_PROVIDERS.get('ui_enable_clear_console', None)
            if ui_enable_clear_console:
                ui_enable_clear_console(window)

    def program_event_thread_target():
        """
        Евентлуп треда загрузки инициализаторов
        """
        program_event_loop.run_until_complete(window._init_program_event())

    class SysRedirect(object):
        """
        Класс-перегрузка sys.stdout
        """

        def __init__(self, qtmain_wind):
            self.main_thread = threading.currentThread()
            self.write_thread = self.main_thread
            self.qtmain_wind = qtmain_wind
            self.terminal = sys.stdout       # To continue writing to terminal

        def write(self, message):
            global _LOG_LAST_TIMESTAMP
            self.write_thread = threading.currentThread()

            if self.terminal:
                self.terminal.write(message)

            if message:
                try:
                    message = str(message)

                    set_to_field = False
                    if time.time() - _LOG_LAST_TIMESTAMP > 2:
                        set_to_field = True

                    #===========================================================
                    # looprunn = stdout_write_loop.is_running()
                    # threadalive = (window._forever_run_stdout_write_thread and window._forever_run_stdout_write_thread.is_alive())
                    # if not looprunn or not threadalive:
                    #     window._forever_run_stdout_write_thread.run()
                    #===========================================================

                    handle = stdout_write_loop.call_soon_threadsafe(write_to_window_s, self.qtmain_wind, message, set_to_field, context=None)

                except Exception as e:
                    if self.terminal:
                        self.terminal.write(f'Write exception: {e!r}')

        def flush(self):
            # this flush method is needed for python 3 compatibility.
            # this handles the flush command by doing nothing.
            # you might want to specify some extra behavior here.
            stdout_write_loop.call_soon_threadsafe(stdout_write_loop.stop)
            pass

    sys.stdout = SysRedirect(window)

    logger = logging.getLogger(f'{PACKAGE_NAME}')
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler(stream=sys.stdout))

    window._forever_run_stdout_write_thread = threading.Thread(target=forever_run_stdout_write_thread_target, daemon=True)
    window._forever_run_stdout_write_thread.start()

    window._program_event_thread = threading.Thread(target=program_event_thread_target)
    window._program_event_thread.start()

    sys.exit(app.exec())
