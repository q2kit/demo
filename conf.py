import os
import configparser

from constants import CONF_PATH


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
