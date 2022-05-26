import argparse
import os
from datetime import datetime

parser = argparse.ArgumentParser()
parser.add_argument("--componentB_input", type=str)
parser.add_argument("--componentB_output", type=str)

print ("Hello Python World...\nI'm componentB :-)")

args = parser.parse_args()

print("componentB_input path: %s" % args.componentB_input)
print("componentB_output path: %s" % args.componentB_output)

print("files in input path: ")
arr = os.listdir(args.componentB_input)
print(arr)

for filename in arr:
    print ("reading file: %s ..." % filename)
    with open(os.path.join(args.componentB_input, filename), 'r') as handle:
        print (handle.read())

cur_time_str = datetime.now().strftime("%b-%d-%Y-%H-%M-%S")

print("Writing file: %s" % os.path.join(args.componentB_output,"file-" + cur_time_str + ".txt"))
with open(os.path.join(args.componentB_output,"file-" + cur_time_str + ".txt"), "wt") as text_file:
    print(f"Logging date time: {cur_time_str}", file=text_file)

