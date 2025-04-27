# demo/cli.py

import argparse
import configparser
import os
import selectors
import socket
import threading
import time
import warnings

import paramiko
import requests

warnings.filterwarnings("ignore")


TEMP_DIR = os.getenv("TEMP") if os.name == "nt" else "/tmp"
HOME_DIR = (
    os.path.expandvars("%USERPROFILE%") if os.name == "nt" else os.path.expanduser("~")
)
ROOT_DIR = os.path.join(HOME_DIR, ".demo")
if not os.path.exists(ROOT_DIR):
    os.makedirs(ROOT_DIR)
CONF_PATH = os.path.join(ROOT_DIR, "demo.conf")
HTTP_SERVER_DOMAIN = "ezdemo.org"
SSH_SERVER_DOMAIN = "ssh.ezdemo.org"
SERVER_URL = f"https://{HTTP_SERVER_DOMAIN}"
SSH_SERVER_PORT = 2222
VERSION = (1, 0, 4)

stop_event = threading.Event()


def download_key_file(domain: str, secret_key: str) -> str:
    """
    Get the key file from the server.

    :param domain: The domain for which the key file is requested.
    :param secret_key: The secret key used for authentication.
    :return: The file path of the downloaded key file.
    """
    url = f"{SERVER_URL}/get_key_file/"
    data = {"domain": domain, "secret_key": secret_key}
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


def reverse_forward_tunnel(remote_port, local_host, local_port, transport):
    def handler(chan, host, port):
        try:
            sock = socket.socket()
            sock.connect((host, port))
        except Exception as e:
            print(f"Forwarding request to {host}:{port} failed: {e}")
            return

        selector = selectors.DefaultSelector()
        selector.register(chan, selectors.EVENT_READ)
        selector.register(sock, selectors.EVENT_READ)

        while not stop_event.is_set():
            events = selector.select(timeout=1)
            for key, _ in events:
                if key.fileobj == chan:
                    data = chan.recv(1024)
                    if not data:
                        selector.unregister(chan)
                        selector.unregister(sock)
                        chan.close()
                        sock.close()
                        return
                    sock.send(data)
                elif key.fileobj == sock:
                    data = sock.recv(1024)
                    if not data:
                        selector.unregister(chan)
                        selector.unregister(sock)
                        chan.close()
                        sock.close()
                        return
                    chan.send(data)
        chan.close()
        sock.close()

    transport.request_port_forward("", remote_port)
    while not stop_event.is_set():
        chan = transport.accept(1)
        if chan is None:
            continue
        thr = threading.Thread(target=handler, args=(chan, local_host, local_port))
        thr.start()


def start_connection(
    user: str,
    remote_port: str,
    local_port: int,
    key_path: str,
):
    key = paramiko.RSAKey.from_private_key_file(key_path)

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    client.connect(
        hostname=SSH_SERVER_DOMAIN,
        port=SSH_SERVER_PORT,
        username=user,
        pkey=key,
        look_for_keys=False,
        allow_agent=False,
    )

    transport = client.get_transport()

    reverse_forward_tunnel(int(remote_port), "127.0.0.1", local_port, transport)


def is_server_available() -> bool:
    """
    Check if the server is available.

    :return: True if the server is available, False otherwise.
    :rtype: bool
    """
    try:
        return requests.get(f"{SERVER_URL}/health").status_code == 200
    except requests.RequestException:
        return False


def send_connection_signal(domain: str, secret_key: str, local_port: int):
    """
    Send a signal to the server to create a connection.

    :param domain: Domain name of the project.
    :param secret_key: Secret key for authentication.
    :param local_port: Local port number to establish the connection.
    """
    url = f"{SERVER_URL}/connect/"
    data = {"domain": domain, "secret_key": secret_key, "port": local_port}
    requests.post(url, data=data)


