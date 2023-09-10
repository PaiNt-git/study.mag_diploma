import json
import asyncio

from collections import OrderedDict

from PyQt5 import QtCore, QtGui, QtWidgets
import time

from info_service.db_base import Session, QuestAnswerBase

from info_service.db_utils import togudb_serializator

from info_service import actions

from info_service.actions._answers_utils import *


def main(main_window):
    table_widget_name = 'TableInitialAllResults'

    initial_query_label_widget = getattr(main_window, f'LabelInitialQuery')
    initial_query_label_text = initial_query_label_widget.text()

    print(initial_query_label_text)
