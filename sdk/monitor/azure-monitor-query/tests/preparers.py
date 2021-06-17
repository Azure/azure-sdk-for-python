  
import functools
import inspect

from azure.identity import DefaultAzureCredential
from devtools_testutils import PowerShellPreparer, is_live

LogsPreparer = functools.partial(
    PowerShellPreparer,
    "azure",
    workspace_id="fake_log_workspace_id",
    secondary_workspace_id="fake_sec_workspace_id",
    workspace_key="fake_log_workspace_key",
    secondary_workspace_key="fake_sec_workspace_key"
)

def trim_kwargs_from_test_function(fn, kwargs):
    # the next function is the actual test function. the kwargs need to be trimmed so
    # that parameters which are not required will not be passed to it.
    if not getattr(fn, "__is_preparer", False):
        try:
            args, _, kw, _, _, _, _ = inspect.getfullargspec(fn)
        except AttributeError:
            args, _, kw, _ = inspect.getargspec(fn)  # pylint: disable=deprecated-method
        if kw is None:
            args = set(args)
            for key in [k for k in kwargs if k not in args]:
                del kwargs[key]

def logs_decorator(func, **kwargs):
    @LogsPreparer()
    def wrapper(*args, **kwargs):
        workspace_id = kwargs.pop("workspace_id")
        secondary_workspace_id = kwargs.pop("secondary_workspace_id")
        secondary_workspace_key = kwargs.pop("secondary_workspace_key")
        workspace_key = kwargs.pop("workspace_key")
        key = DefaultAzureCredential()

        kwargs["workspace_id"] = workspace_id
        kwargs["secondary_workspace_id"] = secondary_workspace_id
        kwargs["credential"] = key
        kwargs["workspace_key"] = workspace_key
        kwargs["secondary_workspace_key"] = secondary_workspace_key

        trimmed_kwargs = {k: v for k, v in kwargs.items()}
        trim_kwargs_from_test_function(func, trimmed_kwargs)

        func(*args, **trimmed_kwargs)

    return wrapper