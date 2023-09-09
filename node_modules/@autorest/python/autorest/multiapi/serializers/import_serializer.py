# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from copy import deepcopy
from typing import Dict, Set, Optional, List, Tuple, Union
from ..models import ImportType, FileImport, TypingSection
from ..utils import convert_list_to_tuple


def _serialize_package(
    package_name: str,
    module_list: Set[
        Optional[
            Union[
                str,
                Tuple[
                    str,
                    str,
                ],
                Tuple[
                    str,
                    Optional[str],
                    Tuple[Tuple[Tuple[int, int], str, Optional[str]]],
                ],
            ]
        ]
    ],
    delimiter: str,
) -> str:
    buffer = []

    versioned_modules = set()
    normal_modules = set()
    for m in module_list:
        if m and isinstance(m, (tuple, list)) and len(m) > 2:
            versioned_modules.add(convert_list_to_tuple(m))
        else:
            normal_modules.add(m)
    if None in normal_modules:
        buffer.append(f"import {package_name}")
    if normal_modules != {None} and len(normal_modules) > 0:
        buffer.append(
            "from {} import {}".format(
                package_name,
                ", ".join(
                    sorted(
                        [
                            mod if isinstance(mod, str) else f"{mod[0]} as {mod[1]}"
                            for mod in normal_modules
                            if mod is not None
                        ]
                    )
                ),
            )
        )
    for submodule_name, alias, version_modules in versioned_modules:
        for n, (version, module_name, comment) in enumerate(version_modules):
            buffer.append(
                "{} sys.version_info >= {}:".format("if" if n == 0 else "elif", version)
            )
            buffer.append(
                f"    from {module_name} import {submodule_name}{f' as {alias}' if alias else ''}"
                f"{f' # {comment}' if comment else ''}"
            )
        buffer.append("else:")
        buffer.append(
            f"    from {package_name} import {submodule_name}{f' as {alias}' if alias else ''}"
            "  # type: ignore  # pylint: disable=ungrouped-imports"
        )
    return delimiter.join(buffer)


def _serialize_type(
    import_type_dict: Dict[
        str,
        Set[
            Optional[
                Union[
                    str,
                    Tuple[
                        str,
                        str,
                    ],
                    Tuple[
                        str,
                        Optional[str],
                        Tuple[Tuple[Tuple[int, int], str, Optional[str]]],
                    ],
                ]
            ]
        ],
    ],
    delimiter: str,
) -> str:
    """Serialize a given import type."""
    import_list = []
    for package_name in sorted(list(import_type_dict.keys())):
        module_list = import_type_dict[package_name]
        import_list.append(_serialize_package(package_name, module_list, delimiter))
    return delimiter.join(import_list)


def _get_import_clauses(
    imports: Dict[
        ImportType,
        Dict[
            str,
            Set[
                Optional[
                    Union[
                        str,
                        Tuple[
                            str,
                            str,
                        ],
                        Tuple[
                            str,
                            Optional[str],
                            Tuple[Tuple[Tuple[int, int], str, Optional[str]]],
                        ],
                    ]
                ]
            ],
        ],
    ],
    delimiter: str,
) -> List[str]:
    import_clause = []
    for import_type in ImportType:
        if import_type in imports:
            import_clause.append(_serialize_type(imports[import_type], delimiter))
    return import_clause


class FileImportSerializer:
    def __init__(self, file_import: FileImport, typing_definitions: str = "") -> None:
        self._file_import = file_import
        self._typing_definitions = typing_definitions

    def _switch_typing_section_key(self, new_key: TypingSection):
        switched_dictionary = {}
        switched_dictionary[new_key] = self._file_import.imports[
            TypingSection.CONDITIONAL
        ]
        return switched_dictionary

    def _get_imports_dict(
        self, baseline_typing_section: TypingSection, add_conditional_typing: bool
    ):
        # If this is a python 3 file, our regular imports include the CONDITIONAL category
        # If this is not a python 3 file, our typing imports include the CONDITIONAL category
        file_import_copy = deepcopy(self._file_import)
        if add_conditional_typing and self._file_import.imports.get(
            TypingSection.CONDITIONAL
        ):
            # we switch the TypingSection key for the CONDITIONAL typing imports so we can merge
            # the imports together
            switched_imports_dictionary = self._switch_typing_section_key(
                baseline_typing_section
            )
            switched_imports = FileImport(switched_imports_dictionary)
            file_import_copy.merge(switched_imports)
        return file_import_copy.imports.get(baseline_typing_section, {})

    def _add_type_checking_import(self):
        if self._file_import.imports.get(TypingSection.TYPING):
            self._file_import.add_submodule_import(
                "typing", "TYPE_CHECKING", ImportType.STDLIB
            )

    def __str__(self) -> str:
        self._add_type_checking_import()
        regular_imports = ""
        regular_imports_dict = self._get_imports_dict(
            baseline_typing_section=TypingSection.REGULAR,
            add_conditional_typing=True,
        )

        if regular_imports_dict:
            regular_imports = "\n\n".join(
                _get_import_clauses(regular_imports_dict, "\n")
            )

        typing_imports = ""
        typing_imports_dict = self._get_imports_dict(
            baseline_typing_section=TypingSection.TYPING,
            add_conditional_typing=False,
        )
        if typing_imports_dict:
            typing_imports += "\n\nif TYPE_CHECKING:\n    # pylint: disable=unused-import,ungrouped-imports\n    "
            typing_imports += "\n\n    ".join(
                _get_import_clauses(typing_imports_dict, "\n    ")
            )

        return regular_imports + typing_imports + self._typing_definitions
