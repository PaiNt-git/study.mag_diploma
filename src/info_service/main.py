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

from PyQt5 import QtWebEngineWidgets
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5 import uic  # , pyrcc
from PyQt5.QtWebEngineWidgets import QWebEngineView  # working with PyQt5 5.13.1


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
_all_inits_runned = False

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


class SecondWindow(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Диалоговое окно')
        super(SecondWindow, self).__init__()
        uic.loadUi(f'{PACKAGE_NAME}_dialog.ui', self)
        time.sleep(0.5)


class MainWindow(QtWidgets.QMainWindow):
    """
    Основное универсальное окно програмы
    """

    def __init__(self):
        """
        Загрузка инфтерфейса, присоединение обработчиков событий
        """
        self.MAINWINDOW_LOCAL_STORAGE = {}
        super(MainWindow, self).__init__()
        uic.loadUi(f'{PACKAGE_NAME}.ui', self)
        self._load_events_handlers()
        time.sleep(0.5)

    def open_second_window(self, ok_callback=None, cancel_callback=None):
        second_window = SecondWindow()
        setattr(second_window, 'main_window', self)

        if ok_callback:
            setattr(second_window.__class__, f'ok_callback', ok_callback)
            second_window.accepted.connect(getattr(second_window, f'ok_callback'))

        if cancel_callback:
            setattr(second_window.__class__, f'cancel_callback', cancel_callback)
            second_window.rejected.connect(getattr(second_window, f'cancel_callback'))

        second_window.exec_()

    def closeEvent(self, event):
        """
        Закрытие программы, закрытие потоков, плохо работает
        :param event:
        """
        print('closing..')

        window.stdout_write_loop = None
        window.program_init_loop = None
        window.program_actions_loop = None

        self._program_init_thread = None
        self._forever_run_stdout_write_thread = None
        self._forever_run_actions_loop_thread = None

        time.sleep(0.2)
        event.accept()

    def _load_events_handlers(self):
        """
        Присоединение обработчиков событий к окну
        """
        for event_name, callable_ in EVENT_PROVIDERS.items():
            callable_(self)
            print(f'\n+++>"{event_name}" handlers connected to MainWindow... ')

    async def _init_program_event(self):
        """
        Инициализаторы исполняющиеся в параллельном потоке программы
        """
        global _LOG_LAST_TIMESTAMP, _all_inits_runned

        ui_disable_clear_console = ACTION_PROVIDERS.get('ui_disable_clear_console', None)
        if ui_disable_clear_console:
            ui_disable_clear_console(self)

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

        ui_enable_clear_console = ACTION_PROVIDERS.get('ui_enable_clear_console', None)
        if ui_enable_clear_console:
            ui_enable_clear_console(self)

        _all_inits_runned = True


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
        _LOG_LAST_TIMESTAMP = 0
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


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    time.sleep(0.1)

    stdout_write_loop = asyncio.new_event_loop()
    program_init_loop = asyncio.new_event_loop()
    program_actions_loop = asyncio.new_event_loop()

    window.stdout_write_loop = stdout_write_loop
    window.program_init_loop = program_init_loop
    window.program_actions_loop = program_actions_loop

    _forever_run_stdout_write_thread = None
    _program_init_thread = None
    _forever_run_actions_loop_thread = None

    window._forever_run_stdout_write_thread = None
    window._program_init_thread = None
    window._forever_run_actions_loop_thread = None

    def forever_run_stdout_write_thread_target():
        """
        Евентлуп треда для принта
        https://stackoverflow.com/questions/29692250/restarting-a-thread-in-python
        """
        global window

        while True:
            try:
                asyncio.set_event_loop(stdout_write_loop)
                stdout_write_loop.run_forever()
            except BaseException as e:
                print('{!r}; restarting thread'.format(e))
            else:
                print('exited normally, bad thread; restarting')

    def program_event_thread_target():
        """
        Евентлуп треда загрузки инициализаторов
        """
        global window

        program_init_loop.run_until_complete(window._init_program_event())

    def forever_run_actions_thread_target():
        """
        Евентлуп треда для действий иницированных элементами гуя

        Исполнять неблокирующее ассинхронное действие в эвентпуле отдельного потока:
        asyncio.run_coroutine_threadsafe(coroutine(), window.program_actions_loop)

        """
        global window

        while True:
            try:
                asyncio.set_event_loop(program_actions_loop)
                program_actions_loop.run_forever()
            except BaseException as e:
                print('{!r}; restarting thread'.format(e))
            else:
                print('exited normally, bad thread; restarting')

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
            global _LOG_LAST_TIMESTAMP, window
            self.write_thread = threading.currentThread()

            if self.terminal:
                self.terminal.write(message)

            if message:
                try:
                    message = str(message)

                    set_to_field = False
                    if time.time() - _LOG_LAST_TIMESTAMP > 2:
                        set_to_field = True

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

    _forever_run_stdout_write_thread = threading.Thread(target=forever_run_stdout_write_thread_target, daemon=True)
    window._forever_run_stdout_write_thread = _forever_run_stdout_write_thread
    window._forever_run_stdout_write_thread.start()

    _forever_run_actions_loop_thread = threading.Thread(target=forever_run_actions_thread_target, daemon=True)
    window._forever_run_actions_loop_thread = _forever_run_actions_loop_thread
    window._forever_run_actions_loop_thread.start()

    _program_init_thread = threading.Thread(target=program_event_thread_target, daemon=True)
    window._program_init_thread = _program_init_thread
    window._program_init_thread.start()

    # Подождем пока последний созданный поток не отработает все иниты
    sleeper_count = 0
    while not _all_inits_runned and sleeper_count < 1:
        time.sleep(0.33)
        sleeper_count += 1

    del window  # Создадим запрос на удаление window но он из-за связанности с app не разрушится в момент работы app,
    #             но зато не произведет ошибку при выходе из программы (т.к. внутри QT ссылка на созданный поток)

    qtapp = app.exec()  # Блокирующая операция

    time.sleep(0.2)

    _forever_run_stdout_write_thread.join()
    time.sleep(0.1)
    _forever_run_actions_loop_thread.join()
    time.sleep(0.1)
    _program_init_thread.join()
    time.sleep(0.1)

    # del _forever_run_stdout_write_thread
    # del _forever_run_actions_loop_thread
    # del _program_init_thread

    time.sleep(1)

    del qtapp

    sys.exit()
