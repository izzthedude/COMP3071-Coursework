from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

from project import enums
from project.environment import Environment
from project.ui.canvas import Canvas
from project.ui.panel import Panel


class MainWindow(QMainWindow):
    key_pressed = Signal(QKeyEvent, int, name="key-pressed")

    def __init__(self, environment: Environment, parent: QObject = None):
        super().__init__(parent)
        self._setup_actions()
        self._setup_layout()
        self.setWindowTitle("Navigator")

        self._env: Environment = environment
        self._is_running: bool = False

        self.panel: Panel = Panel()
        self.canvas: Canvas = Canvas(self._env, self._is_running)
        self._env_runner: QTimer = QTimer(self)  # The environment runner timer: ticks the environment
        self._ui_updater: QTimer = QTimer(self)  # The interface updater timer: runs on a different thread/timer.

        self._setup_panel_values()
        self._connect_panel_widgets()
        self._env_runner.timeout.connect(self._tick)
        self._ui_updater.timeout.connect(self._update_ui)
        self._ui_updater.start(1000 / 60)  # Canvas updates per second, adjust the denominator to the desired FPS.

        self.addWidget(self.panel)
        self.addWidget(self.canvas)
        self.installEventFilter(self)

    def _tick(self):
        self._env.tick()

        # Update the tick interval every tick so that it reflects in real time
        self._env_runner.stop()
        self._env_runner.start(self._env.tick_interval)

    def _update_ui(self):
        self._block_panel_signals(QCheckBox, True)
        self._block_panel_signals(QSpinBox, True)

        self.panel.run_simulation_checkbox.setChecked(self._is_running)
        self.panel.auto_reset_checkbox.setChecked(self._env.auto_reset)
        self.panel.map_size_spinbox.setValue(self._env.get_map_size())
        self.panel.regen_n_runs_checkbox.setChecked(self._env.regen_n_runs_enabled)
        self.panel.regen_n_runs_spinbox.setEnabled(self._env.regen_n_runs_enabled)
        self.panel.regen_n_runs_spinbox.setValue(self._env.regen_n_runs)
        self.panel.resize_n_regens_checkbox.setChecked(self._env.resize_n_regens_enabled)
        self.panel.resize_n_regens_spinbox.setEnabled(self._env.resize_n_regens_enabled)
        self.panel.resize_n_regens_spinbox.setValue(self._env.resize_n_regens)
        self.panel.dynamic_mutation_checkbox.setChecked(self._env.dynamic_mutation)
        self.panel.mutation_chance_spinbox.setDisabled(self._env.dynamic_mutation)
        self.panel.mutation_chance_spinbox.setValue(self._env.mutation_chance)
        self.panel.mutation_rate_spinbox.setValue(self._env.mutation_rate)
        self.canvas.is_running = self._is_running

        self._block_panel_signals(QCheckBox, False)
        self._block_panel_signals(QSpinBox, False)

        self.panel.learning_mode_checkbox.setChecked(self._env.learning_mode)

        self.canvas.update()

    def _update_runner(self, condition: bool):
        if condition:
            self._env_runner.stop()
            self._is_running = False
        else:
            self._env_runner.start(self._env.tick_interval)
            self._is_running = True

    def eventFilter(self, watched: QObject, event: QKeyEvent) -> bool:
        if event.type() in [QEvent.KeyPress, QEvent.KeyRelease]:
            event_type = event.type()
            code = event.key()

            if code == Qt.Key.Key_Space and event_type == QEvent.KeyPress:
                self._update_runner(self._is_running)
            if code == Qt.Key.Key_Return and event_type == QEvent.KeyPress:
                self._on_proceed_nextgen()

            return True
        return False

    def addWidget(self, widget: QWidget):
        self._content_box_layout.addWidget(widget)

    def _on_run_simulation(self, state: int):
        self._update_runner(not state)

    def _on_update_interval_changed(self, value: int):
        self._env.tick_interval = value

    def _on_ticks_until_nextgen_changed(self, value: int):
        self._env.ticks_per_gen = value

    def _on_learning_mode_changed(self, check: int):
        check = bool(check)
        self._env.set_learning_mode(check)
        self.panel.auto_reset_checkbox.setDisabled(check)
        self.panel.regen_n_runs_checkbox.setDisabled(check)
        self.panel.regen_n_runs_spinbox.setDisabled(check)
        self.panel.resize_n_regens_checkbox.setDisabled(check)
        self.panel.resize_n_regens_spinbox.setDisabled(check)
        self.panel.dynamic_mutation_checkbox.setDisabled(check)

    def _on_auto_reset_changed(self, check: int):
        self._env.auto_reset = bool(check)

    def _on_map_size_changed(self, value: int):
        self._env.change_map_size(value)

    def _on_regen_n_runs_checked(self, check: int):
        check = bool(check)
        self._env.regen_n_runs_enabled = check

    def _on_regen_n_runs_changed(self, value: int):
        self._env.regen_n_runs = value

    def _on_resize_n_regens_checked(self, check: int):
        check = bool(check)
        self._env.resize_n_regens_enabled = check

    def _on_resize_n_regens_changed(self, value: int):
        self._env.resize_n_regens = value

    def _on_regenerate(self):
        self._env.regenerate_map()

    def _on_sensor_length_changed(self, value: int):
        enums.SENSOR_LENGTH = value

    def _on_max_speed_changed(self, value: int):
        enums.VEHICLE_MAXSPEED = value

    def _on_dspeed_changed(self, value: float):
        enums.VEHICLE_DSPEED = value

    def _on_dangle_changed(self, value: int):
        enums.VEHICLE_DANGLE = value

    def _on_reset_vehicle(self):
        self._env.reset_vehicles()

    def _on_dynamic_mutation_changed(self, check: int):
        check = bool(check)
        self._env.dynamic_mutation = check
        self.panel.mutation_chance_spinbox.setEnabled(not check)

    def _on_mutation_chance_changed(self, value: float):
        self._env.mutation_chance = value

    def _on_mutation_rate_changed(self, value: float):
        self._env.mutation_rate = value

    def _on_proceed_nextgen(self):
        self._env.end_current_run(True, True)

    def _on_save_best_model(self):
        self._env.save_best_agent(self._env.AGENTS_DIR)

    def _on_load_model(self):
        dialog = QFileDialog(self, "Select Python pickle file", self._env.AGENTS_DIR, "Python Pickles (*.pickle)")
        dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptOpen)

        if dialog.exec():
            file_path = dialog.selectedFiles()[0]
            self._env.load_agent(file_path)

    def _setup_panel_values(self):
        # General
        self.panel.tick_interval_spinbox.setRange(1, 50)
        self.panel.tick_interval_spinbox.setValue(self._env.tick_interval)
        self.panel.ticks_per_gen_spinbox.setRange(100, 2000)
        self.panel.ticks_per_gen_spinbox.setSingleStep(50)
        self.panel.ticks_per_gen_spinbox.setValue(self._env.ticks_per_gen)
        self.panel.auto_reset_checkbox.setChecked(self._env.auto_reset)

        # Map
        self.panel.map_size_spinbox.setRange(3, 11)
        self.panel.regen_n_runs_checkbox.setChecked(self._env.regen_n_runs_enabled)
        self.panel.regen_n_runs_spinbox.setRange(1, 50)
        self.panel.regen_n_runs_spinbox.setSingleStep(1)
        self.panel.regen_n_runs_spinbox.setValue(self._env.regen_n_runs)
        self.panel.regen_n_runs_spinbox.setEnabled(self.panel.regen_n_runs_checkbox.isChecked())
        self.panel.resize_n_regens_checkbox.setChecked(self._env.resize_n_regens_enabled)
        self.panel.resize_n_regens_spinbox.setRange(1, 50)
        self.panel.resize_n_regens_spinbox.setSingleStep(1)
        self.panel.resize_n_regens_spinbox.setValue(self._env.resize_n_regens)
        self.panel.resize_n_regens_spinbox.setEnabled(self.panel.resize_n_regens_checkbox.isChecked())
        self.panel.map_size_spinbox.setValue(self._env.get_map_size())

        # Vehicle
        self.panel.sensor_length_spinbox.setRange(10, enums.CANVAS_SIZE)
        self.panel.sensor_length_spinbox.setSingleStep(10)
        self.panel.sensor_length_spinbox.setValue(enums.SENSOR_LENGTH)
        self.panel.vehicle_maxspeed_spinbox.setRange(1, 50)
        self.panel.vehicle_maxspeed_spinbox.setValue(enums.VEHICLE_MAXSPEED)
        self.panel.dspeed_spinbox.setRange(0.1, 5.0)
        self.panel.dspeed_spinbox.setSingleStep(0.1)
        self.panel.dspeed_spinbox.setValue(enums.VEHICLE_DSPEED)
        self.panel.dangle_spinbox.setRange(1, 20)
        self.panel.dangle_spinbox.setValue(enums.VEHICLE_DANGLE)

        # Agent
        self.panel.dynamic_mutation_checkbox.setChecked(self._env.dynamic_mutation)
        self.panel.mutation_chance_spinbox.setRange(0.01, 0.99)
        self.panel.mutation_chance_spinbox.setSingleStep(0.01)
        self.panel.mutation_chance_spinbox.setValue(self._env.mutation_chance)
        self.panel.mutation_rate_spinbox.setRange(0.01, 0.99)
        self.panel.mutation_rate_spinbox.setSingleStep(0.01)
        self.panel.mutation_rate_spinbox.setValue(self._env.mutation_rate)

    def _connect_panel_widgets(self):
        # General
        self.panel.run_simulation_checkbox.stateChanged.connect(self._on_run_simulation)
        self.panel.tick_interval_spinbox.valueChanged.connect(self._on_update_interval_changed)
        self.panel.ticks_per_gen_spinbox.valueChanged.connect(self._on_ticks_until_nextgen_changed)
        self.panel.learning_mode_checkbox.stateChanged.connect(self._on_learning_mode_changed)
        self.panel.auto_reset_checkbox.stateChanged.connect(self._on_auto_reset_changed)

        # Map
        self.panel.map_size_spinbox.valueChanged.connect(self._on_map_size_changed)
        self.panel.regen_n_runs_checkbox.stateChanged.connect(self._on_regen_n_runs_checked)
        self.panel.regen_n_runs_spinbox.valueChanged.connect(self._on_regen_n_runs_changed)
        self.panel.resize_n_regens_checkbox.stateChanged.connect(self._on_resize_n_regens_checked)
        self.panel.resize_n_regens_spinbox.valueChanged.connect(self._on_resize_n_regens_changed)
        self.panel.regenerate_btn.clicked.connect(self._on_regenerate)

        # Vehicle
        self.panel.sensor_length_spinbox.valueChanged.connect(self._on_sensor_length_changed)
        self.panel.vehicle_maxspeed_spinbox.valueChanged.connect(self._on_max_speed_changed)
        self.panel.dspeed_spinbox.valueChanged.connect(self._on_dspeed_changed)
        self.panel.dangle_spinbox.valueChanged.connect(self._on_dangle_changed)
        self.panel.vehicle_reset_btn.clicked.connect(self._on_reset_vehicle)

        # Agent
        self.panel.dynamic_mutation_checkbox.stateChanged.connect(self._on_dynamic_mutation_changed)
        self.panel.mutation_chance_spinbox.valueChanged.connect(self._on_mutation_chance_changed)
        self.panel.mutation_rate_spinbox.valueChanged.connect(self._on_mutation_rate_changed)
        self.panel.proceed_nextgen_btn.clicked.connect(self._on_proceed_nextgen)
        self.panel.save_best_agent_btn.clicked.connect(self._on_save_best_model)
        self.panel.load_agent_btn.clicked.connect(self._on_load_model)

    def _setup_layout(self):
        self._content_box_layout = QHBoxLayout()
        self._content_box_layout.setContentsMargins(0, 0, 0, 0)
        self._content_box = QWidget(self)
        self._content_box.setLayout(self._content_box_layout)
        self.setCentralWidget(self._content_box)

    def _setup_actions(self):
        self.quit_shortcut = QShortcut(QKeySequence("Ctrl+Q"), self)
        self.close_shortcut = QShortcut(QKeySequence("Ctrl+W"), self)
        self.close_shortcut.activated.connect(self.close)

    def _block_panel_signals(self, widget_type: type, block: bool):
        for widget in self.panel.findChildren(widget_type):
            widget.blockSignals(block)
