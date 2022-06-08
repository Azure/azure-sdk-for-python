import os

for key in os.environ:
  print(key + ": " + os.environ[key])