# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import inspect

from sphinx.ext.autodoc import MethodDocumenter


class WrappedMethodDocumenter(MethodDocumenter):
    """Resolve overloaded method annotations in their defining module."""

    def format_signature(self, **kwargs):
        if (
            self.analyzer
            and ".".join(self.objpath) in self.analyzer.overloads
            and self.config.autodoc_typehints != "none"
        ):
            method = self.object
            # Sphinx 8.2 evaluates overloads in the wrapper's __globals__.
            self.object = inspect.unwrap(method, stop=lambda obj: hasattr(obj, "__signature__"))
            try:
                return super().format_signature(**kwargs)
            finally:
                self.object = method
        return super().format_signature(**kwargs)


def setup(app):
    app.setup_extension("sphinx.ext.autodoc")
    app.add_autodocumenter(WrappedMethodDocumenter, override=True)
    return {"parallel_read_safe": True, "parallel_write_safe": True}
