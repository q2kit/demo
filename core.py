import os
import subprocess

from constants import SSH_SERVER_DOMAIN, SSH_SERVER_PORT, SSH_EXECUTE_PATH
from pid import save_pid_to_file, get_pid_from_file, remove_pid_file


def start_daemon(user: str, remote_port: str, local_port: int, key_path: str):
    """
    Start Demo as a daemon.

    :param user: Username
    :param remote_port: Remote port number
    :param local_port: Local port number
    :param key_path: Key file path
    """
    if os.name == "nt" and not os.path.exists(SSH_EXECUTE_PATH):
        print("[-] Internal SSH not found.")
        return

    ssh_command = [
        SSH_EXECUTE_PATH,
        "-N",
        "-p",
        str(SSH_SERVER_PORT),
        "-R",
        f"{remote_port}:127.0.0.1:{local_port}",
        f"{user}@{SSH_SERVER_DOMAIN}",
        "-i",
        key_path,
        "-o",
        "StrictHostKeyChecking=no",
        "-o",
        "UserKnownHostsFile=/dev/null",
        "-o",
        "LogLevel=ERROR",
    ]
    process = subprocess.Popen(
        ssh_command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    save_pid_to_file(process.pid)


def stop_daemon():
    """
    Stop Demo daemon.

    This function stops Demo daemon by sending a signal (SIGILL) to
    the process ID (PID) obtained from the PID file.
    If the PID file is not found or the process is not running,
    appropriate error messages are displayed.
    """
    pid = get_pid_from_file()
    if pid:
        try:
            os.kill(pid, 4)  # 4 is SIGILL
            remove_pid_file()
            print("[+] Stopped Demo daemon.")
        except Exception:
            print("[-] Process not found.")
    else:
        print("[-] PID file not found.")


def start_without_daemon(
    user: str, remote_port: str, local_port: int, key_path: str
):  # noqa
    """
    Start Demo without daemon mode.

    :param user: Username
    :param remote_port: Remote port number
    :param local_port: Local port number
    :param key_path: Key file path
    """
    if os.name == "nt" and not os.path.exists(SSH_EXECUTE_PATH):
        print("[-] Internal SSH not found.")
        return

    ssh_command = [
        SSH_EXECUTE_PATH,
        "-N",
        "-p",
        str(SSH_SERVER_PORT),
        "-R",
        f"{remote_port}:127.0.0.1:{local_port}",
        f"{user}@{SSH_SERVER_DOMAIN}",
        "-i",
        key_path,
        "-o",
        "StrictHostKeyChecking=no",
        "-o",
        "UserKnownHostsFile=/dev/null",
        "-o",
        "LogLevel=ERROR",
    ]
    subprocess.run(ssh_command)
