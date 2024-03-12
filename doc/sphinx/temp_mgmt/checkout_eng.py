import os
import shutil
import shlex
import stat
import subprocess
from subprocess import check_call, CalledProcessError



def invoke_command(command: str, working_directory: str) -> None:
    try:
        command = shlex.split(command)
        wd = working_directory.replace("\\", "/")
        check_call(command, stderr=subprocess.STDOUT, cwd=wd)
    except CalledProcessError as e:
        print(e)
        raise


def prep_directory(path: str) -> str:
    cleanup_directory(path)

    os.makedirs(path)
    return path


def error_handler_git_access(func, path, exc):
    """
    This function exists because the git idx file is written with strange permissions that prevent it from being
    deleted. Due to this, we need to register an error handler that attempts to fix the file permissions before
    re-attempting the delete operations.
    """

    if not os.access(path, os.W_OK):
        os.chmod(path, stat.S_IWUSR)
        func(path)
    else:
        raise

def cleanup_directory(target_directory: str) -> None:
    """Invokes a directory delete. Specifically handles the case where bad permissions on a git .idx file
    prevent cleanup of the directory with a generic error.
    """
    if os.path.exists(target_directory):
        shutil.rmtree(target_directory, ignore_errors=False, onerror=error_handler_git_access)



def get_eng_from_main(assembly_area):
    clone_folder = prep_directory(os.path.join(assembly_area, "tmp"))
    invoke_command(
        f"git clone --no-checkout --filter=tree:0 https://github.com/Azure/azure-sdk-for-python .", clone_folder
    )
    invoke_command(f"git config gc.auto 0", clone_folder)
    invoke_command(f"git sparse-checkout init", clone_folder)
    invoke_command(f"git sparse-checkout set --no-cone '/eng' '/tools' '/doc' '/scripts'", clone_folder)
    invoke_command(f"git -c advice.detachedHead=false checkout main", clone_folder)


def move_dirs(path):
    shutil.move(os.path.join(path, "tmp", "eng"), os.path.join(path, "eng"))
    shutil.move(os.path.join(path, "tmp", "tools"), os.path.join(path, "tools"))
    shutil.move(os.path.join(path, "tmp", "doc"), os.path.join(path, "doc"))
    shutil.move(os.path.join(path, "tmp", "scripts"), os.path.join(path, "scripts"))

get_eng_from_main(
    assembly_area=os.getcwd(),
)
move_dirs(os.getcwd())