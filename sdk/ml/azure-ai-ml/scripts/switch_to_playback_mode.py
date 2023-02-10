# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import re
import dotenv


def __main__():
    env_path = dotenv.find_dotenv()
    with open(env_path, "r") as f:
        lines = f.readlines()

    environment_variables = dotenv.dotenv_values(env_path)

    def update_bool_env(env_name, expected_bool: bool):
        expected_line = f"{'' if expected_bool else '#'}{env_name}=\"true\"\n"
        if env_name in environment_variables and expected_bool is True:
            return
        if env_name not in environment_variables and expected_bool is False:
            return

        updated = False
        for i, line in enumerate(lines):
            if re.match(r"#? *" + env_name + r" *=.*", line):
                lines[i] = expected_line
                updated = True
        if not updated:
            lines.append(expected_line)

    update_bool_env("AZURE_TEST_RUN_LIVE", False)
    update_bool_env("AZURE_SKIP_LIVE_RECORDING", True)

    with open(env_path, "w") as f:
        f.writelines(lines)


if __name__ == "__main__":
    __main__()
