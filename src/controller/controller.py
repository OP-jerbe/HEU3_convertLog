from PySide6.QtWidgets import QMainWindow

from helpers.helpers import get_folder_path

from ..model.model import Model


class Controller:
    def __init__(self, com_port: str, view: QMainWindow, model: Model) -> None:
        self.com_port = com_port
        self.view = view
        self.model = model


if __name__ == '__main__':
    from PySide6.QtWidgets import QApplication

    app = QApplication([])
    folder_path = get_folder_path()
    print(folder_path)
