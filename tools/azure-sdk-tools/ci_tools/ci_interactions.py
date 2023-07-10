import os, inspect
from ci_tools.variables import in_ci


def output_ci_warning(message: str, location=None) -> None:
    ci_type = in_ci()

    if ci_type == 1:
        if not location:
            import inspect
            source = inspect.stack()[1].filename
        else:
            source = location

        print(f"##vso[task.logissue type=warning;sourcepath={source}]{message}")
    elif ci_type == 2:
        pass
    else:
        print("Unrecognized CI format, not outputting warning.")
    

def set_ci_variable(name: str, value: str) -> None:
    """
    Sets a runtime variable in azure devops or github actions. The variable will only be available
    AFTER the step which invokes this function is completed.
    """
    ci_type = in_ci()

    if ci_type == 1:
        print(f"##vso[task.setvariable variable={name}]{value}")
    elif ci_type == 2:
        env_file = os.getenv('GITHUB_ENV')

        with open(env_file, "a") as env_file:
            env_file.write(f"{name}={value}")
    else:
        print(f"Unrecognized CI format, not setting variable \"{name}.\"")
