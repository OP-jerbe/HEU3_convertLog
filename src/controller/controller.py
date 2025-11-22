from PySide6.QtWidgets import QMainWindow

from helpers.helpers import get_folder_path


class Controller:
    def __init__(self, com_port: str, view: QMainWindow) -> None:
        self.com_port = com_port
        self.view = view


if __name__ == '__main__':
    from PySide6.QtWidgets import QApplication

    app = QApplication([])
    folder_path = get_folder_path()
    print(folder_path)
