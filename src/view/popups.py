from PySide6.QtWidgets import QMessageBox


def could_not_connect_mb(error: str, parent=None) -> None:
    title_text = 'Serial Connection Failed'
    message_text = f'{error}'
    buttons = QMessageBox.StandardButton.Ok
    QMessageBox.critical(parent, title_text, message_text, buttons)


def missing_SN_logNum_mb(parent=None) -> None:
    title_text = 'Missing SN or logNum'
    message_text = 'Please enter a serial number and/or log number.'
    buttons = QMessageBox.StandardButton.Ok
    QMessageBox.critical(parent, title_text, message_text, buttons)


def not_connected_mb(parent=None) -> None:
    title_text = 'No Serial Connection'
    message_text = 'No serial connection. Try reconnecting.'
    buttons = QMessageBox.StandardButton.Ok
    QMessageBox.critical(parent, title_text, message_text, buttons)
