# Python SDK Pylint Guide

Cheat sheet for pylint general guidelines in the Python client SDK library. 


### General Guidance 

How pylint works, how to run it, how to install , what pylint warnings look like -- what do the different types mean 

- Do follow the [Azure SDK for Python Guidelines](https://guidelinescollab.github.io/azure-sdk/python_introduction.html) when writing code. 
- Run pylint : `tox -e pylint -c ../../../eng/tox/tox.ini`
- 



### Ignoring Pylint Checkers

how and when to ignore pylint checkers, status for ignoring really bad custom checkers versus specific ones add to pylintrc file


### Updating Pylint Checker Plugin Steps

Explain the custom checkers here, or the process of how to create a custom checker and add it to the custom plugin and how the custom plugin works on apiview and how to add it to the ci etc. 

how to implement updates to the checkers 


### Updating Pylint Version Steps

when there is a version bump how will that be handled by the CI and how to deal with it 