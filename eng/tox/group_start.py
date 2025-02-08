import os;

if (os.getenv('TF_BUILD') or os.getenv('CI')):
    print(f'##[group]Toxenv {os.getenv("TOX_ENV_NAME")} for {os.getenv("TOXINIDIR")}')