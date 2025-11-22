import sys
from typing import NoReturn

from PySide6.QtWidgets import QApplication

from src.view.main_window import MainWindow


def run_app() -> NoReturn:
    version = "1.0.0"
    app = QApplication([])
    window = MainWindow(version)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    run_app()
