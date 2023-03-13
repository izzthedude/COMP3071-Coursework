from PySide6.QtCore import *
from PySide6.QtWidgets import *


class ControlPanel(QScrollArea):
    def __init__(self, parent: QObject = None):
        super().__init__(parent)

        self.setFixedSize(400, 1000)
        self.setStyleSheet("ControlPanel {background-color: blue;}")
