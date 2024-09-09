import json
import pathlib
import os
from subprocess import check_call, CalledProcessError, check_output, Popen, call
import sys
from ci_tools.parsing import ParsedSetup
import logging
from ci_tools.environment_exclusions import is_check_enabled

user_path = os.environ['USER_PATH']
root_dir = os.environ['ROOT_DIR']

skip = ["tests", "samples", "models", "operations", "_operations", "_generated", "build", "nspkg"]
direct = pathlib.Path(user_path).glob('**/*/__init__.py')
list_of_folders = []
for folder in list(direct):
    
    if not ".tox" in str(folder) and not "mgmt" in str(folder):
        if set(folder.parts).isdisjoint(skip):
            
            if os.path.dirname(folder).split("/")[-1] == "azure":
                list_of_folders.append(os.path.dirname(os.path.dirname(folder)))
# Run pylint on each folder

rcFileLocation = os.path.join(root_dir, "pylintrc")


for folder in list_of_folders:
    try:
        pkg_dir = os.path.abspath(folder)
        pkg_details = ParsedSetup.from_path(pkg_dir)
        top_level_module = pkg_details.namespace.split('.')[0]
    except Exception as e:
        logging.error("Error in parsing setup.py file")
        logging.error(e)
        continue

# Uncomment to run pylint on each check-enabled folder
    try:
        if is_check_enabled(folder, "pylint"):
            os.path.join(folder, top_level_module)
            os.popen(f"tox run -e pylint -c {root_dir}/eng/tox/tox.ini --root {folder}") 
            f = open(f"{folder}/pylint_output.txt", "w")
            call(
                [
                    sys.executable,
                    "-m",
                    "pylint",
                    "--rcfile={}".format(rcFileLocation),
                    "--output-format=parseable",
                    os.path.join(folder, top_level_module),
                ], stdout=f
            )
        else:
            print(f"Package {folder} opts-out of pylint check.")

    except CalledProcessError as e:
       print(e)

# Grab results 

results = []
for folder in list_of_folders:
    try:
        f = open(f"{folder}/pylint_output.txt", "r")
        for line in f.readlines():
            if "[I0021(useless-suppression), ]" in line:
                results.append(line)
    except Exception as e:
        logging.error("Error in reading pylint_output.txt file")
        logging.error(e)
        continue

for i in results:
    print(i)
    print("\n")

# Go through results and delete `#pylint: disable....` that stem from a 'useless-disable' warning

for result in results:
    print(result.split("]")[1].split("'")[1])
    path = result.split(":")[0]
    num = int(result.split(":")[1])
    reason = result.split("]")[1].split("'")[1]

    with open(path, "r") as f:
        lines = f.readlines()
        # num = int(line[0])
        # print(f"Line to read {int(line[0])}")
        
        try:
            print(f"Number of lines in file: {len(lines)}")
            print(f"Line to read: {num}")
            print(f"Looking for: {reason}")
            print(f"Line: {lines[num-1]}")
            
            if f"# pylint: disable={reason}" in lines[num-1]:
                print("Found")
                if "," in lines[num-1].split("pylint")[1]:
                    lines[num-1] = lines[num-1].replace(f"{reason},", "")
                else:
                    lines[num-1] = lines[num-1].replace(f"# pylint: disable={reason}", "").rstrip() + "\n"
                with open(path, "w") as fi:
                    fi.writelines(lines)
            elif f"# pylint:disable={reason}" in lines[num-1]:
                print("Found")
                if "," in lines[num-1].split("pylint")[1]:
                    lines[num-1] = lines[num-1].replace(f"{reason},", "")
                else:
                    lines[num-1] = lines[num-1].replace(f"# pylint:disable={reason}", "").rstrip() + "\n"
                with open(path, "w") as fi:
                    fi.writelines(lines)
            elif f"# pylint: disable" in lines[num-1]:
                print("Found")
                if "," in lines[num-1].split("pylint")[1]:
                    lines[num-1] = lines[num-1].replace(f",{reason}", "")
                else:
                    lines[num-1] = lines[num-1].replace(f"# pylint: disable={reason}", "").rstrip() + "\n"
                with open(path, "w") as fi:
                    fi.writelines(lines)
        except Exception as e:
            print(e)
            print("ERROR")

        # break
