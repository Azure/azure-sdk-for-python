import os

# Path to _models.py
models_file_path = r"C:\Users\haseidfa\Work\Spatio\repo\azure-sdk-for-python\sdk\planetarycomputer\azure-planetarycomputer\azure\planetarycomputer\models\_models.py"

# Read the file content
with open(models_file_path, 'r', encoding='utf-8') as file:
    content = file.read()

# Replace 'datetime.datetime' with 'datetime'
fixed_content = content.replace('datetime.datetime', 'datetime')

# Write the fixed content back to the file
with open(models_file_path, 'w', encoding='utf-8') as file:
    file.write(fixed_content)

print("✅ All 'datetime.datetime' occurrences have been replaced with 'datetime'.")
