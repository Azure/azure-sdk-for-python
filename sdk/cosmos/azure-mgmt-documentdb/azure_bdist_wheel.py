#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

from distutils import log as logger
import os.path

from wheel.bdist_wheel import bdist_wheel
class azure_bdist_wheel(bdist_wheel):
    """The purpose of this class is to build wheel a little differently than the sdist,
    without requiring to build the wheel from the sdist (i.e. you can build the wheel
    directly from source).
    """

    description = "Create an Azure wheel distribution"

    user_options = bdist_wheel.user_options + \
        [('azure-namespace-package=', None,
            "Name of the deepest nspkg used")]

    def initialize_options(self):
        bdist_wheel.initialize_options(self)
        self.azure_namespace_package = None

    def finalize_options(self):
        bdist_wheel.finalize_options(self)
        if self.azure_namespace_package and not self.azure_namespace_package.endswith("-nspkg"):
            raise ValueError("azure_namespace_package must finish by -nspkg")

    def run(self):
        if not self.distribution.install_requires:
            self.distribution.install_requires = []
        self.distribution.install_requires.append(
            "{}>=2.0.0".format(self.azure_namespace_package))
        bdist_wheel.run(self)

    def write_record(self, bdist_dir, distinfo_dir):
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
        bdist_wheel.write_record(self, bdist_dir, distinfo_dir)
cmdclass = {
    'bdist_wheel': azure_bdist_wheel,
}
