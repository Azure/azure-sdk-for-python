import json
import logging

from json_delta import diff

_LOGGER = logging.getLogger(__name__)


def _build_md(content, title, buffer):
    buffer.append(title)
    buffer.append("")
    for item in content:
        buffer.append("  - " + item)
    buffer.append("")


class ChangeLog:
    def __init__(self, old_report, new_report):
        self.features = []
        self.breaking_changes = []
        self.optional_features = []
        self._old_report = old_report
        self._new_report = new_report
        self.removed_operations = []
        self.added_operations = []

    def sort(self):
        self.features.sort()
        self.breaking_changes.sort()
        self.optional_features.sort()

    def build_md(self):
        self.compare_operation()
        self.sort()
        buffer = []
        if self.features:
            _build_md(sorted(set(self.features), key=self.features.index), "### Features Added", buffer)
        if self.breaking_changes:
            _build_md(
                sorted(set(self.breaking_changes), key=self.breaking_changes.index), "### Breaking Changes", buffer
            )
        if not (self.features or self.breaking_changes) and self.optional_features:
            _build_md(
                sorted(set(self.optional_features), key=self.optional_features.index), "### Features Added", buffer
            )

        return "\n".join(buffer).strip()

    @staticmethod
    def _unpack_diff_entry(diff_entry):
        return diff_entry[0], len(diff_entry) == 1

    def operation(self, diff_entry):
        path, is_deletion = self._unpack_diff_entry(diff_entry)

        # Is this a new operation group?
        _, operation_name, *remaining_path = path
        if not remaining_path:
            if is_deletion:
                self.breaking_changes.append(_REMOVE_OPERATION_GROUP.format(operation_name))
            else:
                self.features.append(_ADD_OPERATION_GROUP.format(operation_name))
            return

        _, *remaining_path = remaining_path
        if not remaining_path:
            # Not common, but this means this has changed a lot. Compute the list manually
            old_ops_name = list(self._old_report["operations"][operation_name]["functions"])
            new_ops_name = list(self._new_report["operations"][operation_name]["functions"])
            for removed_function in set(old_ops_name) - set(new_ops_name):
                self.breaking_changes.append(_REMOVE_OPERATION.format(operation_name, removed_function))
            for added_function in set(new_ops_name) - set(old_ops_name):
                self.features.append(_ADD_OPERATION.format(operation_name, added_function))
            return

        # Is this a new operation, inside a known operation group?
        function_name, *remaining_path = remaining_path
        if not remaining_path:
            # Simplify renaming func to begin_func change, put it into the compare_operation() for processing
            if is_deletion:
                self.removed_operations.append(f'{operation_name}.{function_name}')
            else:
                self.added_operations.append(f'{operation_name}.{function_name}')
            return

        if remaining_path[0] == "metadata":
            # Ignore change in metadata for now, they have no impact
            return

        if remaining_path[0] == "parameters":
            old_parameters_list = self._old_report["operations"][operation_name]["functions"][function_name][
                "parameters"
            ]
            new_parameters_list = self._new_report["operations"][operation_name]["functions"][function_name][
                "parameters"
            ]
            old_parameters = {param_name["name"]: param_name for param_name in old_parameters_list}
            new_parameters = {param_name["name"]: param_name for param_name in new_parameters_list}
            old_parameters_set = set(old_parameters.keys())
            new_parameters_set = set(new_parameters.keys())
            # The new parameter is optional or not. Be breaking change for now.
            for removed_parameter in old_parameters_set - new_parameters_set:
                self.breaking_changes.append(
                    _REMOVE_OPERATION_PARAM.format(operation_name, function_name, removed_parameter)
                )
            for added_parameter in new_parameters_set - old_parameters_set:
                if new_parameters[added_parameter]["has_default_value"]:
                    self.features.append(
                        _ADD_OPERATION_PARAM_FEATURE.format(operation_name, function_name, added_parameter)
                    )
                else:
                    self.breaking_changes.append(
                        _ADD_OPERATION_PARAM.format(operation_name, function_name, added_parameter)
                    )
            return
        raise NotImplementedError(f"Other situations. Be err for now: {str(remaining_path)}")

    def models(self, diff_entry):
        path, is_deletion = self._unpack_diff_entry(diff_entry)

        # Is this a new model?
        _, mtype, *remaining_path = path
        if not remaining_path:
            # Seen once in Network, because exceptions were added. Bypass
            return
        model_name, *remaining_path = remaining_path
        if not remaining_path:
            # If only model removal, it is not features, and not enough to be breaking changes, either.  So put it
            # aside temporarily(https://github.com/Azure/azure-sdk-for-python/pull/22139#discussion_r770187333).
            if not is_deletion:
                self.optional_features.append(_MODEL_ADD.format(model_name))
            return

        # That's a model signature change
        if mtype in ["enums", "exceptions"]:
            # Don't change log anything for Enums for now
            return

        _, *remaining_path = remaining_path
        if not remaining_path:  # This means massive signature changes, that we don't even try to list them
            self.breaking_changes.append(_MODEL_SIGNATURE_CHANGE.format(model_name))
            return

        # This is a real model
        parameter_name, *remaining_path = remaining_path
        is_required = lambda report, model_name, param_name: report["models"]["models"][model_name]["parameters"][
            param_name
        ]["properties"]["required"]
        if not remaining_path:
            if is_deletion:
                self.breaking_changes.append(_MODEL_PARAM_DELETE.format(model_name, parameter_name))
            else:
                # This one is tough, if the new parameter is "required",
                # then it's breaking. If not, it's a feature
                if is_required(self._new_report, model_name, parameter_name):
                    self.breaking_changes.append(_MODEL_PARAM_ADD_REQUIRED.format(model_name, parameter_name))
                else:
                    self.features.append(_MODEL_PARAM_ADD.format(model_name, parameter_name))
            return

        # The parameter already exists
        new_is_required = is_required(self._new_report, model_name, parameter_name)
        old_is_required = is_required(self._old_report, model_name, parameter_name)

        if new_is_required and not old_is_required:
            # This shift from optional to required
            self.breaking_changes.append(_MODEL_PARAM_CHANGE_REQUIRED.format(parameter_name, model_name))
            return

    def client(self, old_report, new_report):
        if new_report.get('client'):
            if old_report.get('client'):
                msg = _CLIENT_SIGNATURE_CHANGE.format(old_report['client'][0], new_report['client'][0])
            else:
                msg = _CLIENT_SIGNATURE_CHANGE_WITHOUT_OLD.format(new_report['client'][0])
            self.breaking_changes.append(msg)
        return

    def compare_operation(self):
        '''
        Record changelog like "rename operation.delete to operation.begin_delete"
        instead of "remove operation.delete or add operation.begin_delete"
        '''
        while self.removed_operations:
            op, old_function  = self.removed_operations.pop().split('.')
            new_function = f'begin_{old_function}'
            if f'{op}.{new_function}' in self.added_operations:
                self.added_operations.remove(f'{op}.{new_function}')
                self.breaking_changes.append(_RENAME_OPERATION.format(op, old_function, op, new_function))
            else:
                self.breaking_changes.append(_REMOVE_OPERATION.format(op, old_function))
        for op_function in self.added_operations:
            operation_name, function_name = op_function.split('.')
            self.features.append(_ADD_OPERATION.format(operation_name, function_name))


