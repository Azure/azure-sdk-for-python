# Overview
First, this script will use docker to perform follow-up operations. 

Second, this script will help you generate two code_reports which generate by the latest two versions of azure MGMT package on pypi.

And then, it will automatically use change_ log for these two code_reports.

Finally, it will generate a folder in the current directory, and the results of each comparison will be stored separately in the folder in the form of TXT.

# preprequisites
- [Python 3.6](https://www.python.org/downloads/windows/) or later is required
- [docker desktop](https://www.docker.com/get-started/)

# How to use this script
1.Use gitbash to create a new branch to work in.

2.Please make sure your docker is running on your computer.

3.Open your powershell and enter the path of the script.

4.Execute it with the following command in your powershell:
```
python main.py
```
