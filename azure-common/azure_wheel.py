#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

from distutils import log as logger
import os.path
try:
    from wheel.bdist_wheel import bdist_wheel as original_bdist_wheel
    class bdist_wheel(original_bdist_wheel):
        def write_record(self, bdist_dir, distinfo_dir):
            # following check could be improved, by parsing the package name
            # package_name = self.distribution.get_name()
            possible_init_py = ['azure-', 'azure-mgmt-', 'azure-mgmt-datalake-']
            for azure_sub_package in possible_init_py:
                init_file = os.path.join(bdist_dir, azure_sub_package.replace('-','/'), '__init__.py')
                if os.path.isfile(init_file):
                    logger.info("manually remove {} while building the wheel".format(init_file))
                    os.remove(init_file)
            original_bdist_wheel.write_record(self, bdist_dir, distinfo_dir)
    cmdclass = {
        'bdist_wheel': bdist_wheel,
    }
except ImportError:
    logger.warn("Wheel is not available, disabling bdist_wheel hook")
    cmdclass = {}
