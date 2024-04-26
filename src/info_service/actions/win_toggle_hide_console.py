import time

from collections import OrderedDict

from PyQt5 import QtCore, QtGui, QtWidgets


from info_service import actions
from info_service.db_base import Session, QuestAnswerBase


def main(main_window):
    is_checked = main_window.HideConsoleCheckBox.isChecked()

    if is_checked:
        main_window.ConsoleLabel.hide()
        main_window.ButtonClearConsole.hide()
        main_window.TextConsoleView.hide()
    else:
        main_window.ConsoleLabel.show()
        main_window.ButtonClearConsole.show()
        main_window.TextConsoleView.show()

    #===========================================================================
    # columns = OrderedDict(
    #     [
    #         ('questions', 'Вопросы \n(через точку с запятой)'),
    #         ('abstract', 'Контент\nАбстракт\nОтвет'),
    #     ])
    # actions.win_CRUD_new_instance(main_window, QuestAnswerBase, columns, 'Новое знание')
    # actions.win_answers_first_page(main_window)
    #===========================================================================

    #===========================================================================
    # actions.win_CRUD_del_instance(main_window, 'TableAllAnswers', QuestAnswerBase, 0, dialog_title='Удалить экземпляр')
    # actions.win_answers_first_page(main_window)
    #===========================================================================