## Features
_ADD_OPERATION_GROUP = "Added operation group {}"
_ADD_OPERATION = "Added operation {}.{}"
_ADD_OPERATION_PARAM_FEATURE = "Operation {}.{} has a new optional parameter {}"
_MODEL_PARAM_ADD = "Model {} has a new parameter {}"
_MODEL_ADD = "Added model {}"

## Breaking Changes
_REMOVE_OPERATION_GROUP = "Removed operation group {}"
_REMOVE_OPERATION = "Removed operation {}.{}"
_RENAME_OPERATION = "Renamed operation {}.{} to {}.{}"
_REMOVE_OPERATION_PARAM = "Operation {}.{} no longer has parameter {}"
_CLIENT_SIGNATURE_CHANGE = "Client name is changed from `{}` to `{}`"
_CLIENT_SIGNATURE_CHANGE_WITHOUT_OLD = "Client name is changed to `{}`"
_MODEL_SIGNATURE_CHANGE = "Model {} has a new signature"
_MODEL_PARAM_DELETE = "Model {} no longer has parameter {}"
_MODEL_PARAM_ADD_REQUIRED = "Model {} has a new required parameter {}"
_MODEL_PARAM_CHANGE_REQUIRED = "Parameter {} of model {} is now required"
_ADD_OPERATION_PARAM = "Operation {}.{} has a new required parameter {}"


def build_change_log(old_report, new_report):
    change_log = ChangeLog(old_report, new_report)

    # when diff result is large,  compare_lengths=True may cause wrong result
    result = diff(old_report, new_report, compare_lengths=False)

    for diff_line in result:
        # Operations
        if diff_line[0][0] == "operations":
            change_log.operation(diff_line)
        elif diff_line[0][0] == "models":
            change_log.models(diff_line)
        elif diff_line[0][0] == "client":
            change_log.client(old_report, new_report)

    return change_log


def get_report_from_parameter(input_parameter, tag_is_stable: bool = False):
    if ":" in input_parameter:
        package_name, version = input_parameter.split(":")
        from .code_report import main

        # if tag is preview, just find last version on pypi to create report
        result = main(
            package_name,
            version=version if version not in ["pypi", "latest"] else None,
            last_pypi=version == "pypi",
            last_pypi_stable=tag_is_stable,
        )
        if not result:
            raise ValueError("Was not able to build a report")
        if len(result) == 1:
            with open(result[0], "r") as fd:
                return json.load(fd)

        raise NotImplementedError("Multi-api changelog not yet implemented")

    with open(input_parameter, "r") as fd:
        return json.load(fd)


def main(base, latest, tag_is_stable: bool = False):
    old_report = get_report_from_parameter(base, tag_is_stable)
    new_report = get_report_from_parameter(latest)

    # result = diff(old_report, new_report)
    # with open("result.json", "w") as fd:
    #     json.dump(result, fd)

    change_log = build_change_log(old_report, new_report)
    return change_log.build_md()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="ChangeLog computation",
    )
    parser.add_argument(
        "base",
        help="Base. Could be a file path, or <package_name>:<version>. Version can be pypi, latest or a real version",
    )
    parser.add_argument(
        "latest",
        help="Latest. Could be a file path, or <package_name>:<version>. Version can be pypi, latest or a real version",
    )

    parser.add_argument("--debug", dest="debug", action="store_true", help="Verbosity in DEBUG mode")

    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)

    print(main(args.base, args.latest))
