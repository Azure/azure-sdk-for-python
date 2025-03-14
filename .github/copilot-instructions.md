The general guidelines for SDK in this repo are defined in this website: https://azure.github.io/azure-sdk/python_design.html. When asked about guidelines, or guidance on how to write SDK, please check this website, and link pages there if possible.

- When asked about how to run pylint, or given a command to run pylint, DO check [this website](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/pylint_checking.md.) and guide the user based on the information you find there. 
- DO use the table in https://github.com/Azure/azure-sdk-tools/blob/cb2e8c2638a2e80e3b9039d7031b72ad32452668/tools/pylint-extensions/azure-pylint-guidelines-checker/README.md and the code examples as a guide on how to fix each rule. 
- DO refer to the pylint documentation: https://pylint.readthedocs.io/en/stable/user_guide/checkers/features.html.
- DO disable pylint checkers if we cannot fix them or leave the code alone.


- DO NOT solve a pylint warning if you are not 100% confident about the answer. If you think your approach might not be the best, stop trying to fix the warning and leave it as is.
- DO NOT create a new file when solving a pylint error, all solutions must remain in the current file.
- DO NOT make up or create modules or imports that do not exist to solve a pylint warning.
- DO NOT make larger changes where a smaller change would fix the issue.

You want to follow best python coding practices and ensure the code runnable.