#!C:\Users\t-lilaw\Desktop\Summer\azure-sdk-for-python\venv\Scripts\python.exe
# EASY-INSTALL-ENTRY-SCRIPT: 'azure-sdk-tools','console_scripts','generate_sdk'
__requires__ = 'azure-sdk-tools'
import re
import sys
from pkg_resources import load_entry_point

if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw?|\.exe)?$', '', sys.argv[0])
    sys.exit(
        load_entry_point('azure-sdk-tools', 'console_scripts', 'generate_sdk')()
    )
