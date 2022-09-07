import argparse
import os
import shutil
from pathlib import Path

print("Get file and tabular data")

parser = argparse.ArgumentParser()
parser.add_argument("--input_data", type=str)
parser.add_argument("--file_output_data", type=str)
parser.add_argument("--tabular_output_data", type=str)

args = parser.parse_args()

print("sample_input_data path: %s" % args.input_data)
print("sample_file_output_data path: %s" % args.file_output_data)
print("sample_tabular_output_data path: %s" % args.tabular_output_data)

print("files in input_data path: ")
arr = os.listdir(args.input_data)
print(arr)

for folder_name in arr:
    data_path = args.input_data + "/" + folder_name
    files = os.listdir(data_path)
    print(files)
    if folder_name == "mnist-data":
        output_dir = Path(args.file_output_data)
        print("file_output_dir", output_dir)
        print("file_output_dir exits", Path(output_dir).exists())

        for file_path in files:
            file_source = Path(data_path + "/" + file_path)
            print("Processing {}".format(file_source))
            assert file_source.exists()
            file_destination = Path(output_dir) / file_source.name
            print("file_destination:", file_destination)
            shutil.move(file_source, file_destination)

    elif folder_name == "iris-mltable":
        output_dir = Path(args.tabular_output_data)
        print("tabular_output_dir", output_dir)
        print("tabular_output_dir exits", Path(output_dir).exists())

        for file_path in files:
            file_source = Path(data_path + "/" + file_path)
            print("Processing {}".format(file_source))
            assert file_source.exists()
            file_destination = Path(output_dir) / file_source.name
            print("file_destination:", file_destination)
            shutil.move(file_source, file_destination)
    else:
        pass
