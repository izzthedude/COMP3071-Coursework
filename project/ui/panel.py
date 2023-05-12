from PySide6.QtCore import *
from PySide6.QtWidgets import *


class Panel(QScrollArea):
    def __init__(self, parent: QObject = None):
        super().__init__(parent)

        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setAlignment(Qt.AlignTop)
        self.setLayout(layout)

        # General Settings
        self._general_section = _Section("General")
        self.run_simulation_checkbox = QCheckBox()
        self.tick_interval_spinbox = QSpinBox()
        self.ticks_per_gen_spinbox = QSpinBox()
        self.learning_mode_checkbox = QCheckBox()
        self.auto_reset_checkbox = QCheckBox()

        self._general_section.add_row("Run Simulation", self.run_simulation_checkbox)
        self._general_section.add_row("Tick Interval (ms)", self.tick_interval_spinbox)
        self._general_section.add_row("Ticks Per Generation", self.ticks_per_gen_spinbox)
        self._general_section.add_row("Learning Mode", self.learning_mode_checkbox,
                                      "When enabled, the environment will automatically adjust itself according to the "
                                      "success of the agents. In any case, the agents will proceed to the next "
                                      "generation after each run and 'learn' from the previous generation. Some "
                                      "parameters will be locked while Learning Mode is enabled. "
                                      "Otherwise, the environment is in 'Observation' mode, where you can observe the "
                                      "current generation of agents tackle the environments.")
        self._general_section.add_row("Auto Reset", self.auto_reset_checkbox,
                                      "Automatically reset the environment or proceed to the next generation.")

        # Map Generation Settings
        self._map_section = _Section("Map Generation")
        self.map_size_spinbox = QSpinBox()
        self.regen_n_runs_checkbox = QCheckBox()
        self.regen_n_runs_spinbox = QSpinBox()
        self.resize_n_regens_checkbox = QCheckBox()
        self.resize_n_regens_spinbox = QSpinBox()
        self.regenerate_btn = QPushButton("Regenerate Map")

        self.regen_n_runs_box = QWidget(layout=QHBoxLayout())
        self.regen_n_runs_box.layout().addWidget(self.regen_n_runs_checkbox)
        self.regen_n_runs_box.layout().addWidget(self.regen_n_runs_spinbox)

        self.resize_n_regens_box = QWidget(layout=QHBoxLayout())
        self.resize_n_regens_box.layout().addWidget(self.resize_n_regens_checkbox)
        self.resize_n_regens_box.layout().addWidget(self.resize_n_regens_spinbox)

        self._map_section.add_row("Size", self.map_size_spinbox)
        self._map_section.add_row("Regenerate on N Runs", self.regen_n_runs_box,
                                  "Automatically regenerate the map after N runs of the current map.")
        self._map_section.add_row("Resize on N Regenerations", self.resize_n_regens_box,
                                  "Automatically increment map size after N regenerations of the current map size.")
        self._map_section.add_row("", self.regenerate_btn,
                                  "Regenerate the map based on the current map size.")

        # Vehicle Settings
        self._vehicle_section = _Section("Vehicle")
        self.sensor_length_spinbox = QSpinBox()
        self.vehicle_maxspeed_spinbox = QSpinBox()
        self.dspeed_spinbox = QDoubleSpinBox()
        self.dangle_spinbox = QSpinBox()
        self.vehicle_reset_btn = QPushButton("Reset Vehicles")

        self._vehicle_section.add_row("Sensor Length", self.sensor_length_spinbox)
        self._vehicle_section.add_row("Max Speed", self.vehicle_maxspeed_spinbox)
        self._vehicle_section.add_row("Change of Speed", self.dspeed_spinbox)
        self._vehicle_section.add_row("Change of Angle", self.dangle_spinbox)
        self._vehicle_section.add_row("", self.vehicle_reset_btn,
                                      "Reset the vehicle parameters and some environment parameters "
                                      "(but not agents' NNs).")

        # Agent Settings
        self._agent_section = _Section("Agent")
        self.dynamic_mutation_checkbox = QCheckBox()
        self.mutation_chance_spinbox = QDoubleSpinBox()
        self.mutation_rate_spinbox = QDoubleSpinBox()
        self.proceed_nextgen_btn = QPushButton("Next Generation")
        self.save_best_agent_btn = QPushButton("Save Best Agent")
        self.load_agent_btn = QPushButton("Load Agent")

        self._agent_section.add_row("Dynamic Mutation", self.dynamic_mutation_checkbox,
                                    "Reduce the chance of mutation as the best fit agent gets closer to the goal."
                                    " Max chance is 40%, while min is 1%.")
        self._agent_section.add_row("Chance of Mutation", self.mutation_chance_spinbox,
                                    "The probability of mutating a weight value in an agent's NN.")
        self._agent_section.add_row("Rate of Mutation", self.mutation_rate_spinbox,
                                    "The 'intensity' of the mutation done to a weight value.")
        self._agent_section.add_row("", self.proceed_nextgen_btn,
                                    "Proceeds to the next generation by creating children from some of the best fit "
                                    "agents. Some of the best fit agents are preserved for the next generation.")
        self._agent_section.add_row("", self.save_best_agent_btn)
        self._agent_section.add_row("", self.load_agent_btn)

        self.addWidget(self._general_section)
        self.addWidget(self._map_section)
        self.addWidget(self._vehicle_section)
        self.addWidget(self._agent_section)

        for widget in self.findChildren(QWidget):
            widget.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        self.adjustSize()

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

    def add_row(self, title: str, action_widget: QWidget, tooltip: str = ""):
        row = self._rows_layout.rowCount()
        action_widget.setToolTip(tooltip)
        self._rows_layout.addWidget(QLabel(title, toolTip=tooltip), row, 0, alignment=Qt.AlignLeft | Qt.AlignVCenter)
        self._rows_layout.addWidget(action_widget, row, 1, alignment=Qt.AlignRight | Qt.AlignVCenter)
