#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import numpy as np
# красивый таб с закрывающимися вкладками
# https://stackoverflow.com/questions/57305452/add-icon-to-tab-qtabwidget

from PyQt5 import QtCore, QtGui, QtWidgets, uic

import matplotlib as mpl
import matplotlib.pyplot as plt

mpl.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas, \
    NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure


# -----------------------------------------------------
class TabBar(QtWidgets.QTabBar):
    def tabSizeHint(self, index):
        s = QtWidgets.QTabBar.tabSizeHint(self, index)
        s.transpose()
        return s

    def paintEvent(self, event):
        painter = QtWidgets.QStylePainter(self)
        opt = QtWidgets.QStyleOptionTab()

        colors = 'lightgray lightgreen skyblue orange yellow plum tomato'.split()
        for i in range(self.count()):
            self.initStyleOption(opt, i)
            bgcolor = QtGui.QColor(colors[i % len(colors)])
            opt.palette.setColor(QtGui.QPalette.Window, bgcolor)
            opt.palette.setColor(QtGui.QPalette.Button, bgcolor)

            painter.drawControl(QtWidgets.QStyle.CE_TabBarTabShape, opt)
            painter.save()

            s = opt.rect.size()
            s.transpose()
            r = QtCore.QRect(QtCore.QPoint(), s)
            r.moveCenter(opt.rect.center())
            opt.rect = r

            c = self.tabRect(i).center()
            painter.translate(c)
            painter.rotate(90)
            painter.translate(-c)
            painter.drawControl(QtWidgets.QStyle.CE_TabBarTabLabel, opt)
            painter.restore()


class VerticalTabWidget(QtWidgets.QTabWidget):
    """
    Перевернутый на 90 градусов аналог QtWidgets.QTabWidget
    """

    def __init__(self, *args, **kwargs):
        QtWidgets.QTabWidget.__init__(self, *args, **kwargs)
        self.setTabBar(TabBar())
        self.setTabPosition(QtWidgets.QTabWidget.West)


# -----------------------------------------------------
class ImageLabel(QtWidgets.QLabel):
    dropped = QtCore.pyqtSignal(str)

    def __init__(self, widget):
        super(ImageLabel, self).__init__(widget)
        self.setAcceptDrops(True)
        self.setAlignment(QtCore.Qt.AlignCenter)
        self.setStyleSheet('''
            QLabel{
                border: 4px dashed #aaa
            }
        ''')
        # self.setText(f"\n\n {label} \n\n")

    def dragEnterEvent(self, event):
        if len(event.mimeData().urls()) == 1:
            file_name = event.mimeData().text().replace('\r\n', '')
            if file_name.lower().endswith(('.png', '.jpg', '.jpeg')):
                event.acceptProposedAction()
                return
        event.ignore()

    def dropEvent(self, event):
        self.setStyleSheet('')
        file_path = event.mimeData().urls()[0].toString().replace('file://', '')
        self.setPixmap(QtGui.QPixmap(file_path))
        self.setScaledContents(True)
        self.dropped.emit(str(file_path))


# -----------------------------------------------------
class LoadWidget(QtWidgets.QWidget):
    def __init__(self, ui_file, parent):
        """
        Загрузка ui типа виджет и его привязка к родителю
        Пока используется для хранения контента tab-ов раздельно с MainWindow
        """
        super(LoadWidget, self).__init__()
        uic.loadUi(ui_file, parent)


# -----------------------------------------------------

# Следует добавить в layout информацию об изображении и скомпоновать
# с другим layout её с toolbar-ом (чего месту за зря пропадать?!)

class MplCanvas(QtWidgets.QWidget):
    SUPPORTED_EXT = tuple()
    # сигнал и его возвращаемые значения
    dropped = QtCore.pyqtSignal(str)

    def __init__(
            self, parent=None,
            image_title='Title', figsize=(5, 5), dpi=100,
            toolbar_need=True
    ):
        super(MplCanvas, self).__init__()
        self.image_title = image_title
        self.figsize = dict(
            width=figsize[0],
            height=figsize[1]
        )
        self.dpi = dpi
        self.toolbar_need = toolbar_need
        self.SUPPORTED_EXT = MplCanvas.SUPPORTED_EXT

        self.layout = QtWidgets.QVBoxLayout()
        self.label = QtWidgets.QLabel(self.image_title, self)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setWordWrap(True)
        self.layout.addWidget(self.label)
        self.setLayout(self.layout)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        if len(event.mimeData().urls()) == 1:
            file_name = event.mimeData().text().replace('\r\n', '')
            if file_name.lower().endswith(self.SUPPORTED_EXT):
                event.acceptProposedAction()
                return
        event.ignore()

    def dropEvent(self, event):
        file_path = event.mimeData().urls()[0].toString().replace('file://', '')
        # self.update_image(file_path)
        self.dropped.emit(str(file_path))

    def update_image(self, pixels: np.array):
        """
        Т.к. пиксели представлены внутренней структурой, обновление
        следует вызывать явно. Первоначально предполагалось, что
        будет использован MVC подход, однако мой уровень познания qt
        недостаточно высок, чтобы грамотно определить и модель,
        и нестандартное отображение. Поэтому сим немодульный подход,
        который допустимо применим к несложным gui, как этот.
        :param pixels: пиксели для отрисовки
        """
        self.img = pixels
        self.delete_widgets_of_layout()
        self.fig, self.axes = plt.subplots(
            nrows=1, ncols=1,
            figsize=(self.figsize['width'], self.figsize['height']),
            dpi=self.dpi
        )

        plt.imshow(self.img)  # .astype(np.uint8))
        plt.axis('off')
        plt.gca().set_position((0, 0, 1, 0.9))  # plt.tight_layout()
        plt.suptitle(self.image_title, fontweight='bold', fontsize=16)
        self.canvas_fig = FigureCanvas(self.fig)

        self.layout.addWidget(self.canvas_fig)
        if self.toolbar_need:
            self.toolbar = NavigationToolbar(self.canvas_fig, self)
            self.layout.addWidget(self.toolbar)
        self.setLayout(self.layout)  # обновить

    def delete_widgets_of_layout(self):
        while self.layout.count():
            child = self.layout.takeAt(0)
            widgetToRemove = child.widget()
            if widgetToRemove:
                self.layout.removeWidget(widgetToRemove)
                widgetToRemove.setParent(None)