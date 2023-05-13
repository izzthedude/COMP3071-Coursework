import os

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

from project import enums
from project.environment import Environment
from project.ui.window import MainWindow


class App(QApplication):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setApplicationName("Navigator")
        self.setApplicationDisplayName("Navigator")
        self.setApplicationVersion("0.1.0")
        self.setWindowIcon(QPixmap(os.path.join(os.path.dirname(__file__), "icon.svg")))

        # Prompt for Training or Experiment Mode
        prompt_dialog = QMessageBox()
        prompt_dialog.setText("Choose a mode")
        prompt_dialog.setInformativeText("The Learning Mode creates an environment that trains the agent by "
                                         "progressing it through the maps using a genetic algorithm. "
                                         "The Experiment Mode creates an environment with only one vehicle for the "
                                         "user to observe as it tackles through the maps.")
        training_btn = prompt_dialog.addButton("Training Mode", QMessageBox.ButtonRole.ActionRole)
        experiment_btn = prompt_dialog.addButton("Experiment Mode", QMessageBox.ButtonRole.ActionRole)

        prompt_dialog.exec()
        load_agent = False
        train = prompt_dialog.clickedButton() == training_btn
        if prompt_dialog.clickedButton() == experiment_btn:
            enums.NUM_POPULATION = 1
            load_agent = True

        self._environment = Environment()
        self._main_window = MainWindow(self._environment)
        self._main_window.quit_shortcut.activated.connect(self._on_quit_shortcut)
        self._environment.set_learning_mode(train)
        if load_agent: self._main_window.panel.load_agent_btn.click()
        self._main_window.show()

    def _on_quit_shortcut(self):
        self.quit()
