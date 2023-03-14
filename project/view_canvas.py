from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *


class CanvasView(QWidget):
    def __init__(self, parent: QObject = None):
        super().__init__(parent)

        self.setFixedSize(1000, 1000)
        self.setStyleSheet("CanvasView {background-color: red;}")

    def paintEvent(self, event: QPaintEvent):
        opt = QStyleOption()
        opt.initFrom(self)
        painter = QPainter(self)
        self.style().drawPrimitive(QStyle.PrimitiveElement.PE_Widget, opt, painter, self)
