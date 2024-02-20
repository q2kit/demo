import os
import argparse
import subprocess
import configparser
import requests

TEMP_DIR = os.getenv("TEMP") if os.name == "nt" else "/tmp"
HOME_DIR = os.path.expandvars('%USERPROFILE%') if os.name == "nt" else os.path.expanduser("~")  # noqa
ROOT_DIR = os.path.join(HOME_DIR, ".http-cli")
if not os.path.exists(ROOT_DIR):
    os.makedirs(ROOT_DIR)
CONF_PATH = os.path.join(ROOT_DIR, "http-cli.conf")
SERVER_DOMAIN = "demo.q2k.dev"
SERVER_URL = f"https://{SERVER_DOMAIN}"
PID_FILE_PATH = os.path.join(ROOT_DIR, "http-cli.pid")
EXECUTE_DIR = os.path.dirname(os.path.abspath(__file__))
SSH_EXECUTE_PATH = os.path.join(EXECUTE_DIR, "ssh.exe") if os.name == "nt" else "ssh"  # noqa


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


def start_daemon(user: str, remote_port: str, local_port: int, key_path: str):
    """
    Start the HTTP Tunneling as a daemon.

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
        "-p", "2222",
        "-R", f"{remote_port}:127.0.0.1:{local_port}",
        f"{user}@{SERVER_DOMAIN}",
        "-i", key_path,
        "-o", "StrictHostKeyChecking=no",
        "-o", "UserKnownHostsFile=/dev/null",
        "-o", "LogLevel=ERROR"
    ]
    process = subprocess.Popen(
        ssh_command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    save_pid_to_file(process.pid)


def stop_daemon():
    """
    Stop the HTTP Tunneling daemon.

    This function stops the HTTP Tunneling daemon by sending a signal (SIGILL) to the process ID (PID)
    obtained from the PID file. If the PID file is not found or the process is not running, appropriate
    error messages are displayed.
    """
    pid = get_pid_from_file()
    if pid:
        try:
            os.kill(pid, 4)  # 4 is SIGILL
            remove_pid_file()
            print("[+] Stopped the HTTP Tunneling daemon.")
        except Exception:
            print("[-] Process not found.")
    else:
        print("[-] PID file not found.")


def start_without_daemon(user: str, remote_port: str, local_port: int, key_path: str):  # noqa
    """
    Start the HTTP Tunneling without daemon mode.

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
        "-p", "2222",
        "-R", f"{remote_port}:127.0.0.1:{local_port}",
        f"{user}@{SERVER_DOMAIN}",
        "-i", key_path,
        "-o", "StrictHostKeyChecking=no",
        "-o", "UserKnownHostsFile=/dev/null",
        "-o", "LogLevel=ERROR"
    ]
    subprocess.run(ssh_command)


def download_key_file(domain: str, secret_key: str) -> str:
    """
    Get the key file from the server.

    :param domain: The domain for which the key file is requested.
    :param secret_key: The secret key used for authentication.
    :return: The file path of the downloaded key file.
    """
    url = f"{SERVER_URL}/get_key_file/"
    data = {"domain": domain, "secret": secret_key}
    response = requests.post(url, data=data)
    key_path = os.path.join(TEMP_DIR, "key.pem")

    with open(key_path, "wb") as file:
        file.write(response.content)

    if os.name != "nt":
        os.chmod(key_path, 0o600)

    return key_path


def is_valid_port(port: str) -> bool:
    """
    Check if the port number is valid.

    :param port: Port number
    :type port: str
    :return: True if the port number is valid, False otherwise
    :rtype: bool
    """
    port_num = int(port)
    return 1 <= port_num <= 65535


def get_configuration() -> tuple:
    """
    Get the configuration from the user.

    :return: Tuple containing domain and secret key
    """
    try:
        if not os.path.exists(CONF_PATH):
            return None, None

        config = configparser.ConfigParser()
        config.read(CONF_PATH)
        return config["CONF"]["domain"], config["CONF"]["secret"]
    except (KeyError, configparser.Error):
        return None, None


def save_configuration(domain, secret_key):
    """
    Save the configuration to the user's home directory.
    
    :param domain: Domain
    :param secret_key: Secret key
    """
    with open(CONF_PATH, "w") as file:
        file.write("[CONF]\n")
        file.write(f"domain={domain}\n")
        file.write(f"secret={secret_key}\n")


def is_server_available() -> bool:
    """
    Check if the server is available.

    :return: True if the server is available, False otherwise.
    :rtype: bool
    """
    return requests.get(f"{SERVER_URL}/health").status_code == 200


