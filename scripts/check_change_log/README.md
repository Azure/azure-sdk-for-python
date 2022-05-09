# Overview
This script will generate change_log from two code_reports which generate by the latest two versions of azure-mgmt-package on pypi. It can help us quickly verify whether the changes to the `change_log` tool are correct 



# preprequisites
- [Python 3.6](https://www.python.org/downloads/windows/) or later is required
- [docker desktop](https://www.docker.com/get-started/)

# How to use this script
1.Use gitbash to create a new branch to work in.

2.Please make sure your docker is running on your computer.

3.Open your powershell and enter the path of the script. like `\xx\check_change_log\`

4.Install the dependency
```bash
pip install -r requirements.txt
```

5.Execute it with the following command in your powershell:
```
python main.py
```
