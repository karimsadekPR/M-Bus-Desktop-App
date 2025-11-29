from PyQt5.QtWidgets import QDialog, QLabel, QVBoxLayout
from PyQt5.QtCore import Qt, QObject, pyqtSignal
from PyQt5.QtGui import QMovie
import time

class LoadingDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setModal(True)

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.label = QLabel("Loading...")
        self.label.setAlignment(Qt.AlignCenter)

        # GIF spinner
        self.movie = QMovie("spinner.gif")
        self.label.setMovie(self.movie)
        self.movie.start()

        layout.addWidget(self.label)


class Worker(QObject):
    finished = pyqtSignal(object)   # return value
    error = pyqtSignal(str)

    def __init__(self, func, *args):
        super().__init__()
        self.func = func
        self.args = args

    def run(self):
        try:
            result = self.func(*self.args)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))

