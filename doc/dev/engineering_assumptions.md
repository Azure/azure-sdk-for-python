## Engineering System Assumptions, Gotchas, and Minutae

Build CI for `azure-sdk-for-python` essentially boils down to the following.

1. Install on packages (and their dev_requirements!) in one go.
2. Run `pytest <folder1> <folder2> ....` where folders correspond to package folders
3. All wheels are generated with `universal` flag. We do not currently allow non-universal packages to be shipped out of this repository.
    a. This will change as requirements do