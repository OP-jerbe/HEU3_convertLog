import sys
from typing import NoReturn

from PySide6.QtWidgets import QApplication

from helpers.helpers import get_ini_info
from src.controller.controller import Controller
from src.view.main_window import MainWindow


def run_app() -> NoReturn:
    version = '1.0.0'
    ini: dict[str, str] = get_ini_info()
    com_port = ini['COM']
    app = QApplication([])
    window = MainWindow(version)
    _ = Controller(com_port, window)
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    run_app()
