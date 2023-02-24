TODO:

- [ ] Recognize c-extensions, call `cibuildwheel` instead of `python -m build` against package root in `sdk_build` call
- [ ] Update `azure-extensions-prototype` `pyproject.toml` with necessary additions for cibuildwheel tool config
- [ ] Figure out how to define the targeted matrix from within `pyproject.toml`, set up the targeting matrix there
- [ ] If we can't put the output matrix under `pyproject.toml`, define in `artifact` list with set of platforms
- [ ] Update `create_and_install` to install the appropriate wheel from the wheel output dir
- [ ] Ensure the correct wheel is selected/installed across all tox environments, not just when called in `create_wheel_and_install`.
- [ ] 


Reference below for existing configuration that's working for azure-uamqp-python.
https://github.com/Azure/azure-uamqp-python/blob/5b31ff4fbb824c35320646b912818b2ea9d25239/.azure-pipelines/client.yml#L124

- pwsh: |
      cibuildwheel --output-dir dist .
   displayName: 'Build uAMQP Wheel'
   env:
      CIBW_PRERELEASE_PYTHONS: True
      CIBW_ARCHS_MACOS: x86_64
      CIBW_BUILD: $(BWFilter)

in root pyproject.toml

[tool.cibuildwheel]
# skip musl and pypy
skip = ["*-musllinux*", "pp*"] 
#test-requires = "pytest"
#test-command = "python -X dev -m pytest {project}/tests"

[tool.cibuildwheel.macos.environment]
MACOSX_DEPLOYMENT_TARGET = "10.9"
CMAKE_OSX_DEPLOYMENT_TARGET = "10.9"
CMAKE_OSX_ARCHITECTURES = "x86_64"
UAMQP_USE_OPENSSL = true
UAMQP_REBUILD_PYX = true
UAMQP_SUPPRESS_LINK_FLAGS = true
OPENSSL_ROOT_DIR = "/tmp/openssl"
OPENSSL_INCLUDE_DIR = "/tmp/openssl/include"
LDFLAGS = "-mmacosx-version-min=10.9 -L/tmp/openssl/lib"
CFLAGS = "-mmacosx-version-min=10.9 -I/tmp/openssl/include"

[tool.cibuildwheel.linux]
archs = ["x86_64"]
manylinux-x86_64-image = "manylinux2014"
before-build = "bash utils/install_openssl.sh"
environment = {OPENSSL_ROOT_DIR="/opt/pyca/cryptography/openssl", LIBRARY_PATH="/opt/pyca/cryptography/openssl/lib", CPATH="/opt/pyca/cryptography/openssl/include"}


