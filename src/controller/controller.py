from pathlib import Path

from PySide6.QtCore import QObject, Slot

from helpers.helpers import connect_to_com_port, get_folder_path, open_console

from ..model.model import Model
from ..view.connection_window import ConnectionWindow
from ..view.main_window import MainWindow
from ..view.popups import could_not_connect_mb, not_connected_mb, show_save_loction_mb


class Controller(QObject):
    def __init__(self, com_port: str, view: MainWindow, model: Model) -> None:
        super().__init__()
        self.com_port = com_port
        self.view = view
        self.model = model

        self.view.printIt_sig.connect(self.receive_printIt_sig)
        self.view.csvIt_sig.connect(self.receive_csvIt_sig)
        self.view.commandIt_sig.connect(self.receive_commandIt_sig)
        self.view.SN_changed_sig.connect(self.receive_SN_changed_sig)
        self.view.logNum_changed_sig.connect(self.receive_logNum_changed_sig)
        self.view.connect_sig.connect(self.receive_MWconnect_sig)
        self.view.change_save_dir_sig.connect(self.receive_change_save_dir_sig)
        self.model.not_connected_sig.connect(self.receive_not_connected_sig)
        self.model.worker_finished_sig.connect(self.receive_worker_finished_sig)

        if not self.model.ser:
            self.view.commandIt_pb.setEnabled(False)
            self.view.commandIt_pb.setText('Not Connected')

    @Slot(bool)
    def receive_printIt_sig(self, signal: bool) -> None:
        self.model.printIt = signal

    @Slot(bool)
    def receive_csvIt_sig(self, signal: bool) -> None:
        self.model.csvIt = signal

    @Slot()
    def receive_commandIt_sig(self) -> None:
        if self.view.printIt_cb.isChecked():
            open_console()
        self.view.commandIt_pb.setEnabled(False)
        self.view.commandIt_pb.setText('Getting Data')
        self.model.start_worker()

    @Slot(str)
    def receive_SN_changed_sig(self, serial_number: str) -> None:
        self.model.SN = serial_number
        self.model.fname = f'sn{serial_number}log{self.model.logNum}'

    @Slot(str)
    def receive_logNum_changed_sig(self, log_number: str) -> None:
        self.model.logNum = log_number
        self.model.fname = f'sn{self.model.SN}log{log_number}'

    @Slot()
    def receive_MWconnect_sig(self) -> None:
        """
        MainWindow connect_sig
        """
        connection_window = ConnectionWindow(parent=self.view, com_port=self.com_port)
        connection_window.connect_sig.connect(self.receive_CWconnect_sig)
        connection_window.show()

    @Slot(str)
    def receive_CWconnect_sig(self, com_port: str) -> None:
        """
        ConnectionWindow connect_sig
        """
        try:
            self.model.ser = connect_to_com_port(com_port)
        except Exception as e:
            self.model.ser = None
            could_not_connect_mb(error=str(e), parent=self.view)
        finally:
            if com_port:
                self.com_port = com_port
            if self.model.ser:
                self.view.commandIt_pb.setEnabled(True)
                self.view.commandIt_pb.setText('Pull Data Log')

    @Slot()
    def receive_not_connected_sig(self) -> None:
        not_connected_mb(parent=self.view)

    @Slot()
    def receive_worker_finished_sig(self) -> None:
        show_save_loction_mb(save_loc=str(self.model.wdir), parent=self.view)
        self.view.commandIt_pb.setEnabled(True)
        self.view.commandIt_pb.setText('Pull Data Log')

    @Slot()
    def receive_change_save_dir_sig(self) -> None:
        folder_path: Path = get_folder_path()
        if folder_path:
            self.model.wdir = folder_path


if __name__ == '__main__':
    from PySide6.QtWidgets import QApplication

    app = QApplication([])
    folder_path = get_folder_path()
    print(folder_path)
