import argparse

from banner import display_banner
from conf import get_configuration, save_configuration
from core import start_daemon, stop_daemon, start_without_daemon
from connect import is_server_available, send_connection_signal, fetch_connection_info
from func import download_key_file, is_valid_port


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
            "-d", "--daemon", action="store_true", help="Start as daemon"
        )
        parser.add_argument("-s", "--stop", action="store_true", help="Stop the daemon")
        parser.add_argument(
            "-otc",
            "--one-time-connection",
            type=str,
            help="One time connection. (domain:secret)",
        )
        args = parser.parse_args()

        if args.stop:
            stop_daemon()
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
        print("[-] Something went wrong. Please contact the administrator.")
        print("[-] Error details:", e)


if __name__ == "__main__":
    main()
