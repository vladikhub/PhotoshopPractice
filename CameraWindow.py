from PyQt5 import QtWidgets, uic
from PyQt5.Qt import *
import cv2

class Camera(QMainWindow):
    """
    Класс окна камеры
    """
    def __init__(self, parent=None):
        super().__init__()
        # Подгрузка ui-файла
        uic.loadUi('camera.ui', self)
        self.setWindowTitle("Веб-камера")

        self.parent = parent

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(1000 // 30)

        # Подключение в веб-камере
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            self.cameraLabel.setText("""Ошибка подключения к веб-камере. Веб-камера не найдена.
        Проверьте в диспетчере устройств, включена ли камера.""")


        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 819)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 529)


        self.photoBut.clicked.connect(self.do_photo)

    def update_frame(self):
        """
        Метод обровления кадров веб-камеры и вывод на экран
        :return:
        """
        ret, frame = self.cap.read()  # Считывание кадра с веб-камеры
        frame = cv2.flip(frame, 1)
        if ret:
            rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_image.shape
            bytes_per_line = ch * w
            q_img = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(q_img)
            self.cameraLabel.setPixmap(pixmap)

    def do_photo(self):
        """
        Метод создания снимка с веб камеры
        :return:
        """
        # Считывание кадра с веб-камеры
        ret, frame = self.cap.read()
        frame = cv2.flip(frame, 1)
        # Проверка на наличие кадра
        if ret:
            rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_image.shape
            bytes_per_line = ch * w
            q_img = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(q_img)
            self.parent.imageLabel.setPixmap(pixmap)
        # Открывается изначальное окно
        self.parent.show()
        self.hide()
        self.cap.release()
if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    win = Camera()
    win.show()
    sys.exit(app.exec_())