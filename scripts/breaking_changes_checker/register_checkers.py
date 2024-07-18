# TODO: Model how we would expect checkers to be declared
from checkers.removed_or_renamed_class import RemovedOrRenamedClassChecker

CHECKERS = {
    "class": [
        RemovedOrRenamedClassChecker()
    ]
}