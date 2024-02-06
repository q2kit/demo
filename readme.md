# Building for Linux:
## Prerequisites:
Python installed on your Linux machine.
Make sure you have pyinstaller and requests installed. If not, install them using the following commands:
```bash
pip install -r requirements.txt
```
## Build Steps:
Open a terminal and navigate to the directory containing the script.
Run the following command to build the executable:
```bash
pyinstaller --onefile http-cli.py
```
After the build is complete, you will find the executable in the `dist` directory.

# Building for Windows:
## Prerequisites:
Python installed on your Windows machine.
Make sure you have pyinstaller and requests installed. If not, install them using the following commands:
```cmd
pip install -r requirements.txt
```
Copy the `_internal/ssh.exe` file to `dist/_internal` after the build. This is required for the ssh command to work in the Windows executable.
## Build Steps:
Open a command prompt and navigate to the directory containing the script.
Run the following command to build the executable:
```cmd
pyinstaller --icon=icon.ico http-cli.py
```
After the build is complete, copy the `_internal/ssh.exe` file to the `dist/_internal` directory.

# Server Repository:
For the server-side of this application, please visit the [Server Repository](https://github.com/q2kit/http-server) for more information.

Now you should have the executables ready for both Linux and Windows. Make sure to include these instructions in your README file along with the link to the server repository.