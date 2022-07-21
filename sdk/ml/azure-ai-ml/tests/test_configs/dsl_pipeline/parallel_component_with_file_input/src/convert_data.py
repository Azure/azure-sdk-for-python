
import argparse
import os
from pathlib import Path
import shutil

parser = argparse.ArgumentParser()
parser.add_argument("--input_data", type=str)
parser.add_argument("--file_output_data", type=str)

args = parser.parse_args()

print("input_data path: %s" % args.input_data)

print("files in input_data path: ")
arr = os.listdir(args.input_data)
print(arr)

output_dir = Path(args.file_output_data)
print("file_output_dir", output_dir)
print("file_output_dir exits", Path(output_dir).exists())

MLTable = output_dir / "MLTable"
MLTable.write_text("paths:")

for file_name in arr:
    data_path = Path(args.input_data + "/" + file_name)
    print("Processing {}".format(data_path))
    (output_dir / data_path.name).write_text(file_name)
    with MLTable.open(mode='a') as f:
        f.write(f"\n  - file: ./{data_path.name}")
    # shutil.move(data_path, Path(output_dir / data_path.name))
    # MLTable.write_text(f"\t\t-\tfile:\t./{data_path.name}")


