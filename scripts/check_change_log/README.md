# Overview
This script will use docker and help you generate two code_reports which generate by the latest two versions of azure MGMT package on pypi..
And then it will automatically use change_ log for these two code_reports.
Finally , it will generate a folder in the current directory, and the results of each comparison will be stored separately in the folder in the form of TXT.

### Usage
1.open your powershell and enter the path of the script
2.please make sure your docker is running on your computer
3. execute it with the following command:
```
python main.py
```