def fetch_connection_info(domain: str) -> tuple:
    """
    Get the user and port number from the server.

    :param domain: Domain name of the project.
    :return: Tuple containing user and port number.
    :raises Exception: If there is an error retrieving the connection info.
    """
    url = f"{SERVER_URL}/get_connection_info/"
    data = {"domain": domain}
    response = requests.post(url, data=data)

    if response.status_code != 200:
        raise Exception("Invalid configuration, please check the configuration.")

    response = response.json()
    user, port = response.get("user"), response.get("port")

    if not user or not port:
        raise Exception(response.get("error", "Unknown error"))

    return user, str(port)


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
        return config["CONF"]["domain"], config["CONF"]["secret_key"]
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
        file.write(f"secret_key={secret_key}\n")


def display_banner(local_port: str, domain: str):
    """
    Print the banner with connection information.

    :param local_port: Local port number
    :param domain: Remote domain
    """
    local_line = f"local: http://localhost:{local_port}"
    remote_line = f"remote: https://{domain}"

    max_len = max(len(local_line), len(remote_line)) + 4

    print()
    print("~" * max_len)
    print(
        f"/{' ' * (max_len // 2 - 3)}DEMO{' ' * (max_len // 2 - 3 + (max_len) % 2)}\\"
    )
    print(
        f"\\{' ' * (max_len // 2 - 4)}``````{' ' * (max_len // 2 - 4 + (max_len) % 2)}/"
    )
    print(f"/{' ' * (max_len - 2)}\\")
    print(f"\\ {local_line}{' ' * (max_len - 4 - len(local_line))} /")
    print(f"/ {remote_line}{' ' * (max_len - 4 - len(remote_line))} \\")
    print(f"\\{' ' * (max_len - 2)}/")
    print(f"/{' ' * (max_len - 2)}\\")
    print(f"\\ Ctrl + C to exit{' ' * (max_len - 19)}/")
    print("~" * max_len)


def keep_alive_loop(domain: str):
    url = f"{SERVER_URL}/keep_alive/"
    data = {"domain": domain}

    while not stop_event.is_set():
        try:
            response = requests.post(url, data=data, timeout=10)
            if response.status_code != 200:
                print(f"[-] Failed to send keep-alive: {response.status_code}")
        except Exception as e:
            print(f"[-] Keep-alive error: {e}")

        for _ in range(180):
            if stop_event.is_set():
                break
            time.sleep(1)


def main():
    try:
        parser = argparse.ArgumentParser(description="DEMO")
        parser.add_argument(
            "-p", "--port", type=str, help="Local port number (1-65535)"
        )
        parser.add_argument(
            "-c",
            "--config",
            type=str,
            help="Set the domain and secret_key (domain:secret_key)",
        )
        parser.add_argument(
            "-otc",
            "--one-time-connection",
            type=str,
            help="One time connection. (domain:secret_key)",
        )
        parser.add_argument(
            "--health-check", action="store_true", help="Check server health"
        )
        parser.add_argument(
            "-v",
            "--version",
            action="version",
            version=f"%(prog)s v{VERSION[0]}.{VERSION[1]}.{VERSION[2]}",
        )
        args = parser.parse_args()

        if args.health_check:
            print("[+] Checking server:", SERVER_URL)
            if is_server_available():
                print("[+] Server is available.")
            else:
                print("[-] Server is not available.")
            return

        if args.one_time_connection:
            try:
                domain, secret_key = args.one_time_connection.split(":")
                if not domain or not secret_key:
                    raise ValueError
            except ValueError:
                print("[-] Invalid format. Ex: demo -otc domain:secret_key")
                return
        else:
            if args.config:
                try:
                    domain, secret_key = args.config.split(":")
                except ValueError:
                    print("[-] Invalid format. Ex: demo -c domain:secret_key")
                    return
                if domain and secret_key:
                    save_configuration(domain, secret_key)
                    print("[+] Configuration saved.")
                    if not args.port:
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
        display_banner(local_port, domain)

        keep_alive_thread = threading.Thread(target=keep_alive_loop, args=(domain,))
        keep_alive_thread.start()

        start_connection(
            user,
            remote_port,
            int(local_port),
            key_path,
        )

    except KeyboardInterrupt:
        print("\n[+] Exiting...")
        stop_event.set()
    except Exception as e:
        print("[-] Something went wrong. Please contact the administrator.")
        print("[-] Error details:", e)
        stop_event.set()
