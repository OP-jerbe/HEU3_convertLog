from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QLineEdit, QPushButton, QVBoxLayout, QWidget
from qt_material import apply_stylesheet

from helpers.helpers import get_root_dir


class ConnectionWindow(QWidget):
    CWconnect_sig = Signal(str)

    def __init__(self, com_port: str, parent=None) -> None:
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.Dialog)
        self.com_port = com_port
        self.create_gui()

    def create_gui(self) -> None:
        # Set the window size
        window_width = 150
        window_height = 130
        self.setFixedSize(window_width, window_height)

        # Set the window icon and title
        root_dir: Path = get_root_dir()
        icon_path: str = str(root_dir / 'assets' / 'icon.ico')
        self.setWindowIcon(QIcon(icon_path))
        self.setWindowTitle('Connect to HEU')

        # Apply styling
        apply_stylesheet(self, theme='dark_lightgreen.xml', invert_secondary=True)
        self.setStyleSheet(self.styleSheet() + """QLineEdit {color: lightgreen;}""")

        self.com_port_le = QLineEdit(self.com_port)
        self.connect_btn = QPushButton('Connect')

        self.connect_btn.clicked.connect(self.handle_connect_clicked)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.com_port_le)
        main_layout.addWidget(self.connect_btn)
        self.setLayout(main_layout)

    def handle_connect_clicked(self) -> None:
        """
        Tell the Controller to try and establish serial communication with the given com port.
        """
        self.CWconnect_sig.emit(self.com_port_le.text().upper())


if __name__ == '__main__':
    import sys

    from PySide6.QtWidgets import QApplication

    app = QApplication([])
    com_port = 'COM4'
    window = ConnectionWindow(com_port)
    window.show()
    sys.exit(app.exec())
