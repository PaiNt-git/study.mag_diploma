import os
import sys
import re
import itertools
import glob
import random

import numpy as np
import matplotlib.pyplot as plt
import tensorflow.keras as keras

from collections import defaultdict

from sklearn.preprocessing import OneHotEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix


ETALON_PIXEL_DATA = defaultdict(list)

MATRIX_MAX_X = 0
MATRIX_MAX_Y = 0
SIZE_OF_ONE_IMAGE = 0


def notempty(x): return bool(x and not x.isspace())


def lchunks(lst, n):
    for i_ in range(0, len(lst), n):
        yield lst[i_:i_ + n]


def __pixels_load(filepath, moduletdict):
    with open(filepath, 'r') as fl:
        counter = 0
        for line in fl.readlines():
            if counter > 10:
                fl.close()
                return
            if notempty(line):
                line = line.strip()
                moduletdict[counter].append(line)
            else:
                counter += 1


__pixels_load('datasets/lab3/etalon.txt', ETALON_PIXEL_DATA)

if len(ETALON_PIXEL_DATA):
    MATRIX_MAX_X = len(ETALON_PIXEL_DATA[0][0])
    MATRIX_MAX_Y = len(ETALON_PIXEL_DATA[0])
    SIZE_OF_ONE_IMAGE = MATRIX_MAX_X * MATRIX_MAX_Y


DEFAULT_OH_ENCODER = OneHotEncoder(categories='auto')
LABELS_ONE_HOT_VECTORS = DEFAULT_OH_ENCODER.fit_transform(
    np.array(list(ETALON_PIXEL_DATA.keys())).reshape((-1, 1))
).toarray()


class NNDigitRecogniteModel:
    """
    Класс Нейронной сети для распознавания
    """

    def __init__(self, digits_in_line: int=1, nn_key: str='main'):
        """
        Модель с определенным алиасом должна создаваться один раз
        """

        self.nn_key = nn_key
        self.digits_in_line = digits_in_line
        self.encoder = DEFAULT_OH_ENCODER

        if os.path.isfile(f'datasets/lab3/keras_train_model_{self.nn_key}{self.digits_in_line}.bin'):
            self.model = keras.models.load_model(f'datasets/lab3/keras_train_model_{self.nn_key}{self.digits_in_line}.bin')
        else:
            self.model = keras.Sequential()

            self.model.add(keras.layers.Dense(input_shape=(SIZE_OF_ONE_IMAGE * digits_in_line,), units=128, activation='relu'))
            self.model.add(keras.layers.Dense(10 * digits_in_line, activation='softmax'))

            self.model.summary()

            self.model.compile(optimizer='sgd',
                               loss='categorical_crossentropy',
                               metrics=['accuracy'])

        self.labels_vect_dataset = []
        self.images_vect_dataset = []

        self.X_train, self.X_test, self.y_train, self.y_test = None, None, None, None,

    def _dataset_to_ndarray(self):
        if len(self.labels_vect_dataset) and isinstance(self.labels_vect_dataset, list):
            self.labels_vect_dataset = np.array(self.labels_vect_dataset)

        if len(self.images_vect_dataset) and isinstance(self.images_vect_dataset, list):
            self.images_vect_dataset = np.array(self.images_vect_dataset)

    def _dataset_to_traintest(self):
        self._dataset_to_ndarray()
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(self.images_vect_dataset, self.labels_vect_dataset)

    def nn_fit(self):
        self._dataset_to_traintest()
        self.model.fit(self.X_train, self.y_train, epochs=60, batch_size=128)
        self.model.save(f'datasets/lab3/keras_train_model_{self.nn_key}{self.digits_in_line}.bin')
        self.model.evaluate(self.X_test, self.y_test)

    def nn_predict(self, image_vectors=[]):
        image_vectors_ = image_vectors
        if not isinstance(image_vectors, (list, tuple, )):
            image_vectors_ = [image_vectors]

        images_vect = np.array(list(itertools.chain.from_iterable(image_vectors_)))

        if len(images_vect) != self.digits_in_line * SIZE_OF_ONE_IMAGE:
            raise ValueError

        return self.model.predict(images_vect.reshape((1, -1)))

    def nn_predicted_digit_and_prob(self, image_vectors=[]):
        ret = self.nn_predict(image_vectors)

        ret = ret.tolist()[0]

        label = int(np.argmax(ret))
        prob = ret[label]

        return label, prob

    def add_to_dataset(self, labels=[], image_vectors=[]):
        if not isinstance(labels, (list, tuple, )):
            labels = [labels]
            if not isinstance(image_vectors, (list, tuple, )):
                image_vectors = [image_vectors]

        if len(labels) != self.digits_in_line or len(image_vectors) != self.digits_in_line:
            raise ValueError

        none_labels_vect_data = len(LABELS_ONE_HOT_VECTORS[0])
        none_labels_vect_data = list(itertools.repeat(0, none_labels_vect_data))
        none_labels_vect_data = np.array(none_labels_vect_data)

        def get_lab_vect(label):
            if label is None:
                return none_labels_vect_data
            return LABELS_ONE_HOT_VECTORS[label]

        labels_vect = list(itertools.chain.from_iterable(map(get_lab_vect, labels)))
        images_vect = list(itertools.chain.from_iterable(image_vectors))

        self.labels_vect_dataset.append(labels_vect)
        self.images_vect_dataset.append(images_vect)


