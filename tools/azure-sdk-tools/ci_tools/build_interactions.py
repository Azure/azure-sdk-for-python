import os
from ci_tools.variables import in_ci

def set_ci_variable(name: str, value: str) -> None:
    """
    Sets a runtime variable in azure devops or github actions. The variable will only be available
    AFTER the step which invokes this function is completed.
    """
    ci_type = in_ci()

    if ci_type == 1:
        print(f"##vso[task.setvariable variable={name}]{value}")

    if ci_type == 2:
        env_file = os.getenv('GITHUB_ENV')

        with open(env_file, "a") as env_file:
            env_file.write(f"{name}={value}")
