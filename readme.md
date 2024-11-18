# DEMO
The "DEMO" program is a convenient tool that enables users to make their websites accessible from the internet, even though the websites are running on their local machines.

# Usage
### Step 1: Create a project
- Visit the website https://netswift.org.
- Sign in or create an account if you haven't already.
- After logging in, navigate to the project creation section. This may be labeled as "Create Project" or similar.
- Fill in the required information for your project, such as the project name and domain (if applicable).
- After the project is created successfully, you'll be provided with a secret key. Copy this secret key as you'll need it for the next step.

### Step 2: Run the DEMO program
- Download the DEMO program from the releases section of the repository.
- Once downloaded, unzip the CLI package and install it on your computer.
- Open a terminal or command prompt window. (You can add a path to the environment variables to run the program from any directory)
- Run the command `demo -h` to display detailed instructions and options for using the "DEMO" tool.

# Building the Executable
## Building for Linux:
### Prerequisites:
Python installed on your Linux machine.
Make sure you have pyinstaller and requests installed. If not, install them using the following commands:
```bash
pip install -r requirements.txt
```

### Build Steps:
Open a terminal and navigate to the directory containing the script.
Run the following command to build the executable:
```bash
pyinstaller --onefile main.py
```
After the build is complete, you will find the executable in the `dist` directory.

## Building for Windows:
### Prerequisites:
Python installed on your Windows machine.
Make sure you have pyinstaller and requests installed. If not, install them using the following commands:
```bash
pip install -r requirements.txt
```

### Build Steps:
Open a command prompt and navigate to the directory containing the script.
Run the following command to build the executable:
```bash
pyinstaller --icon=icon.ico main.py
```
After the build is complete, copy the `_internal/ssh.exe` file to the `dist/demo/_internal` directory.
```bash
cp _internal/ssh.exe dist/demo/_internal
```

# Server Repository:
For the server-side of this application, please visit the [Server Repository](https://github.com/q2kit/demo-server) for more information.

Now you should have the executables ready for both Linux and Windows. Make sure to include these instructions in your README file along with the link to the server repository.
