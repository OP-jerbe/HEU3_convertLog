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
        self.view.commandIt_sig.connect(self.receive_commandIt_sig)
        self.view.convertLog_sig.connect(self.receive_convertLog_sig)
        self.view.fname_sig.connect(self.receive_fname_sig)
        self.view.file_path_sig.connect(self.receive_file_path_sig)
        self.view.folder_path_sig.connect(self.receive_folder_path_sig)

        self.view.connection_window.CWconnect_sig.connect(self.receive_CWconnect_sig)

    @Slot(bool)
    def receive_printIt_sig(self, printIt: bool) -> None:
        self.model.printIt = printIt

    @Slot(str)
    def receive_file_path_sig(self, file_path: str) -> None:
        self.model.logIn_txt = Path(file_path)

    @Slot(str)
    def receive_folder_path_sig(self, folder_path: str) -> None:
        self.model.wdir = Path(folder_path)

    @Slot()
    def receive_commandIt_sig(self) -> None:
        self.model.start_commandIt_worker()

    @Slot(bool, bool)
    def receive_convertLog_sig(self, printIt: bool, csvIt: bool) -> None:
        if printIt:
            h.open_console()
        self.model.csvIt = csvIt
        self.model.start_convertLog_worker()

    @Slot(str, str)
    def receive_fname_sig(self, serial_number: str, log_number: str) -> None:
        self.model.SN = serial_number
        self.model.logNum = log_number
        self.model.fname = f'sn{serial_number}log{log_number}'

    @Slot(str)
    def receive_CWconnect_sig(self, com_port: str) -> None:
        """
        Save the user's com port input and tell the model
        to connect to the com port with a serial connection.
        """
        self.model.com_port = com_port
        self.model.serial_connect(self.model.com_port)
