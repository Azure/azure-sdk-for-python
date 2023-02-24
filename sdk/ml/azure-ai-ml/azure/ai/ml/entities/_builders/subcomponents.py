# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# This file contains mldesigner decorator-produced components
# that are used within node constructors. Keep imports and 
# general complexity in this file to a minimum.

from mldesigner import command_component, Output


def save_mltable_yaml(path, mltable_paths):
    import os
    path = os.path.abspath(path)

    if os.path.isfile(path):
        raise ValueError(f'The given path {path} points to a file.')

    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)

    save_path = os.path.join(path, 'MLTable')
    # Do not touch - this is MLTable syntax that is needed to mount these paths
    # To the MLTable's inputs
    mltable_file_content = "\n".join(["paths:"] + [f"- folder : {path}" for path in mltable_paths])

    # mltable_yaml_dict = yaml.dump({"paths": mltable_paths}, default_)
    # mltable_yaml_dict[_PATHS_KEY] = self.paths
    with open(save_path, 'w') as f:
        f.write(mltable_file_content)


@command_component()
def aggregate_output(aggregated_output: Output(type="mltable"), **kwargs):
    print("Aggregated Output {}".format(aggregated_output))
    # keys are inputs names (ex: silo_output_silo_1)
    # values are uri_folder paths 
    path_list = [v for v in kwargs.values()] 
    save_mltable_yaml(aggregated_output, path_list)
