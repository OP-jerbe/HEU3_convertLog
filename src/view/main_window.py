from pathlib import Path

from PySide6.QtCore import Signal
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QCheckBox,
    QGridLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QWidget,
)
from qt_material import apply_stylesheet

from helpers.helpers import get_root_dir


class MainWindow(QMainWindow):
    csvIt_sig = Signal(bool)
    printIt_sig = Signal(bool)
    commandIt_sig = Signal(bool)
    SN_changed_sig = Signal(str)
    logNum_changed_sig = Signal(str)

    def __init__(self, version: str) -> None:
        super().__init__()
        self.version = version
        self.logNum: str = ''
        self.SN: str = ''
        self.create_gui()

    def create_gui(self) -> None:
        window_width = int(400 * 1.5)
        window_height = int(300 * 1.5)
        self.setFixedSize(window_width, window_height)
        root_dir: Path = get_root_dir()
        icon_path: str = str(root_dir / 'assets' / 'icon.ico')
        self.setWindowIcon(QIcon(icon_path))
        self.setWindowTitle(f'HEU3 convertLog (v{self.version})')
        apply_stylesheet(self, theme='dark_lightgreen.xml', invert_secondary=True)
        self.setStyleSheet(self.styleSheet() + """QLineEdit {color: lightgreen;}""")

        self.printIt_cb = QCheckBox('Print Log')
        self.printIt_cb.setChecked(False)
        self.csvIt_cb = QCheckBox('Create CSV')
        self.csvIt_cb.setChecked(True)
        self.commandIt_pb = QPushButton('Pull Data Log')
        self.SN_le = QLineEdit(placeholderText='Enter HEU Serial Number')
        self.logNum_le = QLineEdit(placeholderText='Enter Log Number')

        self.printIt_cb.clicked.connect(self.handle_printIt_clicked)
        self.csvIt_cb.clicked.connect(self.handle_csvIt_clicked)
        self.commandIt_pb.clicked.connect(self.handle_commandIt_clicked)

        main_layout = QGridLayout()

        container = QWidget()
        container.setLayout(main_layout)

        self.setCentralWidget(container)

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
        self.commandIt_sig.emit()
