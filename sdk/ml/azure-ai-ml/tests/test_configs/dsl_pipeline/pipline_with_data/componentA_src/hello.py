import argparse
import os
from datetime import datetime

parser = argparse.ArgumentParser()
parser.add_argument("--componentA_input", type=str)
parser.add_argument("--componentA_output", type=str)

print("Hello Python World...\nI'm componentA :-)")

args = parser.parse_args()

print("componentA_input path: %s" % args.componentA_input)
print("componentA_output path: %s" % args.componentA_output)

print("files in input path: ")
arr = os.listdir(args.componentA_input)
print(arr)

for filename in arr:
    print("reading file: %s ..." % filename)
    with open(os.path.join(args.componentA_input, filename), "r") as handle:
        print(handle.read())

cur_time_str = datetime.now().strftime("%b-%d-%Y-%H-%M-%S")

print("Writing file: %s" % os.path.join(args.componentA_output, "file-" + cur_time_str + ".txt"))
with open(os.path.join(args.componentA_output, "file-" + cur_time_str + ".txt"), "wt") as text_file:
    print(f"Logging date time: {cur_time_str}", file=text_file)
