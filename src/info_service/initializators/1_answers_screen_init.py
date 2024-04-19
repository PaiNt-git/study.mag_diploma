import json
import time

from PyQt5 import QtCore, QtGui, QtWidgets

from collections import OrderedDict

from info_service.db_base import Session, QuestAnswerBase

from info_service.db_utils import togudb_serializator

from info_service import actions

from info_service.actions._answers_utils import *


def main(main_window):
    time.sleep(0.2)
    actions.win_answers_first_page(main_window)
