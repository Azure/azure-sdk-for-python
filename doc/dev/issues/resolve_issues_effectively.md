# Resolve Issues Effectively

Azure Python SDK is an open-source project. It allows users to create issues in the forum to ask questions, report bugs and provide feedback.

Most issues can be classified into 3 categories. They are

1. Usage error.
2. Feature request.
3. Bug report.

## Usage error (For users)
If you are not familiar with the SDK usage of a service, you can find relevant examples in [this repo][sample repo] in most cases.

For some common errors, you can check [here](## Summary Of Common Errors).

## Feature Request(For users)

See [here][request_a_feature] for more details.

## Bug Report (For users)

Please describe the bug in as much detail as possible, such as listing the SDK package name, version and operating system info you use.

If you can provide detailed reproduction steps, it will help us locate and solve the issue.

<hr/>

## Summary Of Common Errors

### Error from Track1 to Track2
If the code you use needs to set wait() function for the Long Running Operation to wait for the result, it should be the SDK of Track1. We have stopped maintenance at present.

We strongly recommend that you update the SDK version. Then you will find that in the SDK of Track2, we all use the function name prefixed with `begin_` for LRO operations, and the result() method can be used to get the returned result.

### Error from Service
Since the python SDK is generated based on the [rest API][rest API], it will not deliberately change the returned results. So if you have any questions about the response result value of the request, please open the issue under the [rest issue][rest issue].

### Error like (AttributeError: 'PipelineResponse' object has no attribute 'get')
When this error occurs, you can check the version of `msrest`. Currently, for most SDKs, it needs to be >= 0.6.21. FYI: [SDK dependency][SDK dependency]

You could upgrade the dependency before using the SDK to check if the issue has been solved.

<hr/>

## Resolve issue (For contributors)

Bug report is one of the most common issues reported in open-source community. Basic steps to resolve a bug report are

1. Confirm the bug.
2. Locate the fault.
3. Fix the bug.

### Confirm the Bug

Confirm whether it is a bug. If you can definitely identify it is a bug according description of the issue, then go to next step. Otherwise, try to reproduce the bug by yourself. You can ask the issue reporter for details such as version, concrete steps and logs so that you can understand the issue better and it is more likely to be able to reproduce the bug. It is not rare that it is not a bug. Instead, it is a usage error. Refer to "Usage Error" section.

### Locate the Fault

Fault localization is critical to bug fix. Some tips:

1. Analyzing logs. It helps you understand the bug.

2. Step-by-step debugging. Most modern IDEs provide integrated debugging experience.


### Fix the bug

Once you have confirmed the bug and found the fault location, it should be easy to fix the bug. Add a sample if it is missing. Remember to tell users when the fix will released.


## Common Principles

If the issue is not from the SDK but from the [rest API][rest API], you can reply to the user and reopen the issue in the appropriate place.


[sample repo]: https://github.com/Azure-Samples/azure-samples-python-management
[request_a_feature]: https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/how_to_request_a_feature_in_sdk.md
[rest API]: https://github.com/Azure/azure-rest-api-specs
[rest issue]: https://github.com/Azure/azure-rest-api-specs/issues
[SDK dependency]: https://github.com/Azure/azure-sdk-for-python/blob/main/shared_requirements.txt
