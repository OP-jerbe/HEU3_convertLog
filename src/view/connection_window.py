from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget


class ConnectionWindow(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.Dialog)
