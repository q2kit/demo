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
    if daemon:
        print(f"\\ Close connection: demo -s{' ' * (max_len - 28)}/")
    else:
        print(f"\\ Ctrl + C to exit{' ' * (max_len - 19)}/")
    print("~" * max_len)
