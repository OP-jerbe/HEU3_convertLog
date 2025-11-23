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
        self.view.SN_changed_sig.connect(self.receive_SN_changed_sig)
        self.view.logNum_changed_sig.connect(self.receive_logNum_changed_sig)

    @Slot(bool)
    def receive_printIt_sig(self, signal: bool) -> None:
        self.model.printIt = signal

    @Slot(bool)
    def receive_csvIt_sig(self, signal: bool) -> None:
        self.model.csvIt = signal

    @Slot()
    def receive_commandIt_sig(self) -> None:
        self.model.commandIt()

    @Slot(str)
    def receive_SN_changed_sig(self, serial_number: str) -> None:
        self.model.SN = serial_number
        self.model.fname = f'sn{serial_number}log{self.model.logNum}'

    @Slot(str)
    def receive_logNum_changed_sig(self, log_number: str) -> None:
        self.model.logNum = log_number
        self.model.fname = f'sn{self.model.SN}log{log_number}'


if __name__ == '__main__':
    from PySide6.QtWidgets import QApplication

    app = QApplication([])
    folder_path = get_folder_path()
    print(folder_path)
