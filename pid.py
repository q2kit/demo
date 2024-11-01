import os

from constants import PID_FILE_PATH


def save_pid_to_file(pid):
    """
    Save the PID to a file.

    Args:
        pid (int): The process ID to be saved.

    Returns:
        None
    """
    with open(PID_FILE_PATH, "w") as file:
        file.write(str(pid))


def get_pid_from_file() -> int:
    """
    Get the PID from the file.

    :return: The PID (Process ID) read from the file as an integer.
             If the file does not exist or the PID is not a valid integer,
             None is returned.
    """
    try:
        with open(PID_FILE_PATH, "r") as file:
            return int(file.read())
    except FileNotFoundError:
        return None
    except ValueError:
        print("[-] Invalid PID file format.")
        return None


def remove_pid_file():
    """
    Remove the PID file.

    This function removes the PID file specified by the `PID_FILE_PATH` constant.
    If the file does not exist, it silently ignores the error.
    """
    try:
        os.remove(PID_FILE_PATH)
    except FileNotFoundError:
        pass
