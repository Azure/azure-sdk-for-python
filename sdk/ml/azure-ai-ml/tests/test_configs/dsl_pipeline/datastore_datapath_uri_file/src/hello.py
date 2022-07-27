
import argparse
import os
from datetime import datetime
from pathlib import Path

print ("Hello Python World")

parser = argparse.ArgumentParser()
parser.add_argument("--input_data", type=str)
parser.add_argument("--input_string", type=str)
parser.add_argument("--output_data", type=str)

args = parser.parse_args()

print("sample_input_string: %s" % args.input_string)
print("sample_input_data path: %s" % args.input_data)
print("sample_output_data path: %s" % args.output_data)

fpath = args.input_data
if not os.path.isdir(fpath):
    fpath = Path(fpath).parent.absolute()

print("files in input_data: ")
arr = os.listdir(fpath)
print(arr)

for filename in arr:
    print("########### Reading file: %s ..." % filename)
    fp = os.path.join(fpath, filename)
    if os.path.isfile(fp):
        with open(fp, 'r') as handle:
            print(handle.read())

if args.output_data:
    cur_time_str = datetime.now().strftime("%b-%d-%Y-%H-%M-%S")
    print("########### Writing file: %s" % os.path.join(args.output_data,"file-" + cur_time_str + ".txt"))
    with open(os.path.join(args.output_data, "file-" + cur_time_str + ".txt"), "wt") as text_file:
        print(f"Logging date time: {cur_time_str}", file=text_file)

