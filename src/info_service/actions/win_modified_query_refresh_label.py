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

    modified_query_text_widget = getattr(main_window, f'TextModifiedQuery')
    modified_query_text = modified_query_text_widget.toPlainText()

    modified_query_label_widget = getattr(main_window, f'LabelModifiedQuery')
    modified_query_label_text = modified_query_label_widget.setText(modified_query_text)
