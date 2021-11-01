## SDK Auto-Release System Assumptions, Gotchas, and Minutiae



## Background

Applying automated processes can reduce labor costs and better respond to more and more SDK releases. It can also speed up the release and reduce some errors caused by human factors.

## Target

1. Speed up the release of SDK by 50%
2. Reduce manual operation by 80%
3. Perfect application in Python SDK,
4. provide customized processes according to Java SDK, Go and other owners.

## Present Situation

The process has been applied to the daily release of Python SDK and good feedback has been obtained.

## Process Implementation(Take Python as an example)

1. Users submit SDK release issue through this [website]([OpenAPI Hub - Azure DevX (azure-devex-tools.com)](https://portal.azure-devex-tools.com/tools/request-api-release)).
2. Parse the link and extract readme link and package name
3. According to the last merge of readme link, changlog is obtained and automatically replied to the user.
4. At the same time, generate the SDK and wait for the user to check
5. After the user confirms, the PR is merged and published to pypi.



## Q&A

1. #### What should I do if the auto reply fails?

   Check whether the readme tag completes the configuration. If it is completed, add the `configure` tag.

2. #### What steps are automated?

   Parse the link, get the package name, reply to the user, check the changelog, automatically close the issue after publishing, and even the link of the pipeline can be found automatically during publishing. 

   If it goes well, all people need to do is see the user approve and click publish

