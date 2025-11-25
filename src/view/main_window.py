from pathlib import Path

from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import (
    QCheckBox,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QVBoxLayout,
    QWidget,
)
from qt_material import apply_stylesheet

import helpers.constants as c
import helpers.helpers as h
import src.view.popups as popup

from ..model.model import Model
from ..view.connection_window import ConnectionWindow


class MainWindow(QMainWindow):
    # Define Signals to emit to Controller
    csvIt_sig = Signal(bool)
    printIt_sig = Signal(bool)
    commandIt_sig = Signal(bool)
    SN_changed_sig = Signal(str)
    logNum_changed_sig = Signal(str)
    MWconnect_sig = Signal()
    change_save_dir_sig = Signal()

    def __init__(self, model: Model) -> None:
        super().__init__()
        self.version = c.VERSION

        self.model = model
        self.model.connected_sig.connect(self.receive_connected_sig)
        self.model.not_connected_sig.connect(self.receive_not_connected_sig)
        self.model.commandIt_failed_sig.connect(self.receive_commandIt_failed_sig)
        self.model.worker_finished_sig.connect(self.receive_worker_finished_sig)

        self.logNum: str = ''
        self.SN: str = ''

        self.connection_window = ConnectionWindow(
            parent=self, com_port=self.model.com_port
        )

        self.create_gui()

    def create_gui(self) -> None:
        window_width = 330
        window_height = 250
        self.setFixedSize(window_width, window_height)
        root_dir: Path = h.get_root_dir()
        icon_path: str = str(root_dir / 'assets' / 'icon.ico')
        self.setWindowIcon(QIcon(icon_path))
        self.setWindowTitle(f'HEU3 convertLog (v{self.version})')
        apply_stylesheet(self, theme='dark_lightgreen.xml', invert_secondary=True)
        self.setStyleSheet(self.styleSheet() + """QLineEdit {color: lightgreen;}""")

        self._create_menubar()

        self.printIt_cb = QCheckBox('Print Log')
        self.printIt_cb.setChecked(False)
        self.csvIt_cb = QCheckBox('Create CSV')
        self.csvIt_cb.setChecked(True)
        self.commandIt_pb = QPushButton('Pull Data Log')
        self.convertLog_pb = QPushButton('Convert Log')
        self.SN_le = QLineEdit(placeholderText='Enter Serial Number')
        self.logNum_le = QLineEdit(placeholderText='Enter Log Number')

        # Create a fixed-height vertical spacer (20 is minimum width, doesn't matter much here)
        width = 20
        height = 20
        spacer = QSpacerItem(
            width, height, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed
        )

        self.printIt_cb.clicked.connect(self.handle_printIt_clicked)
        self.csvIt_cb.clicked.connect(self.handle_csvIt_clicked)
        self.commandIt_pb.clicked.connect(self.handle_commandIt_clicked)
        self.convertLog_pb.clicked.connect(self.handle_convertLog_clicked)

        le_layout = QHBoxLayout()
        le_layout.addWidget(self.SN_le)
        le_layout.addWidget(self.logNum_le)

        cb_layout = QHBoxLayout()
        cb_layout.addWidget(self.printIt_cb)
        cb_layout.addWidget(self.csvIt_cb)

        group_box = QGroupBox()
        group_box.setStyleSheet("""
            QGroupBox::title {
                color: transparent; /* Makes text invisible */
                padding: 0px;       /* Removes space reserved for text */
                padding-top: 0px;
                height: 0px;
                }
            QGroupBox {
                padding: 0px;
                padding-top: 0px;        
            }
        """)
        group_box_layout = QVBoxLayout()
        group_box_layout.addLayout(cb_layout)
        group_box_layout.addWidget(self.convertLog_pb)
        group_box.setLayout(group_box_layout)

        main_layout = QVBoxLayout()
        main_layout.addLayout(le_layout)
        main_layout.addWidget(self.commandIt_pb)
        main_layout.addItem(spacer)
        main_layout.addWidget(group_box)

        container = QWidget()
        container.setLayout(main_layout)

        self.setCentralWidget(container)

    def _create_menubar(self) -> None:
        self.exit_action = QAction(text='Exit', parent=self)
        self.connect_action = QAction(text='Connect', parent=self)
        self.change_save_dir_action = QAction(text='Change Save Location', parent=self)

        self.menu_bar = self.menuBar()
        self.file_menu = self.menu_bar.addMenu('File')
        self.option_menu = self.menu_bar.addMenu('Options')
        # self.help_menu = self.menu_bar.addMenu('Help')

        self.file_menu.addAction(self.connect_action)
        self.file_menu.addAction(self.exit_action)
        self.option_menu.addAction(self.change_save_dir_action)

        self.exit_action.triggered.connect(self.handle_exit_triggered)
        self.connect_action.triggered.connect(self.handle_connect_triggered)
        self.change_save_dir_action.triggered.connect(
            self.handle_change_save_dir_triggered
        )

    def handle_printIt_clicked(self) -> None:
        if self.printIt_cb.isChecked():
            self.printIt_sig.emit(True)
        else:
            self.printIt_sig.emit(False)

    def handle_csvIt_clicked(self) -> None:
        if self.csvIt_cb.isChecked():
            self.printIt_sig.emit(True)
        else:
            self.printIt_sig.emit(False)

    def handle_commandIt_clicked(self) -> None:
        # Make sure the user has put text in for the serial and log numbers.
        if not self.SN_le.text() or not self.logNum_le.text():
            popup.missing_SN_logNum_mb(self)  # error message box
            return
        self.commandIt_pb.setEnabled(False)
        self.commandIt_pb.setText('Getting Data')
        self.SN_changed_sig.emit(self.SN_le.text())
        self.logNum_changed_sig.emit(self.logNum_le.text())
        self.commandIt_sig.emit(self.printIt_cb.isChecked())

    def handle_change_save_dir_triggered(self) -> None:
        self.change_save_dir_sig.emit()

    def handle_connect_triggered(self) -> None:
        self.connection_window.show()

    def handle_exit_triggered(self) -> None:
        self.close()

    def handle_convertLog_clicked(self) -> None:
        print('clicked')

    @Slot()
    def receive_connected_sig(self) -> None:
        self.commandIt_pb.setEnabled(True)
        self.commandIt_pb.setText('Pull Data Log')

    @Slot(str)
    def receive_not_connected_sig(self, error: str) -> None:
        self.commandIt_pb.setEnabled(False)
        self.commandIt_pb.setText('Not Connected')
        popup.could_not_connect_mb(error, parent=self)

    @Slot()
    def receive_worker_finished_sig(self) -> None:
        popup.show_save_loction_mb(save_loc=str(self.model.wdir), parent=self)
        self.commandIt_pb.setEnabled(True)
        self.commandIt_pb.setText('Pull Data Log')

    @Slot(str)
    def receive_commandIt_failed_sig(self, error: str) -> None:
        popup.commandIt_failed_mb(error, parent=self)
