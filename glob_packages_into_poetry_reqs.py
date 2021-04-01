import glob
import os

packages = glob.glob('C:/repo/sdk-for-python/sdk/*/*/setup.py')

for pkg in packages:
    name = os.path.dirname(pkg).split(os.sep)[-1]
    path = os.path.dirname(pkg.split('python/')[1]).replace(os.sep, '/')

    print('{} = {{path = "{}"}}'.format(name, path))
   
    