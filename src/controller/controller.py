from helpers.helpers import get_folder_path

if __name__ == '__main__':
    from PySide6.QtWidgets import QApplication

    app = QApplication([])
    folder_path = get_folder_path()
    print(folder_path)
