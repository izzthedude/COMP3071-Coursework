from PySide6.QtCore import *


class PanelController(QObject):
    def __init__(self, parent: QObject = None):
        super().__init__(parent)
