import configparser
import ctypes
import sys
from pathlib import Path
from typing import TypeAlias

from PySide6.QtWidgets import QFileDialog
from serial import Serial

ConfigData: TypeAlias = configparser.ConfigParser


def open_console() -> None:
    if getattr(sys, 'frozen', False):
        try:
            # Check if we can attach to an existing console (e.g., if run from CMD)
            if not ctypes.windll.kernel32.AttachConsole(-1):
                # If not, allocate a new one
                ctypes.windll.kernel32.AllocConsole()

            # Redirect stdout/stderr to the new console
            # Need to reopen file descriptors to point to the new console
            sys.stdout = open('CONOUT$', 'w')
            sys.stderr = open('CONOUT$', 'w')

        except Exception as e:
            # Handle potential failure to allocate console
            print(f'Could not open console\n\n{str(e)}')


def get_root_dir() -> Path:
    """
    Get the root directory of the __main__ file.

    Returns [str]:
        Path object
    """
    if getattr(sys, 'frozen', False):  # Check if running from the PyInstaller EXE
        return Path(getattr(sys, '_MEIPASS', '.'))
    else:  # Running in a normal Python environment
        return Path(__file__).resolve().parents[1]


def load_config(file_name: str) -> ConfigData:
    """
    Get the data contained in the .ini file from file_name.

    Inputs [file_name]:
        Path to file_name
    InputTypes [str]
    Returns [configparser.ConfigParser]:
        The parsed data contained in the .ini file.
    """
    config_data = configparser.ConfigParser()
    config_data.read(file_name)
    return config_data


def get_ini_info(
    config_dir: str = 'configuration',
    ini_file: str = 'config.ini',
) -> dict[str, str]:
    """
    Get the initialization information from the .ini file that is
    in the configuration folder.

    Inputs: [str, str]:
        The name of the folder where the .ini file resides and the name of the .ini file.
    Returns [dict(str, str)]:
        The COM port listed in the ini file.
    """
    root_dir: Path = get_root_dir()
    ini_file_path: str = str(root_dir / config_dir / ini_file)
    config_data: ConfigData = load_config(ini_file_path)
    com_port: str = config_data.get(section='COM_PORT', option='COM')

    return {'COM': com_port}


def get_folder_path() -> str:
    """
    Open a file dialog to select a folder.

    Returns:
        Path: The path to the selected folder. If the dialog is cancelled,
             an empty string is returned.
    """

    folder_path: str = QFileDialog.getExistingDirectory(
        parent=None,
        caption='Choose Folder',
        dir='',
        options=QFileDialog.Option.ShowDirsOnly,
    )

    return folder_path


def connect_to_com_port(
    com_port: str, baudrate: int = 38400, timeout: int = 1
) -> Serial:
    return Serial(port=com_port, baudrate=baudrate, timeout=timeout)


if __name__ == '__main__':
    root_dir = get_root_dir()
    ini = get_ini_info()

    print(root_dir)
    print(ini['COM'])
