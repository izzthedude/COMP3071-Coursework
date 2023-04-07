from PySide6.QtCore import *
from PySide6.QtWidgets import *

from project import enums


class Panel(QScrollArea):
    def __init__(self, parent: QObject = None):
        super().__init__(parent)
        self.setFixedSize(350, enums.CANVAS_SIZE)

        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setAlignment(Qt.AlignTop)
        self.setLayout(layout)

        # General Settings
        self._general_section = _Section("General")
        self.run_simulation_checkbox = QCheckBox()
        self.tick_interval_spinbox = QSpinBox()
        self.ticks_per_gen_spinbox = QSpinBox()
        self.auto_reset_checkbox = QCheckBox()

        self._general_section.add_row("Run Simulation", self.run_simulation_checkbox)
        self._general_section.add_row("Tick Interval (ms)", self.tick_interval_spinbox)
        self._general_section.add_row("Ticks Per Generation", self.ticks_per_gen_spinbox)
        self._general_section.add_row("Auto Reset", self.auto_reset_checkbox)

        # Map Generation Settings
        self._map_section = _Section("Map Generation")
        self.map_size_spinbox = QSpinBox()
        self.regenerate_button = QPushButton("Regenerate Map")

        self._map_section.add_row("Size", self.map_size_spinbox)
        self._map_section.add_row("", self.regenerate_button)

        # Vehicle Settings
        self._vehicle_section = _Section("Vehicle")
        self.vehicle_maxspeed_spinbox = QSpinBox()
        self.dspeed_spinbox = QDoubleSpinBox()
        self.dangle_spinbox = QSpinBox()
        self.vehicle_reset_btn = QPushButton("Reset Vehicles")

        self._vehicle_section.add_row("Max Speed", self.vehicle_maxspeed_spinbox)
        self._vehicle_section.add_row("Change of Speed", self.dspeed_spinbox)
        self._vehicle_section.add_row("Change of Angle", self.dangle_spinbox)
        self._vehicle_section.add_row("", self.vehicle_reset_btn)

        # Agent Settings
        self._agent_section = _Section("Agent")
        self.learning_mode_checkbox = QCheckBox()
        self.dynamic_mutation_checkbox = QCheckBox()
        self.mutation_chance_spinbox = QDoubleSpinBox()
        self.mutation_rate_spinbox = QDoubleSpinBox()
        self.regen_on_success_spinbox = QSpinBox()
        self.resize_on_success_spinbox = QSpinBox()
        self.proceed_nextgen_btn = QPushButton("Next Generation")
        self.save_best_btn = QPushButton("Save Best Model")
        self.load_model_btn = QPushButton("Load Model")

        self._agent_section.add_row("Learning Mode", self.learning_mode_checkbox)
        self._agent_section.add_row("Dynamic Mutation", self.dynamic_mutation_checkbox)
        self._agent_section.add_row("Chance of Mutation", self.mutation_chance_spinbox)
        self._agent_section.add_row("Rate of Mutation", self.mutation_rate_spinbox)
        self._agent_section.add_row("Regen on Success", self.regen_on_success_spinbox)
        self._agent_section.add_row("Resize on Success", self.resize_on_success_spinbox)
        self._agent_section.add_row("", self.proceed_nextgen_btn)
        self._agent_section.add_row("", self.save_best_btn)
        self._agent_section.add_row("", self.load_model_btn)

        self.addWidget(self._general_section)
        self.addWidget(self._map_section)
        self.addWidget(self._vehicle_section)
        self.addWidget(self._agent_section)

        for widget in self.findChildren(QWidget):
            widget.setFocusPolicy(Qt.FocusPolicy.NoFocus)

    def addWidget(self, widget: QWidget):
        self.layout().addWidget(widget)


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
