# Get the Unreleased Package

This guide is to help Python SDK users to get unreleased package.

(1) Submit a draft PR to https://github.com/Azure/azure-rest-api-specs.

(Any modification is OK, because only the pipeline needs to be triggered)
![img.png](unreleased_package_guide_example1.png)

(2) Wait until swagger generation artifacts is complete.

The following figure shows the wheel and zip of the package.Click to download them.
![img.png](unreleased_package_guide_example2.png)

## Note
(1) If there is no link in the figure above, it may be folded. You can also find it in the check.
![img.png](unreleased_package_guide_example3.png)

(2) [Private repo](https://github.com/Azure/azure-rest-api-specs-pr) can only be triggered when the target branch is main