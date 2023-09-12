# SSH Remote Server Connection and Data Transfer Scripts

This Python script allows connecting to and managing remote servers over the SSH protocol using the paramiko library.
It also transfers data via SFTP and performs data writes and pulls to a CSV file.

## Requirements
+ Python3.x
+ paramiko library
+ csv library
+ subprocess library
## Installation
1. Clone this project or download it as a ZIP.
```
git clone https://github.com/sinemenguc/remote-server-management.git
```
2. Install the **paramiko** and **csv** libraries required for the script to run.
```
pip install paramiko
pip install csv
pip install subprocess
``` 
## How to use
1. Run the script:
```
python3 ssh.py
```
2. The script will then prompt for the target username, the target IP address and the name of the directory you want to create.
3. Enter the password for the target server.
4. The script will establish SSH connection to the remote server, create the specified directory and create a CSV file in it and write the data.
5. After the CSV file is successfully created, the same file will be downloaded to your local computer using SFTP.
6. If you want to stay on the remote server, you can restart your SSH session by removing the last two lines of the script from the comment line.

## Notes
+ The script will display a login failed message if the correct username and password are not provided.
+ If an error occurs, the corresponding error message will be displayed.
+ Replace the 'query' parts in the script with queries that will be suitable for you.
---
This project was created to help you interact with remote servers and transfer data. Please refrain from using this script on systems you are not responsible for and without permission.

*Author*: *Sinem Mengüç*
