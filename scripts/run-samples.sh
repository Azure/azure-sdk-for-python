#!/bin/bash

success_count=0
failure_count=0
for file in $(find . -type f -name "*sample*.py"); do
  echo "===============$file================="
  if python "$file"; then
    success_count=$((success_count + 1))
  else
    failure_count=$((failure_count + 1))
  fi
done
echo "Success count: $success_count"
echo "Failure count: $failure_count"
if [ $failure_count -gt 0 ]; then
  exit 1
fi
