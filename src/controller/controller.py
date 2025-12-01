from pathlib import Path

from PySide6.QtCore import QObject, Slot

import helpers.helpers as h

from ..model.model import Model
from ..view.main_window import MainWindow


class Controller(QObject):
    def __init__(self, model: Model, view: MainWindow) -> None:
        super().__init__()
        self.model = model
        self.view = view

        self.view.printIt_sig.connect(self.receive_printIt_sig)
        self.view.csvIt_sig.connect(self.receive_csvIt_sig)
        self.view.commandIt_sig.connect(self.receive_commandIt_sig)
        self.view.convertLog_sig.connect(self.receive_convertLog_sig)
        self.view.SN_sig.connect(self.receive_SN_sig)
        self.view.logNum_sig.connect(self.receive_logNum_sig)
        self.view.change_wdir_sig.connect(self.receive_change_wdir_sig)
        self.view.connection_window.CWconnect_sig.connect(self.receive_CWconnect_sig)
        self.view.file_path_sig.connect(self.receive_file_path_sig)

    @Slot(bool)
    def receive_printIt_sig(self, signal: bool) -> None:
        self.model.printIt = signal

    @Slot(bool)
    def receive_csvIt_sig(self, signal: bool) -> None:
        self.model.csvIt = signal

    @Slot()
    def receive_commandIt_sig(self) -> None:
        self.model.start_commandIt_worker()

    @Slot(str)
    def receive_file_path_sig(self, file_path: str) -> None:
        self.model.logIn_txt = Path(file_path)

    @Slot(bool)
    def receive_convertLog_sig(self, printIt: bool) -> None:
        if printIt:
            h.open_console()
        self.model.start_convertLog_worker()

    @Slot(str)
    def receive_SN_sig(self, serial_number: str) -> None:
        self.model.SN = serial_number
        self.model.fname = f'sn{serial_number}log{self.model.logNum}'

    @Slot(str)
    def receive_logNum_sig(self, log_number: str) -> None:
        self.model.logNum = log_number
        self.model.fname = f'sn{self.model.SN}log{log_number}'

    @Slot()
    def receive_change_wdir_sig(self) -> None:
        self.model.change_wdir()

    @Slot(str)
    def receive_CWconnect_sig(self, com_port: str) -> None:
        """
        Save the user's com port input and tell the model
        to connect to the com port with a serial connection.
        """
        self.model.com_port = com_port
        self.model.serial_connect(self.model.com_port)
