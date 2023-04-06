from PySide6.QtCore import *
from PySide6.QtGui import *

from project import enums
from project.environment import Environment
from project.models import Vehicle, VehicleData
from project.ui.canvas import Canvas
from project.ui.panel import Panel
from project.ui.window import MainWindow


class AppController(QObject):
    def __init__(self, environment: Environment, window: MainWindow, parent: QObject = None):
        super().__init__(parent)
        self._window: MainWindow = window
        self._panel: Panel = self._window.panel

        self._environment = environment
        self._mapgen = environment.mapgen
        self._vehicles: dict[Vehicle, VehicleData] = environment.vehicle_datas

        self._is_running: bool = False

        self._canvas: Canvas = Canvas(self._environment, self._is_running)
        self._env_runner: QTimer = QTimer(self)
        self._ui_updater: QTimer = QTimer(self)  # The 'updater' timer: runs on a different thread/timer.
        self._window.centralWidget().layout().addWidget(self._canvas)

        self._panel.tick_interval_spinbox.setRange(1, 50)
        self._panel.tick_interval_spinbox.setValue(self._environment.tick_interval)
        self._panel.ticks_per_gen_spinbox.setRange(100, 2000)
        self._panel.ticks_per_gen_spinbox.setSingleStep(50)
        self._panel.ticks_per_gen_spinbox.setValue(self._environment.ticks_per_gen)
        self._panel.auto_reset_checkbox.setChecked(self._environment.auto_reset)
        self._panel.map_size_spinbox.setRange(3, 11)
        self._panel.map_size_spinbox.setValue(self._mapgen.get_map_size())
        self._panel.vehicle_maxspeed_spinbox.setRange(1, 50)
        self._panel.vehicle_maxspeed_spinbox.setSingleStep(1)
        self._panel.vehicle_maxspeed_spinbox.setValue(enums.VEHICLE_MAXSPEED)
        self._panel.dspeed_spinbox.setRange(0.1, 5.0)
        self._panel.dspeed_spinbox.setSingleStep(0.2)
        self._panel.dspeed_spinbox.setValue(enums.VEHICLE_DSPEED)
        self._panel.dangle_spinbox.setRange(1, 30)
        self._panel.dangle_spinbox.setSingleStep(2)
        self._panel.dangle_spinbox.setValue(enums.VEHICLE_DANGLE)
        self._panel.learning_mode_checkbox.setChecked(self._environment.learning_mode)
        self._panel.mutation_chance_spinbox.setRange(0.0, 1.0)
        self._panel.mutation_chance_spinbox.setSingleStep(0.05)
        self._panel.mutation_chance_spinbox.setValue(self._environment.mutation_chance)
        self._panel.mutation_rate_spinbox.setRange(0.0, 1.0)
        self._panel.mutation_rate_spinbox.setSingleStep(0.05)
        self._panel.mutation_rate_spinbox.setValue(self._environment.mutation_rate)
        self._panel.regen_on_success_spinbox.setRange(0, 10)
        self._panel.regen_on_success_spinbox.setValue(self._environment.regen_on_success)
        self._panel.resize_on_success_spinbox.setRange(0, 10)
        self._panel.resize_on_success_spinbox.setValue(self._environment.resize_on_success)

        self._window.key_pressed.connect(self._on_key_pressed)
        self._panel.run_simulation_checkbox.stateChanged.connect(self._on_run_simulation)
        self._panel.tick_interval_spinbox.valueChanged.connect(self._on_update_interval_changed)
        self._panel.ticks_per_gen_spinbox.valueChanged.connect(self._on_ticks_until_nextgen_changed)
        self._panel.auto_reset_checkbox.stateChanged.connect(self._on_auto_reset_changed)
        self._panel.map_size_spinbox.valueChanged.connect(self._on_size_changed)
        self._panel.regenerate_button.clicked.connect(self._on_regenerate)
        self._panel.vehicle_maxspeed_spinbox.valueChanged.connect(self._on_max_speed_changed)
        self._panel.dspeed_spinbox.valueChanged.connect(self._on_dspeed_changed)
        self._panel.dangle_spinbox.valueChanged.connect(self._on_dangle_changed)
        self._panel.vehicle_reset_btn.clicked.connect(self._on_reset_vehicle)
        self._panel.learning_mode_checkbox.stateChanged.connect(self._on_learning_mode_changed)
        self._panel.mutation_chance_spinbox.valueChanged.connect(self._on_mutation_chance_changed)
        self._panel.mutation_rate_spinbox.valueChanged.connect(self._on_mutation_rate_changed)
        self._panel.regen_on_success_spinbox.valueChanged.connect(self._on_success_regen_changed)
        self._panel.resize_on_success_spinbox.valueChanged.connect(self._on_success_resize_changed)
        self._panel.proceed_nextgen_btn.clicked.connect(self._on_proceed_nextgen)

        self._env_runner.timeout.connect(self._tick)
        self._ui_updater.timeout.connect(self._update_ui)
        self._ui_updater.start(1000 / 30)  # Canvas updates per second, adjust the denominator to the desired FPS.

    def _tick(self):
        if not self._environment.current_ticks_left <= 0:
            self._environment.tick()
        else:
            self._environment.end_current_run()

        self._env_runner.stop()
        self._env_runner.start(self._environment.tick_interval)

    def _on_key_pressed(self, event: QKeyEvent, code: int):
        event_type = event.type()

        if code == Qt.Key.Key_Space and event_type == QEvent.KeyPress:
            self._update_runner(self._is_running)

        if code == Qt.Key.Key_Return and event_type == QEvent.KeyPress:
            self._on_proceed_nextgen()

    def _on_run_simulation(self, state: int):
        self._update_runner(not state)

    def _on_update_interval_changed(self, value: int):
        self._environment.tick_interval = value

    def _on_ticks_until_nextgen_changed(self, value: int):
        self._environment.ticks_per_gen = value

    def _on_auto_reset_changed(self, check: bool):
        self._environment.auto_reset = check

    def _on_size_changed(self, value: int):
        self._environment.on_size_changed(value)

    def _on_regenerate(self):
        self._environment.on_regenerate()

    def _on_max_speed_changed(self, value: int):
        enums.VEHICLE_MAXSPEED = value

    def _on_dspeed_changed(self, value: float):
        enums.VEHICLE_DSPEED = value

    def _on_dangle_changed(self, value: int):
        enums.VEHICLE_DANGLE = value

    def _on_reset_vehicle(self):
        self._environment.on_reset()

    def _on_learning_mode_changed(self, check: bool):
        self._environment.learning_mode = check

    def _on_mutation_chance_changed(self, value: float):
        self._environment.on_mutation_chance_changed(value)

    def _on_mutation_rate_changed(self, value: float):
        self._environment.on_mutation_rate_changed(value)

    def _on_success_regen_changed(self, value: int):
        self._environment.on_success_regen_changed(value)

    def _on_success_resize_changed(self, value: int):
        self._environment.on_success_resize_changed(value)

    def _on_proceed_nextgen(self):
        self._environment.proceed_next_gen()

    def _on_save_best_model(self):
        self._environment.on_save_best_model()

    def _on_load_model(self):
        # self._environment.on_load_model()
        pass

    def _update_runner(self, condition: bool):
        if condition:
            self._env_runner.stop()
            self._is_running = False
        else:
            self._env_runner.start(self._environment.tick_interval)
            self._is_running = True

    def _update_ui(self):
        self._panel.run_simulation_checkbox.setChecked(self._is_running)
        self._panel.map_size_spinbox.setValue(self._environment.mapgen.get_map_size())
        self._panel.mutation_chance_spinbox.setValue(self._environment.mutation_chance)
        self._panel.mutation_rate_spinbox.setValue(self._environment.mutation_rate)
        self._canvas.is_running = self._is_running
        self._canvas.update()
