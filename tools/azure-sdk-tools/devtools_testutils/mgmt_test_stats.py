import os
import re

pattern = ".\/sdk\/[a-z]+\/azure-mgmt-[a-z-]+$" 
dirs = [x[0] for x in os.walk(".") if re.match(pattern, x[0])]
print(dirs)
print(len(dirs))
