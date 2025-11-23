from PySide6.QtCore import Slot

from helpers.helpers import get_folder_path

from ..model.model import Model
from ..view.main_window import MainWindow


class Controller:
    def __init__(self, com_port: str, view: MainWindow, model: Model) -> None:
        self.com_port = com_port
        self.view = view
        self.model = model

        self.view.printIt_sig.connect(self.receive_printIt_sig)
        self.view.csvIt_sig.connect(self.receive_csvIt_sig)
        self.view.commandIt_sig.connect(self.receive_commandIt_sig)

    @Slot(bool)
    def receive_printIt_sig(self, signal: bool) -> None:
        self.model.printIt = signal

    @Slot(bool)
    def receive_csvIt_sig(self, signal: bool) -> None:
        self.model.csvIt = signal

    @Slot()
    def receive_commandIt_sig(self) -> None:
        self.model.commandIt()


if __name__ == '__main__':
    from PySide6.QtWidgets import QApplication

    app = QApplication([])
    folder_path = get_folder_path()
    print(folder_path)
