#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtGui, QtWidgets, uic
import sys
import os
import GUI.icons
from LOGICS.Common import ApplicationLogic
from GUI.ModifiedWidgets import LoadWidget
from math import sqrt

QT_MAIN_GUI = 'GUI/MainGUI.ui'
Ui_MainWindow, QtBaseClass = uic.loadUiType(
    QT_MAIN_GUI,
    from_imports=True, import_from="GUI", resource_suffix=''
)


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    # расширения по умолчанию изображений, которые могут быть загружены
    # в программу
    SUPPORTED_EXT = ('.png', '.jpg', '.jpeg', '.tiff')
    # путь по умолчанию для диалогов открытия изображений
    IMAGE_PATH = os.path.abspath(os.path.dirname(sys.argv[0]))

    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)

        self.init_undoStack_dest()

        self.Ui_modify()
        self.app_logic = ApplicationLogic(parent=self)
        self.connect_widgets()

    def Ui_modify(self):
        self.configure_tabs()
        self.select_file_dialog = self.init_select_image_file_dialog()

        self.tab_src.widget_mpl.SUPPORTED_EXT = self.SUPPORTED_EXT
        self.tab_src.widget_mpl.label.setText(
            '<b><font size="20">Исходное изображение</font></b><br><br>'
            'Для открытия используйте drag&drop или <br>'
            'меню «Файл» - «Открыть исходное»'
        )

        self.tab_dest.widget_mpl.SUPPORTED_EXT = self.SUPPORTED_EXT
        self.tab_dest.widget_mpl.label.setText(
            '<b><font size="20">Маркированное изображение</font></b><br><br>'
            'Для открытия используйте drag&drop или <br>'
            'меню «Файл» - «Открыть маркированное»'
        )

        self.salt_and_pepper_settings = uic.loadUi(
            'GUI/SaltAndPepper.ui', QtWidgets.QDialog(self)
        )

        self.gaussian_noise_settings = uic.loadUi(
            'GUI/GaussianNoise.ui', QtWidgets.QDialog(self)
        )

    def init_undoStack_dest(self):
        self.undoStack_dest = QtWidgets.QUndoStack(self)
        self.action_redo_attack.triggered.connect(
            self.undoStack_dest.redo
        )
        self.action_undo_attack.triggered.connect(
            self.undoStack_dest.undo
        )


    def init_select_image_file_dialog(self):
        dialog = QtWidgets.QFileDialog(self)
        dialog.setFileMode(QtWidgets.QFileDialog.FileMode.ExistingFile)
        ext_with_star = ' '.join(['*' + ext for ext in self.SUPPORTED_EXT])
        dialog.setNameFilter(f"Images ({ext_with_star})")
        dialog.setViewMode(QtWidgets.QFileDialog.Detail)
        dialog.setDirectory(self.IMAGE_PATH)
        return dialog

    def handler_of_select_image_dialog(self, type_d=int()):
        if self.select_file_dialog.exec_():
            file = self.select_file_dialog.selectedFiles()[0]
            if type_d == 0:
                self.app_logic.load_src_image(file)
            elif type_d == 1:
                print(f'Загрузка ЦВЗ: {file}')
            elif type_d == 2:
                self.tabWidget_main.setCurrentIndex(type_d)
                message = ("Загрузка нового маркированного изображения очистит "
                           "стэк отмены/повтора атаки.\nВсе равно открыть изображение?")
                if (not self.undoStack_dest.count() or
                        QtWidgets.QMessageBox.question(
                            self, "Открыть маркированное изображение", message,
                            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
                        ) == QtWidgets.QMessageBox.Yes
                ):
                    self.undoStack_dest.clear()
                    self.app_logic.load_dest_image(file)


    def configure_tabs(self):
        """
        Загружает контент вкладок и устанавливает иконки
        """
        # у родителя появляются дочерние элементы
        LoadWidget('GUI/TabSrc.ui', self.tab_src)
        LoadWidget('GUI/TabSrc.ui', self.tab_watermark)
        LoadWidget('GUI/TabSrc.ui', self.tab_dest)
        LoadWidget('GUI/TabSrc.ui', self.tab_metrics)

        icons = ['src.svg', 'key.svg', 'dest.svg', 'metrics.svg']
        for i in range(len(icons)):
            icon = QtGui.QIcon()
            icon.addPixmap(
                QtGui.QPixmap(f":/icons/icons/{icons[i]}"),
                QtGui.QIcon.Normal,
                QtGui.QIcon.Off
            )
            self.tabWidget_main.setTabIcon(i, icon)
        self.tabWidget_main.setIconSize(QtCore.QSize(96, 96))

    def connect_widgets(self):
        """ Дополнительные коннекты для слотов, нуждающихся в сложной обработке """
        self.action_about.triggered.connect(self.show_about)
        self.tab_src.widget_mpl.dropped.connect(
            self.app_logic.load_src_image
        )
        self.tab_dest.widget_mpl.dropped.connect(
            self.app_logic.load_dest_image
        )
        self.action_open_src.triggered.connect(
            lambda: self.handler_of_select_image_dialog(type_d=0)
        )
        self.action_open_watermark.triggered.connect(
            lambda: self.handler_of_select_image_dialog(type_d=1)
        )
        self.action_dest.triggered.connect(
            lambda: self.handler_of_select_image_dialog(type_d=2)
        )

        self.action_salt_pepper.triggered.connect(
            lambda: self.attack_trigered(page=self.salt_and_pepper_settings)
        )

        self.action_gauss_noise.triggered.connect(
            lambda: self.attack_trigered(page=self.gaussian_noise_settings)
        )

        self.salt_and_pepper_settings.buttonBox_dialog.accepted.connect(
            lambda: self.app_logic.attack_to_image(
                type_a='s&p',
                amount=self.salt_and_pepper_settings.salt_spinBox.value() / 100,
                salt_vs_pepper=self.salt_and_pepper_settings.amount_spinBox.value() / 100
            )
        )

        self.salt_and_pepper_settings.salt_vs_pepper_Slider.valueChanged.connect(
            self.salt_vs_pepper_Slider_valueChanged
        )

        self.connect_gaussian_noise_settings()

    def connect_gaussian_noise_settings(self):
        """
        каждый раз возвращает дисперсию, на её основе
        будут переопределены другие виджеты
        """


        self.can_change_var = True
        def change_var(var: float):
            if self.can_change_var:
                self.can_change_var = False
                dev = sqrt(var)
                self.gaussian_noise_settings.var_doubleSpinBox.setValue(var)
                self.gaussian_noise_settings.var_Slider.setValue(int(var * 100))
                self.gaussian_noise_settings.dev_doubleSpinBox.setValue(dev)
                self.gaussian_noise_settings.dev_Slider.setValue(int(dev * 100))
                self.gaussian_noise_settings.dev_brightness_doubleSpinBox.setValue(dev * 255)
                self.can_change_var = True

        self.gaussian_noise_settings.var_doubleSpinBox.valueChanged.connect(change_var)
        self.gaussian_noise_settings.var_Slider.valueChanged.connect(lambda x: change_var(x / 100))
        self.gaussian_noise_settings.dev_doubleSpinBox.valueChanged.connect(lambda x: change_var(x**2))
        self.gaussian_noise_settings.dev_Slider.valueChanged.connect(lambda x: change_var((x / 100) ** 2))

        self.can_change_mean = True
        def change_mean(mean: float):
            if self.can_change_mean:
                self.can_change_mean = False
                self.gaussian_noise_settings.mean_doubleSpinBox.setValue(mean)
                self.gaussian_noise_settings.mean_Slider.setValue(int(mean * 100))
                self.gaussian_noise_settings.mean_brightness_doubleSpinBox.setValue(mean*255)
                self.can_change_mean = True

        self. gaussian_noise_settings.mean_doubleSpinBox.valueChanged.connect(change_mean)
        self. gaussian_noise_settings.mean_Slider.valueChanged.connect(lambda x: change_mean(x / 100))



        self.gaussian_noise_settings.buttonBox_dialog.accepted.connect(
            lambda: self.app_logic.attack_to_image(
                type_a='gaussian',
                mean=self.gaussian_noise_settings.mean_doubleSpinBox.value(),
                var=self.gaussian_noise_settings.var_doubleSpinBox.value()
            )
        )


    def show_about(self):
        """ Показ справки """
        if not hasattr(self, 'about'):
            self.about = uic.loadUi('GUI/About.ui', QtWidgets.QDialog(self))
        self.about.exec_()

    def show_error(self, title, message, more_info=''):
        if not hasattr(self, 'error_dialog'):
            self.error_dialog = QtWidgets.QMessageBox(self)
            self.error_dialog.setIcon(QtWidgets.QMessageBox.Critical)
        self.error_dialog.setWindowTitle(title)
        self.error_dialog.setText(message)
        if more_info:
            self.error_dialog.setInformativeText(more_info)
        self.error_dialog.exec_()

    def attack_trigered(self, page):
        if not self.app_logic.dest_image:
            self.show_error(
                title='Невозможно атакавать',
                message='Сначала загрузите маркированное изображение!',
                more_info='Атаки нужны для оценки устойчивости алгоритма маркирования '
                          'к внешним воздействиям. Для этого маркированное изображение '
                          'атакую, извлекают и оценивают качество полученного ЦВЗ.'
            )
            return 1

        page.exec_()

    def salt_vs_pepper_Slider_valueChanged(self):
        value = self.salt_and_pepper_settings.salt_vs_pepper_Slider.value()
        self.salt_and_pepper_settings.salt_spinBox.setValue(value + 50)
        self.salt_and_pepper_settings.pepper_spinBox.setValue(50 - value)



if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    # MainWindow.IMAGE_PATH = os.path.join(MainWindow.IMAGE_PATH, '../data')
    MainWindow.IMAGE_PATH = os.path.expanduser('~/General/Pictures')
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
