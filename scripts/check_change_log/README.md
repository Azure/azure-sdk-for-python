# Overview
This script will generate change_log by comparing latest two versions of mgmt package on pypi. It can help us quickly verify whether the changes to the `change_log` tool are correct 



# preprequisites
- [Python 3.6](https://www.python.org/downloads/windows/) or later is required
- [docker desktop](https://www.docker.com/get-started/)

# How to use this script
1.Use gitbash to create a new branch to work in.

2.Please make sure your docker is running on your computer.

3.Open your powershell and step in path where the script is in

4.Install the dependency
```bash
pip install -r requirements.txt
```

5.Run command in your powershell:
```
python main.py
```
