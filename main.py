import sys
from typing import NoReturn

from PySide6.QtWidgets import QApplication

from helpers.helpers import connect_to_com_port, get_ini_info
from src.controller.controller import Controller
from src.model.model import Model
from src.view.main_window import MainWindow


def run_app() -> NoReturn:
    version = '1.0.0'
    ini: dict[str, str] = get_ini_info()
    com_port = ini['COM']
    try:
        ser = connect_to_com_port(com_port)
    except Exception as e:
        print(f'{str(e)}')
        ser = None
    app = QApplication(sys.argv)
    view = MainWindow(version)
    model = Model(ser)
    _ = Controller(com_port, view, model)
    view.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    run_app()
