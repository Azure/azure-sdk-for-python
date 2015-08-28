#
# build.ps1
#
# TODO: integrate this into the root setup.py
#

$packages = @(
    "azure-nspkg",
    "azure-common",
    "azure-mgmt-nspkg",
    "azure-mgmt-common",
    "azure-mgmt-compute",
    "azure-mgmt-network",
    "azure-mgmt-resource",
    "azure-mgmt-storage",
    "azure-servicebus",
    "azure-servicemanagement-legacy"
)

$bundles = @(
    "azure",
    "azure-mgmt"
)

function build-sdist($package, $target) {
    pushd $package
    Remove-Item -Force -Recurse dist
    Remove-Item -Force -Recurse *.egg-info
    py -3.4-32 setup.py sdist
    Copy-Item -Force "dist\*.zip" $($target)
    popd
}

function build-wheel($package) {
    py -3.4-32 -m pip wheel --no-index --no-deps $package
}

$sdist_target = Join-Path $PSScriptRoot dist
Remove-Item -Force -Recurse $sdist_target
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
