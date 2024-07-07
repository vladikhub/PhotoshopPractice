from PIL import Image
from PyQt5 import QtWidgets, uic, QtCore, QtGui
from PyQt5.Qt import *

from CameraWindow import Camera
import numpy as np
import cv2


# Класс, отвечающий за создание меню
class Menu(QMainWindow):
    def __init__(self):
        super().__init__()
        # загрузка окна Меню
        uic.loadUi('D://PycharmProjects/SumPracticaFinal/ui/menu.ui', self)
        self.setWindowTitle("Photoshop")
        # дополнительная установка интерфейса ui
        self.setUpUi()

        self.curPixmap = None
        self.originPixmap = None
        self.changedImage = False

        self.loadedImage = None

        # Привязывание кнопок и виджетов к функциям
        self.cameraBut.clicked.connect(self.photo)
        self.redRadio.toggled.connect(self.load_red_channel)
        self.greenRadio.toggled.connect(self.load_green_channel)
        self.blueRadio.toggled.connect(self.load_blue_channel)
        self.widthSpinBox.valueChanged.connect(self.resize_image)
        self.heightSpinBox.valueChanged.connect(self.resize_image)

        self.brightSlayder.sliderReleased.connect(self.setBrightness)

        self.drawButton.clicked.connect(self.draw_line)

        # Установка начальных состояний кнопок
        self.set_start_tools()


    def setUpUi(self):
        """
        Метод установки дополнительного интерфейса
        """
        # Создание menuBar
        self.menubar = self.menuBar()
        self.menubar.setStyleSheet('''
                    QMenuBar { border: 1px solid rgb(100, 100, 100)};
                ''')
        # Создание Label для картинки
        self.layout = QVBoxLayout()
        self.imageLabel = QLabel()
        self.widget.setLayout(self.layout)
        self.layout.addWidget(self.imageLabel, alignment=Qt.AlignCenter)
        self.imageLabel.setFixedSize(800, 600)
        self.imageLabel.setStyleSheet("border:None;")
        self.imageLabel.setAlignment(Qt.AlignCenter)
        self.imageLabel.setScaledContents(True)

        # Добавление вкладок в menuBar и привязывание методов
        openAct = QAction('Открыть', self)
        openAct.setStatusTip('Открыть изображение')
        openAct.triggered.connect(self.openImg)

        saveAct = QAction("Сохранить", self)
        saveAct.setStatusTip("Сохранить изображение")
        saveAct.triggered.connect(self.saveImg)

        fileMenu = self.menubar.addMenu('Файл')
        fileMenu.addAction(openAct)
        fileMenu.addAction(saveAct)

    def resize_image(self):
        """
        Метод измения размера изображения
        :return:
        """
        if self.imageLabel.pixmap():
            w = self.widthSpinBox.value()
            h = self.heightSpinBox.value()
            self.imageLabel.setFixedSize(w, h)

    def saveImg(self):
        """
        Метод сохранения изображения на компьютере
        :return:
        """
        # Проверка на наличие изображения
        if self.imageLabel.pixmap():
            # появления окна для выбора пути
            folder_path = QFileDialog.getExistingDirectory(self, 'Выберите папку для сохранения')
            if folder_path != '':
                # Окно с вводом названия картинки
                name, flag = QInputDialog.getText(self, "Название картинки",
                                                  "В названии должно быть разрешение(*.jpg):")
                if flag and "." in name:
                    try:
                        image_path = folder_path + f"/{name}"
                        # Сохранение фотографии по заданному пути
                        self.imageLabel.pixmap().save(image_path)
                        self.imageLabel.setPixmap(QPixmap())
                        self.set_start_tools()

                        # Вывод сообщение об успешном сохранении
                        mes = QMessageBox()
                        mes.setStyleSheet("QMessageBox {background-color: rgb(62, 62, 62)};")
                        mes.setWindowTitle("Успешно")
                        mes.setText("Изображение успешно сохранено!")
                        mes.setIcon(QMessageBox.Information)
                        mes.setStandardButtons(QMessageBox.Ok)
                        mes.exec_()
                        self.originPixmap = None
                    except Exception:
                        # Вывод ошибки при попытки сохранения изображения
                        mes = QMessageBox()
                        mes.setWindowTitle("Ошибка")
                        mes.setText("При сохранении изображения произошла ошибка")
                        mes.setIcon(QMessageBox.Warning)
                        mes.setStandardButtons(QMessageBox.Ok)
                        mes.exec_()
                else:
                    # Вывод ошидки, если название изображения введено неправильно
                    mes = QMessageBox()
                    mes.setWindowTitle("Ошибка")
                    mes.setText("Название введено неправильно или его вовсе нет")
                    mes.setIcon(QMessageBox.Warning)
                    mes.setStandardButtons(QMessageBox.Ok)
                    mes.exec_()
        else:
            # Вывол сообщения, если нет изображения для сохранения
            mes = QMessageBox()
            mes.setWindowTitle("Ошибка")
            mes.setText("Нет изображения для сохранения!")
            mes.setIcon(QMessageBox.Warning)
            mes.setStandardButtons(QMessageBox.Ok)
            mes.exec_()

    def set_start_tools(self):
        "Установка начальных состояний кнопок"
        self.redRadio.setChecked(False)
        self.greenRadio.setChecked(False)
        self.blueRadio.setChecked(False)
        self.redRadio.setEnabled(False)
        self.greenRadio.setEnabled(False)
        self.blueRadio.setEnabled(False)
        self.heightSpinBox.setEnabled(False)
        self.widthSpinBox.setEnabled(False)
        self.brightSlayder.setEnabled(False)
        self.heightSpinBox.setValue(600)
        self.widthSpinBox.setValue(800)
        self.startX.setPlaceholderText(f"[0:{self.widthSpinBox.value()}]")
        self.startY.setPlaceholderText(f"[0:{self.heightSpinBox.value()}]")
        self.finishX.setPlaceholderText(f"[0:{self.widthSpinBox.value()}]")
        self.finishY.setPlaceholderText(f"[0:{self.heightSpinBox.value()}]")
        self.lineWidth.setPlaceholderText(f"[0:{self.widthSpinBox.value()}]")
        self.startX.setEnabled(False)
        self.startY.setEnabled(False)
        self.finishX.setEnabled(False)
        self.finishY.setEnabled(False)
        self.lineWidth.setEnabled(False)
        validatorX = QIntValidator()
        validatorY = QIntValidator()
        validatorX.setRange(0, self.widthSpinBox.value())
        validatorY.setRange(0, self.heightSpinBox.value())
        self.startX.setValidator(validatorX)
        self.startY.setValidator(validatorY)
        self.finishX.setValidator(validatorX)
        self.finishY.setValidator(validatorY)
        self.lineWidth.setValidator(validatorX)
        self.drawButton.setEnabled(False)

    def openImg(self):
        """Функция открытия изображения с компьютера
        по указанному пути и установка картинки"""
        file = QFileDialog.getOpenFileName(self,
                                           'Выберете картинку',
                                           '/Загрузки',
                                           'Картинка (*.jpg);;Картинка (*.png)'
                                           )[0]
        if file:
            try:
                # Попытка открытия файла. Если файл поврежден, то будет ошибка
                self.loadedImage = Image.open(file)
                pixmap = QPixmap(file)
                self.imageLabel.setPixmap(pixmap)
                self.originPixmap = pixmap
                self.set_tools_enabled_true()
            except Exception as ex:
                # Вызов окна с ошибкой
                err = QMessageBox()
                err.setWindowTitle("Ошибка")
                err.setText("Произошла ошибка при открытии изображения")
                err.setIcon(QMessageBox.Warning)
                err.setStandardButtons(QMessageBox.Ok)
                err.setInformativeText("Возможно файла по указанному пути нет или он поврежден.")
                err.exec_()




    def set_tools_enabled_true(self):
        """
        Метод включения инструментов для редактирования
        :return:
        """
        self.redRadio.setEnabled(True)
        self.greenRadio.setEnabled(True)
        self.blueRadio.setEnabled(True)
        self.heightSpinBox.setEnabled(True)
        self.widthSpinBox.setEnabled(True)
        self.brightSlayder.setEnabled(True)
        self.startX.setEnabled(True)
        self.startY.setEnabled(True)
        self.finishX.setEnabled(True)
        self.finishY.setEnabled(True)
        self.lineWidth.setEnabled(True)
        self.drawButton.setEnabled(True)

    def draw_line(self):
        """
        Метод для отрисовки зеленой линии
        :return:
        """
        # Получение координат начальной и конечной точки
        start_point = (int(self.startX.text()), int(self.startY.text()))
        finish_point = (int(self.finishX.text()), int(self.finishY.text()))
        color = (0, 255, 0)
        pixmap = self.originPixmap
        if pixmap:
            qimage = pixmap.toImage()
            # Перевод изображение в nparray
            width = qimage.width()
            height = qimage.height()
            ptr = qimage.bits()
            ptr.setsize(qimage.byteCount())
            img_arr = np.array(ptr).reshape((height, width, 4))
            # Отрисовка линии
            image_with_line = cv2.line(img_arr, start_point, finish_point, color,
                                       thickness=int(self.lineWidth.text()))
            # форматирование изображения в QImage и вывод
            b, g, r, t = cv2.split(image_with_line)
            image = cv2.merge((b, g, r))
            new_image = QImage(image.data, width, height, QImage.Format_BGR888)
            pixmap = QPixmap.fromImage(new_image)
            self.imageLabel.setPixmap(pixmap)
            self.originPixmap = pixmap

    def setBrightness(self):
        """
        Метод для увеличения яркости изображения
        :return:
        """
        self.copyLoadedImage = self.loadedImage.copy()
        if self.copyLoadedImage:
            # Получаем значения с QSlider
            value = self.brightSlayder.value()
            # Загружаем картинку
            pixels = self.copyLoadedImage.load()
            width, height = self.copyLoadedImage.size
            # Пробегаемся по пикселям
            for y in range(height):
                for x in range(width):
                    pixel = pixels[x, y]
                    # Меняем значения яркости
                    new_pixel = tuple(max(0, channel + value) for channel in pixel)
                    pixels[x, y] = new_pixel

            image = self.copyLoadedImage
            # Конфертируем изображение
            image_data = image.convert("RGBA").tobytes("raw", "RGBA")
            # Преобразуем изображение в QImage
            qimage = QImage(image_data, image.size[0], image.size[1], QImage.Format_RGBA8888)
            pixmap = QPixmap.fromImage(qimage)
            self.originPixmap = pixmap
            self.imageLabel.setPixmap(pixmap)

    def photo(self):
        """
        Метод создания экземплятра класса
        для веб-камеры и перехода в другое окно
        :return:
        """
        self.cam = Camera(self)
        self.cam.show()
        self.hide()

    def load_red_channel(self):
        """
        Метод установки красного канала изображения
        :return:
        """
        color = (0, 0, 1)
        self.load_channel(color)

    def load_green_channel(self):
        """
        Метод установки зеленого канала изображения
        :return:
        """
        color = (0, 1, 0)
        self.load_channel(color)

    def load_blue_channel(self):
        """
        Метод установки синего канала изображения
        :return:
        """
        color = (1, 0, 0)
        self.load_channel(color)

    def load_channel(self, color):
        """
        Метод загрузки разных каналов
        :param color: выбранный цвет канала,
        который хранится в кортеже вида (b, g, r)
        :return:
        """
        # берем начальное изображение
        pixmap = self.originPixmap
        if pixmap:
            qimage = pixmap.toImage()
            # перевод в nparray
            width = qimage.width()
            height = qimage.height()
            ptr = qimage.bits()
            ptr.setsize(qimage.byteCount())
            img_arr = np.array(ptr).reshape((height, width, 4))
            # разделение на каналы
            b, g, r, t = cv2.split(img_arr)
            # соединение каналов в одну картинку
            image = cv2.merge((b * color[0], g * color[1], r * color[2]))
            # преобразование в QImage
            new_image = QImage(image.data, width, height, QImage.Format_BGR888)
            pixmap = QPixmap.fromImage(new_image)
            self.imageLabel.setPixmap(pixmap)
            self.curPixmap = pixmap


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    win = Menu()
    win.show()
    sys.exit(app.exec_())