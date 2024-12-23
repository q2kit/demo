import os
import requests

from constants import SERVER_URL, TEMP_DIR


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
