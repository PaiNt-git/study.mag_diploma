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

    initial_query_text_widget = getattr(main_window, f'TextInitialQuery')
    initial_query_text = initial_query_text_widget.toPlainText()

    initial_query_pgstemming_label_widget = getattr(main_window, f'LabelPostgresQueryLexStemming')
    initial_query_pgstemming_label_widget.setText(actions.db_get_searchterm_get_stemming(initial_query_text))