def send_connection_signal(domain: str, secret_key: str, local_port: int):
    """
    Send a signal to the server to create a connection.
    
    :param domain: Domain name of the server.
    :param secret_key: Secret key for authentication.
    :param local_port: Local port number to establish the connection.
    """
    url = f"{SERVER_URL}/connect/"
    data = {"domain": domain, "secret": secret_key, "port": local_port}
    requests.post(url, data=data)


def fetch_connection_info(domain: str) -> tuple:
    """
    Get the user and port number from the server.

    :param domain: Domain name of the server.
    :return: Tuple containing user and port number.
    :raises Exception: If there is an error retrieving the connection info.
    """
    url = f"{SERVER_URL}/get_connection_info/"
    data = {"domain": domain}
    response = requests.post(url, data=data)

    if response.status_code != 200:
        return None, None, None

    response = response.json()
    user, port = response.get("user"), response.get("port")

    if not user or not port:
        raise Exception(response.get("error", "Unknown error"))

    return user, str(port)


def display_banner(local_port: str, domain: str, daemon: bool = False):
    """
    Print the banner with connection information.

    :param local_port: Local port number
    :param domain: Remote domain
    :param daemon: True if daemon mode
    """
    local_line = f"local: http://localhost:{local_port}"
    remote_line = f"remote: https://{domain}"

    max_len = max(len(local_line), len(remote_line)) + 4

    print()
    print("~" * max_len)
    print(f"/{' ' * (max_len // 2 - 8)}HTTP Tunneling{' ' * (max_len // 2 - 8 + (max_len) % 2)}\\")  # noqa
    print(f"\\{' ' * (max_len // 2 - 8)}``````````````{' ' * (max_len // 2 - 8 + (max_len) % 2)}/")  # noqa
    print(f"/{' ' * (max_len - 2)}\\")
    print(f"\\ {local_line}{' ' * (max_len - 4 - len(local_line))} /")
    print(f"/ {remote_line}{' ' * (max_len - 4 - len(remote_line))} \\")
    print(f"\\{' ' * (max_len - 2)}/")
    print(f"/{' ' * (max_len - 2)}\\")
    if daemon:
        print(f"\\ Close connection: http-cli -s{' ' * (max_len - 32)}/")
    else:
        print(f"\\ Ctrl + C to exit{' ' * (max_len - 19)}/")
    print("~" * max_len)


def main():
    try:
        parser = argparse.ArgumentParser(description="HTTP Tunneling")
        parser.add_argument("-p", "--port", type=str, help="Local port number (1-65535)")  # noqa
        parser.add_argument("-c", "--config", type=str, help="Set the domain and secret_key (domain:secret_key)")  # noqa
        parser.add_argument("-d", "--daemon", action="store_true", help="Start as daemon")  # noqa
        parser.add_argument("-s", "--stop", action="store_true", help="Stop the daemon")  # noqa
        args = parser.parse_args()

        if not any(vars(args).values()):
            parser.print_help()
            return

        if args.stop and (args.port or args.config or args.daemon):
            parser.print_help()
            return

        if args.stop:
            stop_daemon()
            return

        if args.config:
            try:
                domain, secret_key = args.config.split(":")
            except ValueError:
                print("[-] Invalid format. Ex: http-cli -c domain:secret_key")  # noqa
                return
            if domain and secret_key:
                save_configuration(domain, secret_key)
                print("[+] Configuration saved.")
                return
            else:
                print("[o] Please set the domain and secret_key")
                domain = input("[?] Domain: ")
                secret_key = input("[?] Secret_key: ")
                save_configuration(domain, secret_key)
                print("[+] Configuration saved.")
                return
        else:
            domain, secret_key = get_configuration()
            if not domain or not secret_key:
                print("[o] Please set the domain and secret_key")
                domain = input("[?] Domain: ")
                secret_key = input("[?] Secret_key: ")
                save_configuration(domain, secret_key)

        local_port = args.port or 80
        if not is_valid_port(local_port):
            print("[-] Invalid port number!")
            return

        if not is_server_available():
            print("[-] Server is not available!")
            return

        print("[+] Creating connection...")

        user, remote_port = fetch_connection_info(domain)
        send_connection_signal(domain, secret_key, remote_port)

        key_path = download_key_file(domain, secret_key)
        display_banner(local_port, domain, args.daemon)

        if args.daemon:
            start_daemon(user, remote_port, int(local_port), key_path)
            return
        else:
            try:
                start_without_daemon(
                    user,
                    remote_port,
                    int(local_port),
                    key_path,
                )
            except KeyboardInterrupt:
                print("\n[+] Exiting...")

    except Exception as e:
        print(f"[-] {e}")


if __name__ == "__main__":
    main()