NEURAL_MODEL_REGISTRY = {}


class NNPixelDigit:
    """
    Класс цифры
    """

    def __init__(self, string_with_lb: str, label: int=None, nn_key: str='main'):
        """
        Инициализация с текстом с обрывами строк в котором записаны пиксели.

        Элемент self._pixel_data: [
        '*******',
        '*....*',
        '*....*',
        '*....*',
        '*....*',
        '*....*',
        '*******',
        ]

        :param string_with_lb: строка с обрывами в которой закодировано изображение одной цифры
        :param label: метка, которой соотвествует изображение, если не задано это не обучающий инстанс
        :param nn_key: инстанс нейронной сети из реестра модуля
        """
        self._pixel_data = list(map(lambda x: x.strip(), string_with_lb.splitlines()))
        if nn_key + str(1) not in NEURAL_MODEL_REGISTRY:
            NEURAL_MODEL_REGISTRY[nn_key + str(1)] = NNDigitRecogniteModel(1, nn_key)

        self.nn = NEURAL_MODEL_REGISTRY[nn_key + str(1)]

        self.image_vect = self.bin_vectorize_block()
        self.label = label
        self.label_vect = self.bin_vectorize_label()

    def bin_vectorize_block(self):
        """
        С помощью numpy предстваить список "пикселей" как бинарный вектор
        """
        return np.array(list(map(lambda x: 1 if x == '*' else 0, itertools.chain.from_iterable(self._pixel_data))))

    def bin_vectorize_label(self):
        """
        С помощью sklearn предстваить метку как бинарный вектор, используем One-Hot кодирование (датасет для различий - все эталоны)
        """
        if not self.label:
            return None
        return LABELS_ONE_HOT_VECTORS[self.label]

    def plot_image(self):
        """
        Нарисовать картинку из вектора изображения
        """
        plt.imshow(self.image_vect.reshape((MATRIX_MAX_Y, MATRIX_MAX_X)), cmap='gray')
        plt.show()


