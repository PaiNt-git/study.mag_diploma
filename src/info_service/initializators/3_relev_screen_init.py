import time

from PyQt5 import QtCore, QtGui, QtWidgets

from collections import OrderedDict

from info_service import actions

from info_service.actions._lemms_utils import *


def main(main_window):
    time.sleep(0.2)
    actions.win_relev_query_first_page(main_window)
    time.sleep(0.2)
    actions.win_relev_first_page(main_window)
