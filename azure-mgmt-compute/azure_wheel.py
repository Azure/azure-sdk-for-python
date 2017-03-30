#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

from distutils import log as logger
import os.path
try:
    from wheel.bdist_wheel import bdist_wheel as original_bdist_wheel
    class azure_bdist_wheel(original_bdist_wheel):

        description = "Create an Azure wheel distribution"

        user_options = original_bdist_wheel.user_options + \
            [('azure-namespace-package=', None,
              "Name of the deepest nspkg used")]

        def initialize_options(self):
            original_bdist_wheel.initialize_options(self)
            self.azure_namespace_package = None

        def finalize_options(self):
            original_bdist_wheel.finalize_options(self)
            if self.azure_namespace_package and not self.azure_namespace_package.endswith("-nspkg"):
                raise ValueError("azure_namespace_package must finish by -nspkg")

        def run(self):
            self.distribution.install_requires.append(
                "{}>=2.0.0".format(self.azure_namespace_package))
            original_bdist_wheel.run(self)

        def write_record(self, bdist_dir, distinfo_dir):
            # following check could be improved, by parsing the package name
            # package_name = self.distribution.get_name()
            if self.azure_namespace_package:
                # Split and remove last part, assuming it's "nspkg"
                subparts = self.azure_namespace_package.split('-')[0:-1]
            folder_with_init = [os.path.join(*subparts[0:i+1]) for i in range(len(subparts))]
            for azure_sub_package in folder_with_init:
                init_file = os.path.join(bdist_dir, azure_sub_package, '__init__.py')
                if os.path.isfile(init_file):
                    logger.info("manually remove {} while building the wheel".format(init_file))
                    os.remove(init_file)
                else:
                    raise ValueError("Unable to find {}. Are you sure of your namespace package?".format(init_file))
            original_bdist_wheel.write_record(self, bdist_dir, distinfo_dir)
    cmdclass = {
        'azure_bdist_wheel': azure_bdist_wheel,
    }
except ImportError:
    logger.warn("Wheel is not available, disabling bdist_wheel hook")
    cmdclass = {}
