import os


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
PID_FILE_PATH = os.path.join(ROOT_DIR, "demo.pid")
if os.name == "nt":
    SSH_EXECUTE_PATH = os.path.join(os.path.dirname(__file__), "ssh.exe")
else:
    SSH_EXECUTE_PATH = "ssh"