class Clock:
    """
    Класс Показаний часов
    """

    def devide_digits(self, string_time: str):
        """
        Разделить введенные цифры на группы

        :param string_time:
        """
        lipixels = string_time.splitlines(False)

        maxx = MATRIX_MAX_X
        maxy = MATRIX_MAX_Y

        time_digits = defaultdict(str)

        for i in range(len(lipixels)):
            lipixels[i] = re.sub('[^.*]+', '', lipixels[i])

            cnks = list(lchunks(lipixels[i], maxx))

            time_digits[0] = '\n'.join([time_digits[0], cnks[0]]).strip()
            time_digits[1] = '\n'.join([time_digits[1], cnks[1]]).strip()
            time_digits[2] = '\n'.join([time_digits[2], cnks[2]]).strip()
            time_digits[3] = '\n'.join([time_digits[3], cnks[3]]).strip()

        return time_digits[0], time_digits[1], time_digits[2], time_digits[3]

    def __init__(self, string_time: str, nn_key: str='main'):
        """
        Передаем значение показаний записанное с пробельными разделитлями, 4 цифры, по типу:

        ******      ******              ******      ******
        *....*      *....*              *....*      *....*
        .....*      *....*              *....*      *....*
        *....*      *....*      +       *....*      *.....
        *....*      *....*              *....*      *....*
        *....*      *....*              *....*      *....*
        *....*      *....*      +       .....*      *....*
        *....*      *....*              *....*      *....*
        ******      ******              ******      ******

        :param string_time: строка введенаня пользователем
        :param nn_key: инстанс нейронной сети из реестра модуля
        """
        self._d1, self._d2, self._d3, self._d4 = self.devide_digits(string_time)

        self.first_digit = NNPixelDigit(self._d1)
        self.first_prob = 0

        self.second_digit = NNPixelDigit(self._d2)
        self.second_prob = 0

        self.third_digit = NNPixelDigit(self._d3)
        self.third_prob = 0

        self.four_digit = NNPixelDigit(self._d4)
        self.four_prob = 0

    @property
    def mid_prob_loss(self):
        digit_nn = self.first_digit.nn

        if self.first_digit.label is None and self.first_prob == 0:

            self.first_digit.label, self.first_prob = digit_nn.nn_predicted_digit_and_prob(self.first_digit.image_vect)

        if self.second_digit.label is None and self.second_prob == 0:

            self.second_digit.label, self.second_prob = digit_nn.nn_predicted_digit_and_prob(self.second_digit.image_vect)

        if self.third_digit.label is None and self.third_prob == 0:

            self.third_digit.label, self.third_prob = digit_nn.nn_predicted_digit_and_prob(self.third_digit.image_vect)

        if self.four_digit.label is None and self.four_prob == 0:

            self.four_digit.label, self.four_prob = digit_nn.nn_predicted_digit_and_prob(self.four_digit.image_vect)

        mid_prob_loss = 1.0 - ((self.first_prob +
                                self.second_prob +
                                self.third_prob +
                                self.four_prob) / 4)

        return mid_prob_loss

    def add_to_dataset(self, labels: list=None):
        self.first_digit.nn.add_to_dataset(labels=labels[0],
                                           image_vectors=self.first_digit.image_vect
                                           )

        self.second_digit.nn.add_to_dataset(labels=labels[1],
                                            image_vectors=self.second_digit.image_vect
                                            )

        self.third_digit.nn.add_to_dataset(labels=labels[2],
                                           image_vectors=self.third_digit.image_vect
                                           )

        self.four_digit.nn.add_to_dataset(labels=labels[3],
                                          image_vectors=self.four_digit.image_vect
                                          )

    def __str__(self):
        if self.mid_prob_loss > 0.5:
            return '[Невозможно определить]'

        # Поправки для контекста "Часы и минуты"
        if self.first_digit.label > 2:
            self.first_digit.label = None
        else:
            if self.first_digit.label == 2 and self.second_digit.label > 4:
                self.second_digit.label = None

        if self.third_digit.label > 5:
            self.third_digit.label = None

        if self.first_digit.label is not None and self.second_digit.label is not None and self.third_digit.label is not None and self.four_digit.label is not None:
            return f'{self.first_digit.label}{self.second_digit.label}:{self.third_digit.label}{self.four_digit.label}'
        return '[Невозможно определить]'

    time = property(__str__)


def main():
    # Если в папке найдены образцы для обучения цифр
    trrainpath = os.path.join('datasets', 'lab3', 'train_dataset', '*.txt')
    training_samples = glob.glob(trrainpath)
    if len(training_samples):
        nn_digit = NNDigitRecogniteModel(1, 'main')
        NEURAL_MODEL_REGISTRY['main1'] = nn_digit

        samples_list = []

        for sample in training_samples:
            training_etalons = defaultdict(list)
            __pixels_load(sample, training_etalons)

            for k, pixels in training_etalons.items():
                digit = NNPixelDigit('\n'.join(pixels), label=k)

                samples_list.append((k, digit))

        random.shuffle(samples_list)

        for k, dig in samples_list:
            nn_digit.add_to_dataset(k, dig.bin_vectorize_block())

        nn_digit.nn_fit()
