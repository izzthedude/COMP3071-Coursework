from PySide6.QtGui import *
from PySide6.QtWidgets import *
from PySide6.QtCore import *

from project.ui.view_panel import ControlPanel
from project.ui.view_canvas import CanvasView


class MainWindow(QMainWindow):
    def __init__(self, parent: QObject = None):
        super().__init__(parent)
        self._setup_actions()
        self.setWindowTitle("Navigator")

        self.content_box_layout = QHBoxLayout()
        self.content_box_layout.setContentsMargins(0, 0, 0, 0)
        self.content_box = QWidget(self)
        self.content_box.setLayout(self.content_box_layout)
        self.setCentralWidget(self.content_box)

        self.panel = ControlPanel()
        self.canvas = CanvasView()
        self.content_box_layout.addWidget(self.panel)
        self.content_box_layout.addWidget(self.canvas)

    def _setup_actions(self):
        self.quit_shortcut = QShortcut(QKeySequence("Ctrl+Q"), self)
        self.close_shortcut = QShortcut(QKeySequence("Ctrl+W"), self)
        self.close_shortcut.activated.connect(self._on_close_shortcut)

    def _on_close_shortcut(self):
        self.close()
