#!/usr/bin/env python3
import os.path

from PIL import ImageOps
from PyQt5 import QtCore, QtGui, QtWidgets
import numpy as np
import PIL
import matplotlib.pyplot as plt
import matplotlib as mpl
import copy
import random
import math
# import cv2  # pip install opencv-python-headless
import skimage


class Picture:
    @staticmethod
    def define_image_by_path(img_path: str):
        image = PIL.Image.open(img_path)
        return np.array(image, dtype='uint8')

    # @staticmethod
    # def define_image_by_path_cv2(img_path: str):
    #     image = cv2.imread(img_path)
    #     image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    #     return image  # uint8

    def __init__(self, pixels: np.ndarray):
        self.pixels = pixels


class MarkedPicture(Picture):
    def __init__(self, pixels: np.ndarray):
        super().__init__(pixels)


# skimage.util.random_noise(img, mode=mode)
class ImageAttacks(object):
    """
    See also:
        https://scikit-image.org/docs/stable/api/skimage.util.html#skimage.util.random_noise
        https://theailearner.com/tag/skimage-util-random_noise/
        https://gist.github.com/Prasad9/28f6a2df8e8d463c6ddd040f4f6a028a
    """
    @staticmethod
    def salt_and_pepper(pixels: np.ndarray, amount=0.05, salt_vs_pepper=0.5):
        """
        :param amount: Доля зашумленности от 0 до 1
        :param salt_vs_pepper: Отношение соли к перцу от 0 до 1
        :rtype: np.ndarray(dtype='uint8')
        """
        img = skimage.util.random_noise(
            pixels, mode="s&p", amount=amount, salt_vs_pepper=salt_vs_pepper
        )
        return np.array(255 * img, dtype='uint8')

    @staticmethod
    def gaussian(pixels: np.ndarray, mean: float = 0, var: float = 0.01):
        """
        :param mean: Mean of random distribution
        :param var: Variance of random distribution.
                    Note: variance = (standard deviation) ** 2
        :rtype: np.ndarray(dtype='uint8')
        """
        img = skimage.util.random_noise(
            pixels, mode="gaussian", mean=mean, var=var
        )
        return np.array(255 * img, dtype='uint8')

    @staticmethod
    def speckle(pixels: np.ndarray, mean: float = 0, var: float = 0.01):
        """
        :param mean: Mean of random distribution
        :param var: Variance of random distribution.
                    Note: variance = (standard deviation) ** 2
        :rtype: np.ndarray(dtype='uint8')
        """
        img = skimage.util.random_noise(
            pixels, mode="speckle", mean=mean, var=var
        )
        return np.array(255 * img, dtype='uint8')


class ApplicationLogic:
    def __init__(
            self, parent=QtWidgets.QMainWindow
    ):
        self.parent = parent
        self.init_update_methods_for_gui()
        self.src_image: Picture = None  # self.load_src_image
        self.dest_image: MarkedPicture = None

    def init_update_methods_for_gui(self):
        """
        Инициализация простых методов обновления виджетов в интерфейсе.
        Сделано для удобства.
        :return:
            self.reload_src_image - метод, обновляющий виджет tab_src.widget_mpl
        """

        def reload_src_image(image_path='Image', update_title=True):
            """
            :param image_path: имя изображения для установки title
            :param update_title: обновлять ли существующий title
            """
            if update_title:
                self.parent.tab_src.widget_mpl.image_title = \
                    f'Исходное изображение: {os.path.basename(image_path)}'

            self.parent.tab_src.widget_mpl.update_image(
                self.src_image.pixels
            )

        def reload_dest_image(image_path='Image', update_title=True):
            """
            :param image_path: имя изображения для установки title
            :param update_title: обновлять ли существующий title
            """
            if update_title:
                self.parent.tab_dest.widget_mpl.image_title = \
                    f'Маркированное изображение: {os.path.basename(image_path)}'

            self.parent.tab_dest.widget_mpl.update_image(
                self.dest_image.pixels
            )

        self.reload_src_image = reload_src_image
        self.reload_dest_image = reload_dest_image

    def load_src_image(self, image_path):
        """
        Данный метод - слот для сигналов, испускающих путь к изображению
        :param image_path: str
        :return:
        """
        self.src_image = Picture(pixels=Picture.define_image_by_path(image_path))
        self.reload_src_image(image_path)

    def load_dest_image(self, image_path):
        """
        Данный метод - слот для сигналов, испускающих путь к изображению
        :param image_path: str
        :return:
        """
        self.dest_image = MarkedPicture(
            pixels=MarkedPicture.define_image_by_path(image_path)
        )
        self.reload_dest_image(image_path)

    def attack_to_image(self, type_a, *args, **kwargs):
        new_pixels = None
        if type_a == 's&p':
            new_pixels = ImageAttacks.salt_and_pepper(
                self.dest_image.pixels, *args, **kwargs
            )
        elif type_a == 'gaussian':
            new_pixels = ImageAttacks.gaussian(
                self.dest_image.pixels, *args, **kwargs
            )

        if type(new_pixels) == np.ndarray:
            old_image = self.dest_image
            new_image = MarkedPicture(pixels=new_pixels)
            command = UndoStackDestCommandAdd(self, old_image, new_image)
            self.parent.undoStack_dest.push(command)


class UndoStackDestCommandAdd(QtWidgets.QUndoCommand):
    def __init__(self, parent, old_image, new_image):
        """
        :param parent: app_logic
        :param old_image: class MarkedPicture
        :param new_image: class MarkedPicture
        """
        super(UndoStackDestCommandAdd, self).__init__()
        self.parent = parent
        self.old_image = old_image
        self.new_image = new_image

    def redo(self):
        """ Выполняется всегда при инициализации """
        self.parent.dest_image = self.new_image
        self.parent.reload_dest_image(update_title=False)

    def undo(self):
        self.parent.dest_image = self.old_image
        self.parent.reload_dest_image(update_title=False)
