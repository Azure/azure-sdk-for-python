#!/bin/bash

# Check if the correct number of arguments are provided
if [ "$#" -ne 5 ]; then
    echo "Usage: $0 <template_file_path> <output_envoy_config_file> <account_name> <write_region> <read_region>"
    exit 1
fi

# Assign arguments to variables
template_file_path=$1
output_envoy_config_file=$2
account_name=$3
write_region=$4
read_region=$5

# Replace occurrences of "<>" with the account name
# Replace occurrences of "||" with the write region
# Replace occurrences of "^^" with the read region
# and write to the new file
sed "s/<>/$account_name/g" "$template_file_path" | sed "s/||/$write_region/g" | sed "s/\^\^/$read_region/g" > "$output_envoy_config_file"

echo "Replacement complete. The result is saved in $output_envoy_config_file"
