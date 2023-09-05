import sys
import time
import asyncio

from PyQt5 import QtCore, QtGui, QtWidgets

from info_service import actions


async def main(main_window):

    await asyncio.sleep(15)

    actions.keras()
