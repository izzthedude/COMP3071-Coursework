from PySide6.QtCore import *


class CanvasController(QObject):
    def __init__(self, parent: QObject = None):
        super().__init__(parent)
