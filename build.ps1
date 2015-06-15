#
# build.ps1
#
# TODO: integrate this into the root setup.py
#

$packages = @(
    "azure-_core",
    "azure-common",
    "azure-mgmt-_core",
    "azure-mgmt-compute",
    "azure-mgmt-network",
    "azure-mgmt-resource",
    "azure-mgmt-storage",
    "azure-servicebus",
    "azure-servicemanagement-legacy",
    "azure-storage"
)

$bundles = @(
    "azure",
    "azure-mgmt"
)

function build-sdist($package, $target) {
    pushd $package
    py -3.4-32 setup.py sdist
    Copy-Item -Force "dist\*.zip" $($target)
    popd
}

function build-wheel($package) {
    py -3.4-32 -m pip wheel --no-index --no-deps $package
}

$sdist_target = Join-Path $PSScriptRoot dist
mkdir $sdist_target -Force

foreach ($package in ($packages + $bundles)) {
    build-sdist $package $sdist_target
}

pushd $sdist_target
foreach ($package in $packages) {
    $item = Get-Item ($package + "*.zip")
    build-wheel $item.name
}
popd
