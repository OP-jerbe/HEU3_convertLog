import sys
from typing import NoReturn

from PySide6.QtWidgets import QApplication

import helpers.constants as C
from helpers.helpers import get_ini_info
from src.controller.controller import Controller
from src.model.model import Model
from src.view.main_window import MainWindow

# TODO: fix what happens when the user cancels choosing a file to convert.


def run_app() -> NoReturn:
    load_ini()
    app = QApplication(sys.argv)
    model = Model()
    view = MainWindow(model)
    _ = Controller(model, view)
    view.show()
    sys.exit(app.exec())


def load_ini() -> None:
    ini: dict[str, str | int] = get_ini_info()
    C.COM_PORT = ini['COM']
    C.LOG_VERSION = ini['LOG_VERSION']
    C.TIME_ZONE_OFFSET = ini['TIME_ZONE_OFFSET']
    C.DATE_LINE_OFFSET = ini['DATE_LINE_OFFSET']
    C.MEGS = ini['MEGS']
    C.MUTE = ini['MUTE']
    C.START_LINE = ini['START_LINE']
    C.END_LINE = ini['END_LINE']


if __name__ == '__main__':
    run_app()
