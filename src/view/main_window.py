from pathlib import Path

from PySide6.QtCore import Signal
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import (
    QCheckBox,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMenuBar,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)
from qt_material import apply_stylesheet

from helpers.helpers import get_root_dir


class MainWindow(QMainWindow):
    csvIt_sig = Signal(bool)
    printIt_sig = Signal(bool)
    commandIt_sig = Signal()
    SN_changed_sig = Signal(str)
    logNum_changed_sig = Signal(str)
    connect_sig = Signal(str)

    def __init__(self, version: str) -> None:
        super().__init__()
        self.version = version
        self.logNum: str = ''
        self.SN: str = ''
        self.create_gui()

    def create_gui(self) -> None:
        window_width = int(330)
        window_height = int(200)
        self.setFixedSize(window_width, window_height)
        root_dir: Path = get_root_dir()
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
        self.SN_le = QLineEdit(placeholderText='Enter Serial Number')
        self.logNum_le = QLineEdit(placeholderText='Enter Log Number')

        self.printIt_cb.clicked.connect(self.handle_printIt_clicked)
        self.csvIt_cb.clicked.connect(self.handle_csvIt_clicked)
        self.commandIt_pb.clicked.connect(self.handle_commandIt_clicked)

        le_layout = QHBoxLayout()
        le_layout.addWidget(self.SN_le)
        le_layout.addWidget(self.logNum_le)

        cb_layout = QHBoxLayout()
        cb_layout.addWidget(self.printIt_cb)
        cb_layout.addWidget(self.csvIt_cb)

        main_layout = QVBoxLayout()
        main_layout.addLayout(le_layout)
        main_layout.addLayout(cb_layout)
        main_layout.addWidget(self.commandIt_pb)

        container = QWidget()
        container.setLayout(main_layout)

        self.setCentralWidget(container)

    def _create_menubar(self) -> None:
        self.exit_action = QAction(text='Exit', parent=self)
        self.connect_action = QAction(text='Connect', parent=self)

        self.menu_bar = self.menuBar()
        self.file_menu = self.menu_bar.addMenu('File')
        self.help_menu = self.menu_bar.addMenu('Help')

        self.file_menu.addAction(self.exit_action)
        self.file_menu.addAction(self.connect_action)

        self.exit_action.triggered.connect(self.handle_exit_triggered)
        self.connect_action.triggered.connect(self.handle_connect_triggered)

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
            title_text = 'Missing SN or logNum'
            message_text = 'Please enter a serial number and/or log number.'
            buttons = QMessageBox.StandardButton.Ok
            QMessageBox.critical(self, title_text, message_text, buttons)
            return
        self.SN_changed_sig.emit(self.SN_le.text())
        self.logNum_changed_sig.emit(self.logNum_le.text())
        self.commandIt_sig.emit()

    def handle_connect_triggered(self) -> None: ...

    def handle_exit_triggered(self) -> None:
        self.close()
