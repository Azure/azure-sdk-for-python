# coding=utf-8
import glob
import os
import subprocess as sp
import time
from pypi_tools.pypi import PyPIClient
from pathlib import Path

error_packages_info = {}

def find_report_name(result):
    signal_api_pattern = 'written to'
    multi_api_pattern = 'merged_report'
    print("result: ", result)
    for line in result:
        idx = line.find(signal_api_pattern)
        idx1 = line.find(multi_api_pattern)
        if idx > 0 and idx1 > 0:
            return "_/" + line[idx + len(signal_api_pattern):].replace(" ", "")

    for line in result:
        idx = line.find(signal_api_pattern)
        if idx > 0:
            return "_/" + line[idx + len(signal_api_pattern):].replace(" ", "")

    return ''

def create_folder(name):
    if not os.path.exists(name):
        os.mkdir(name)
        print("create folder successfully")
    else:
        print("folder has been created")

def write_txt(foldor, text_name, text, last_version, older_version):
    path = foldor + f"\{text_name}" + " " + last_version + "-" + older_version + r".txt"
    with open(file=path, mode="w", encoding="utf-8") as file:

        file.write(text)
    print("change_log.txt create successful")

def create_code_report(cmd, service_name):
    info = sp.Popen(cmd,
                    stderr=sp.STDOUT,
                    stdout=sp.PIPE,
                    universal_newlines=True,
                    cwd=None,
                    shell=False,
                    env=None,
                    encoding="utf-8",
                    )
    output_buffer = []
    for line in info.stdout:
        output_buffer.append(line.rstrip())
    info.wait()
    info_output = "\n".join(output_buffer)
    if info.returncode:
        err_info = '\n'.join(output_buffer[-min(len(output_buffer), 7):0])
        error_packages_info[service_name] = err_info
    return info_output.split('\n')

if __name__ == '__main__':
    # get sdk path
    env = Path.cwd()
    docker_path = env.parent.parent

    # create docker env in sdk path
    sp.call(fr"docker create -it --rm -h Change_log --name Change_log -v {docker_path}:/_ l601306339/autorest")
    sp.call("docker start Change_log")

    # install azure tools
    sp.call(f'docker exec -it Change_log /bin/bash -c  "python _/scripts/dev_setup.py -p azure-core"  ')

    # get all azure-mgmt-package paths
    in_files = glob.glob(str(Path(f'{docker_path}/sdk/*/azure-mgmt-*')))
    for i in in_files[0:1]:
        path = Path(i)
        service_name = path.parts[-1]
        print(service_name)

        # get package version in pypi
        client = PyPIClient()
        versions = [str(v) for v in client.get_ordered_versions(f"{service_name}")]
        if len(versions) >= 2:
            older_version = versions[-2]
            last_version = versions[-1]

            # generate code_report
            cmd_last_version = fr'docker exec -it Change_log /bin/bash -c "cd _/ && python -m packaging_tools.code_report  {service_name} --version={last_version}"'
            cmd_older_version = fr'docker exec -it Change_log /bin/bash -c "cd _/ && python -m packaging_tools.code_report {service_name} --version={older_version}"'
            last_code_report_info = create_code_report(cmd_last_version, service_name)
            older_code_report_info = create_code_report(cmd_older_version, service_name)

            # get code_report path
            route_last_version = find_report_name(last_code_report_info)
            route_older_version = find_report_name(older_code_report_info)

            # use change_log on these two code_reports
            try:
                result = sp.getoutput(
                    fr'docker exec -it Change_log /bin/bash -c "python -m packaging_tools.change_log {route_older_version} {route_last_version}"')
            except Exception as e:
                print(e)
            output_message = result.split("\n")
            result_text = ""
            for i in output_message[1:]:
                result_text = result_text + str(i) + "\n"
            print(result_text)

            # write a txt to save change_log
            change_log_foldor_path = str(env/"Change_Log")
            create_folder(change_log_foldor_path)
            write_txt(change_log_foldor_path, service_name, result_text, last_version, older_version)

    if error_packages_info:
        for k, v in error_packages_info.items():
            print(f'== {k} encountered an error, info: {v}')

    # exit and stop docker
    sp.call(f'docker exec -it Change_log /bin/bash -c "exit"')
    sp.call(f'docker stop Change_log')
