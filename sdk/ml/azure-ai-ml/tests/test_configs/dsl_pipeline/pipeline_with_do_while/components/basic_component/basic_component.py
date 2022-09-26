import argparse

from mldesigner._component_executor import ExecutorBase

parser = argparse.ArgumentParser()
parser.add_argument("--component_in_number", type=int)
parser.add_argument("--component_in_path", type=str)
parser.add_argument("--output_in_path", type=str)

args = parser.parse_args()

lines = [f"component_in_number: {args.component_in_number}", f"component_in_path: {args.component_in_path}"]

with open(args.component_in_path, "r") as file:
    content = file.read()
    try:
        component_in_number = int(content)
    except Exception:
        component_in_number = args.component_in_number

output_in_num = component_in_number - 1

with open(args.output_in_path, "w") as file:
    file.write(str(output_in_num))

control_output_content = '{"is_number_larger_than_zero": %s}' % (str(output_in_num > 0))
ExecutorBase._write_control_outputs_to_run_history(control_output_content=control_output_content)
