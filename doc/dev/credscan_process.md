# Guide for monitoring CredScan checks

Hi

This guide describes how package owners can monitor their package's Credential Scanner (CredScan) status and correct
any warnings.

General information about CredScan can be found in the overview documentation at [aka.ms/credscan][credscan_doc]. The
Azure SDK's motivation and methodology for running CredScan is documented [here][devops_doc].

## Table of Contents

- [Check CredScan status](#check-credscan-status)
- [Correct active warnings](#correct-active-warnings)
  - [True positives](#true-positives)
  - [False positives](#false-positives)
- [Correct baselined warnings](#correct-baselined-warnings)

## Check CredScan status

CredScan checks are integrated into CI, and files affected by a PR will be scanned as part of the "Compliance" pipeline
job. The results of this scan can be viewed in the [CredScan result analysis][ci_scan_output] task's output.

CredScan is also run each night over the entire `azure-sdk-for-python` repository as part of the
[python - aggregate-reports][aggregate_reports] pipeline. The scan produces a list of active warnings in the
[CredScan result analysis][aggregate_reports_output] task's output as part of the "ComplianceTools" job.

Each warning will begin with an error code and the path to the file containing a potential credential, as well as the
row and column where the credential string begins. For example, for a potential credential that starts in row 3 and
column 20 of a particular file:

```
##[error]1. Credential Scanner Error CSCAN-GENERAL0030 - File: sdk/{service}/{package}/{file}.py:sdk/{service}/{package}/{file}.py(3,20)
```

The warning will then list a description of why the potential credential was flagged. The code of the particular error
will vary depending on the kind of potential credential that was discovered.

## Correct active warnings

If you find any warnings listed for a package you own, the next step is to determine if the potential credential found
by CredScan is an actual credential (a true positive), or a fake credential/false flag (a false positive).

### True positives

If CredScan discovers an actual credential, please contact the EngSys team at azuresdkengsysteam@microsoft.com so any
remediation can be done.

### False positives

If CredScan flags something that's not actually a credential or secret, we can suppress the warning to shut off the
false alarm. CredScan allows you to suppress fake credentials by either suppressing a string value or by suppressing
warnings for a whole file. **Files that contain more than just fake credentials shouldn't be suppressed.**

Credential warnings are suppressed in [eng/CredScanSuppression.json][suppression_file]. Suppressed string values are in
the `"placeholder"` list, and suppressed files are in the `"file"` list under `"suppressions"`.

If you have a fake credential flagged by CredScan, try one of the following (listed from most to least preferable):

- Import and use a suitable credential from our centralized fake secret store: [`devtools_testutils.fake_credentials`][fake_credentials].
- Import and use a suitable credential from another file that's already suppressed in [eng/CredScanSuppression.json][suppression_file].
- Replace the credential with a string value that's already suppressed in [eng/CredScanSuppression.json][suppression_file].
- Move the credential into [devtools_testutils/fake_credentials.py][fake_credentials].
- Move the credential into a `fake_credentials.py` file in your package, and add the file path to the list of suppressed files if necessary.
- Add the credential to the list of suppressed string values.

Ideally, fake credential files -- which contain nothing but fake secrets -- should be suppressed and their fake
credentials shouldn't appear in any other files. Sanitizers should be used to keep fake credentials out of test
recordings when possible. String value suppression should be avoided unless the string appears in many files.

Suppressing string values will disable warnings no matter where the string comes up during a scan, but is inefficient
and inconvenient for lengthy strings. Suppressing warnings in a file is convenient for fake credential files, but
strings in that file will still trigger warnings if present in another unsuppressed file.

## Correct baselined warnings

In addition to active warning that appear in the [python - aggregate-reports][aggregate_reports] pipeline ouput, there
are also CredScan warnings that have been suppressed in [eng/python.gdnbaselines][baseline]. This file is a snapshot of
the active warnings at one point in time; CredScan won't re-raise warnings that have been recorded here.

Ultimately, we hope to remove this baseline file from the repository entirely. If you see any warnings for a package
that you own in this file, please remove a few at a time from the file so that CredScan will output these warnings in
the pipeline. Then, resolve them following the steps from the [Correct active warnings](#correct-active-warnings)
section of this guide.

[AGGREGATE_REPORTS]: https://dev.azure.com/azure-sdk/internal/\_build?definitionId=1401&\_a=summary
[AGGREGATE_REPORTS_OUTPUT]: https://dev.azure.com/azure-sdk/internal/\_build/results?buildId=1411446&view=logs&j=9e400fad-ff47-5b38-f9dc-cae2431972da&t=8613334a-c306-55ea-63ff-80c6e8e0a0ca
[BASELINE]: https://github.com/Azure/azure-sdk-for-python/blob/main/eng/python.gdnbaselines
[CI_SCAN_OUTPUT]: https://dev.azure.com/azure-sdk/public/\_build/results?buildId=1426258&view=logs&jobId=b70e5e73-bbb6-5567-0939-8415943fadb9&j=bc67675d-56bf-581f-e0a2-208848ba68ca&t=7eee3a58-6120-518b-7fcb-7e943712aa81
[CREDSCAN_DOC]: https://aka.ms/credscan
[DEVOPS_DOC]: https://dev.azure.com/azure-sdk/internal/\_wiki/wikis/internal.wiki/413/Credential-Scan-Step-in-Pipeline
[FAKE_CREDENTIALS]: https://github.com/Azure/azure-sdk-for-python/blob/main/tools/azure-sdk-tools/devtools_testutils/fake_credentials.py
[SUPPRESSION_FILE]: https://github.com/Azure/azure-sdk-for-python/blob/main/eng/CredScanSuppression.json
