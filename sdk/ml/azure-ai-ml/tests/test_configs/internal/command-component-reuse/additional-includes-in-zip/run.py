# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------


import sys
from library3.hello import say_hello

sys.path.append('library2.zip')

from library2.greetings import greetings  # pylint: disable=wrong-import-position

# to run locally
# import os
# dir_path = os.path.dirname(os.path.realpath(__file__))
# sys.path.append(f'{dir_path}\\..\\src\\python\\')
# sys.path.append(f'{dir_path}\\..\\src1\\')
# print(sys.path)


if __name__ == '__main__':
    say_hello()
    greetings()