import requests

from constants import SERVER_URL


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
    data = {"domain": domain, "secret": secret_key, "port": local_port}
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
