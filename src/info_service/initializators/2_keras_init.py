import sys
import time
import asyncio

from PyQt5 import QtCore, QtGui, QtWidgets

from info_service import actions


async def main(main_window):

    print('before')

    await asyncio.sleep(15)

    print('after')

    actions.keras()
