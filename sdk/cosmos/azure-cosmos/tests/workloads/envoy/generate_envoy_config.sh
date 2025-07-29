#!/bin/bash

# Check if the correct number of arguments are provided
if [ "$#" -ne 3 ]; then
    echo "Usage: $0 <template_file_path> <output_envoy_config_file> <account_name>"
    exit 1
fi

# Assign arguments to variables
template_file_path=$1
output_envoy_config_file=$2
account_name=$3

# Replace occurrences of "<>" with the account name and write to the new file
sed "s/<>/$account_name/g" "$template_file_path" > "$output_envoy_config_file"

echo "Replacement complete. The result is saved in $output_envoy_config_file"
