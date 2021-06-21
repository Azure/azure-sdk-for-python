import os
import subprocess

def start_testserver():
    os.environ["FLASK_APP"] = "coretestserver"
    cmd = "flask run"
    if os.name == 'nt': #On windows, subprocess creation works without being in the shell
        result = subprocess.Popen(cmd, env=dict(os.environ))
    else:
        result = subprocess.Popen(cmd, shell=True, preexec_fn=os.setsid) #On linux, have to set shell=True
    print('##vso[task.setvariable variable=FLASK_PID]{}'.format(result.pid))
    print("This is used in the pipelines to set the FLASK_PID env var. If you want to stop this testserver, kill this PID.")
    return result

if __name__ == "__main__":
    start_testserver()
