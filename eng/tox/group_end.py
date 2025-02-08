import os

if (os.getenv('TF_BUILD') or os.getenv('CI')):
    print(f'##[endgroup]')