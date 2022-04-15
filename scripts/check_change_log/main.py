# coding=utf-8
import glob
import os
import subprocess as sp
import time
from pypi_tools.pypi import PyPIClient
from pathlib import Path


def find_report_name(result):
    pattern = 'written to'
    merged = 'merged_report'
    for line in result:
        idx = line.find(pattern)
        idx1 = line.find(merged)
        if idx > 0 and idx1 > 0:
            return "_/" + line[idx + len(pattern):].replace(" ", "")

    for line in result:
        idx = line.find(pattern)
        if idx > 0:
            return "_/" + line[idx + len(pattern):].replace(" ", "")

    return ''

def create_foldor(name):
    if not os.path.exists(name):
        os.mkdir(name)
        print("create successful")
    else:
        print("foldor has been created")

def write_txt(foldor, text_name, text, version1, version2):
    foldor_path = r'{0}\\'.format(foldor)
    path = foldor_path + text_name + " " + version1 + "-" + version2 + r".txt"
    file = open(path, "w", encoding="utf-8")
    file.write(text)
    print("txt create successful")
    file.close()

def create_code_report(cmd):
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
    in_files = glob.glob(f'{docker_path}\sdk\*\*mgmt*')
    for i in in_files:
        t = i.split('\\\\')
        mgmt_path_list = t[0].split('\\')
        print(t)
        package_name = mgmt_path_list[3]
        service_name = mgmt_path_list[5]

        # get package version in pypi
        client = PyPIClient()
        versions = [str(v) for v in client.get_ordered_versions(f"{service_name}")]
        if len(versions) >= 2:
            version = versions[-2]
            last_version = versions[-1]

            # generate code_report
            cmd_cl1 = fr'docker exec -it Change_log /bin/bash -c "cd _/ && python -m packaging_tools.code_report  {service_name} --version={last_version}"'
            cmd_cl2 = fr'docker exec -it Change_log /bin/bash -c "cd _/ && python -m packaging_tools.code_report {service_name} --version={version}"'
            last_info = create_code_report(cmd_cl1)
            info = create_code_report(cmd_cl2)

            # get code_report path
            last_route = find_report_name(last_info)
            route = find_report_name(info)

            # use change_log on these two code_reports
            result_text = sp.getoutput(
                fr'docker exec -it Change_log /bin/bash -c "python -m packaging_tools.change_log {route} {last_route}"')
            print(result_text)

            # write a txt to save change_log
            env = Path.cwd()
            change_log_foldor_path = str(env) + r"\Change_Log"
            create_foldor(change_log_foldor_path)
            write_txt(change_log_foldor_path, service_name, result_text, last_version, version)
        else:
            continue

    # exit and stop docker
    sp.call(f'docker exec -it Change_log /bin/bash -c "exit"')
    sp.call(f'docker stop Change_log')
