from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

from project.view_panel import ControlPanel


class MainWindow(QMainWindow):
    def __init__(self, parent: QObject = None):
        super().__init__(parent)
        self._setup_actions()
        self._setup_layout()
        self.setWindowTitle("Navigator")

        self.panel = ControlPanel()
        self._content_box_layout.addWidget(self.panel)

    def _setup_layout(self):
        self._content_box_layout = QHBoxLayout()
        self._content_box_layout.setContentsMargins(0, 0, 0, 0)
        self._content_box = QWidget(self)
        self._content_box.setLayout(self._content_box_layout)
        self.setCentralWidget(self._content_box)

    def _setup_actions(self):
        self.quit_shortcut = QShortcut(QKeySequence("Ctrl+Q"), self)
        self.close_shortcut = QShortcut(QKeySequence("Ctrl+W"), self)
        self.close_shortcut.activated.connect(self._on_close_shortcut)

    def _on_close_shortcut(self):
        self.close()
