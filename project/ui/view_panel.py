from PySide6.QtCore import *
from PySide6.QtWidgets import *


class ControlPanel(QScrollArea):
    def __init__(self, parent: QObject = None):
        super().__init__(parent)
        self.setFixedSize(300, 1000)

        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setAlignment(Qt.AlignTop)
        self.setLayout(layout)

        # Map Generation Settings
        self._map_section = _Section("Map Generation Settings")

        self.size_spinbox = QSpinBox()
        self.size_spinbox.setRange(3, 11)
        self.regenerate_button = QPushButton("Regenerate")

        self._map_section.add_row("Size", self.size_spinbox)
        self._map_section.add_row("", self.regenerate_button)

        # Vehicle Settings
        self._vehicle_section = _Section("Vehicle")
        self.reset_btn = QPushButton("Reset Vehicle")
        self.change_speed_spinbox = QDoubleSpinBox()
        self.turn_multiplier_spinbox = QSpinBox()

        self._vehicle_section.add_row("", self.reset_btn)
        self._vehicle_section.add_row("Change of Speed Rate", self.change_speed_spinbox)
        self._vehicle_section.add_row("Turn Speed Multiplier", self.turn_multiplier_spinbox)

        # Agent Settings
        self._agent_section = _Section("Agent")
        self.manual_mode_btn = QCheckBox()
        self._agent_section.add_row("Manual Mode", self.manual_mode_btn)

        self.layout().addWidget(self._map_section)
        self.layout().addWidget(self._vehicle_section)
        self.layout().addWidget(self._agent_section)


class _Section(QWidget):
    def __init__(self, title: str, parent: QObject = None):
        super().__init__(parent)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 5, 0, 15)
        self.setLayout(layout)

        self._title_label = QLabel(title)
        self._title_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(self._title_label)

        self._rows_layout = QGridLayout()
        self._rows_layout.setContentsMargins(10, 0, 10, 10)
        layout.addLayout(self._rows_layout)

    def set_title(self, title: str):
        self._title_label.setText(title)

    def add_row(self, title: str, action_widget: QWidget):
        row = self._rows_layout.rowCount()
        self._rows_layout.addWidget(QLabel(title), row, 0, alignment=Qt.AlignLeft | Qt.AlignVCenter)
        self._rows_layout.addWidget(action_widget, row, 1, alignment=Qt.AlignRight | Qt.AlignVCenter)
