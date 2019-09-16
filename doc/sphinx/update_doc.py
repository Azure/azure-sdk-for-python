import os
import argparse
import logging

REF_FOLDER = './ref'
_LOGGER = logging.getLogger(__name__)

# This is a list of ignored files that we don't want to touch
IGNORED_FILES = [
    "azure.rst",
    "modules.rst",
    "setup.rst",
]

def get_sub_package_list(file):
	if not os.path.exists(file):
		return None
	ret = list()
	with open(file) as f:
		for line in f:
			vline = line.strip()
			if((vline.lower() == "submodules") or vline.endswith(" module") or vline.lower().startswith("module ")):
				return ret
			if not vline:
				continue
			if vline.startswith("===="):
				continue
			if vline.startswith("----"):
				continue
			if vline.endswith(" package"):
				continue
			if vline.lower() == "subpackages":
				continue
			if "toctree" in vline.lower():
				continue
			ret.append(vline)
	return ret
	
def update_rst(file, sub_packages):
	if not os.path.exists(file):
		return
	with open(file) as f:
		content = f.readlines()
	with open(file, 'w') as f:
		for line in content:
			if line.endswith(" package\n"):
				new_line = line.replace(" package", "")
				if new_line.strip() in  sub_packages:
					#This is a sub package
					_LOGGER.info(new_line)
					f.write(new_line)
					continue
				#This is a top package
				new_line = new_line.replace(".", "-")
				_LOGGER.info(new_line)
				f.write(new_line)
				continue
			if line.endswith(" module\n"):
				new_line = line.replace(" module", "")
				_LOGGER.info(new_line)
				f.write(new_line)
				continue
			_LOGGER.info(line)
			f.write(line)

def update_doc(ref_folder):
	sub_packages = list()
	files = []
	# r=root, d=directories, f = files
	for r, d, f in os.walk(ref_folder):
		for file in f:
			if '.rst' in file and not(file in IGNORED_FILES):
				files.append(os.path.join(r, file))

	for f in files:
		ret = get_sub_package_list(f)
		if len(ret) > 0:
			sub_packages.extend(ret)
	
	for f in files:
		update_rst(f, sub_packages)

def main():
	parser = argparse.ArgumentParser(
		description='Update documentation file.'
	)
	parser.add_argument('--folder', '-f',
						dest='ref_folder', default=REF_FOLDER,
						help='The folder that stores the rst files [default: %(default)s]')
	parser.add_argument("--debug",
						dest="debug", action="store_true",
						help="Verbosity in DEBUG mode")

	args = parser.parse_args()

	main_logger = logging.getLogger()
	if args.debug:
		logging.basicConfig()
		main_logger.setLevel(logging.DEBUG if args.debug else logging.INFO)

	update_doc(args.ref_folder)

if __name__ == "__main__":
	main()
