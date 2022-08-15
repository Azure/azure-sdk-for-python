import argparse
import os
from datetime import datetime

print("Hello Python World")

parser = argparse.ArgumentParser()
parser.add_argument("--input_data", type=str)
parser.add_argument("--input_string", type=str)
parser.add_argument("--output_data", type=str)

args = parser.parse_args()

print("sample_input_string: %s" % args.input_string)
print("sample_input_data path: %s" % args.input_data)
print("sample_output_data path: %s" % args.output_data)

if os.path.isdir(args.input_data) == True:
    print("files in input_data path: ")
    arr = os.listdir(args.input_data)
    print(arr)

    for filename in arr:
        print("reading file: %s ..." % filename)
        with open(os.path.join(args.input_data, filename), "r") as handle:
            print(handle.read())
elif os.path.isfile(args.input_data) == True:
    with open(args.input_data, "r") as handle:
        print(handle.read())
else:
    print("input_data is neither directory nor a file: " + args.input_data)

cur_time_str = datetime.now().strftime("%b-%d-%Y-%H-%M-%S")

print("Writing file: %s" % os.path.join(args.output_data, "file-" + cur_time_str + ".txt"))
with open(os.path.join(args.output_data, "file-" + cur_time_str + ".txt"), "wt") as text_file:
    print(f"Logging date time: {cur_time_str}", file=text_file)
