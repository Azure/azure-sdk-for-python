# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Real-model lazy construction contracts. Functional tests, not hosted latency evidence."""

from pathlib import Path
import os
import subprocess
import sys

import pytest


def _fresh(code):
    import azure.ai.agentserver.responses as responses

    package_root = Path(responses.__file__).resolve().parents[4]
    env = os.environ.copy()
    env["PYTHONPATH"] = os.pathsep.join(filter(None, (str(package_root), env.get("PYTHONPATH"))))
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    result = subprocess.run(
        [sys.executable, "-B", "-c", code],
        cwd=package_root,
        env=env,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_echo_imports_construct_only_needed_real_types():
    _fresh("""
from typing_extensions import is_typeddict
from azure.ai.agentserver.responses import CreateResponse, ResponseContext, ResponsesAgentServerHost, TextResponse
from azure.ai.agentserver.responses.models._generated import types
loaded=[name for name,value in vars(types).items() if not name.startswith('_') and is_typeddict(value)]
assert len(loaded) <= 3, loaded
assert is_typeddict(CreateResponse)
assert CreateResponse.__module__ == types.__name__
assert CreateResponse.__qualname__ == 'CreateResponse'
assert CreateResponse(model='m', input='hi') == {'model':'m','input':'hi'}
""")


def test_public_type_hints_and_cold_pickle_resolution():
    _fresh("""
import pickle, typing
from azure.ai.agentserver.responses import CreateResponse
from azure.ai.agentserver.responses.models._generated import types
# A normal GLOBAL pickle reference produced by the original class's canonical name.
blob=b'cazure.ai.agentserver.responses.models._generated.types\\nResponseObject\\n.'
cls=pickle.loads(blob)
assert cls is types.ResponseObject
assert pickle.loads(pickle.dumps(cls)) is cls
assert cls.__qualname__ == 'ResponseObject'
assert typing.get_type_hints(CreateResponse)['model'] is str
assert typing.get_type_hints(cls)['model'] is str
assert 'id' in cls.__required_keys__
""")


def test_star_dir_and_original_constructor_behavior():
    _fresh("""
import ast
from pathlib import Path
from typing_extensions import is_typeddict
import azure.ai.agentserver.responses.models as models
from azure.ai.agentserver.responses.models._generated import types
names=set(dir(types))
assert {'CreateResponse','ResponseObject','OpenApiTool','ResponseCreatedEvent'} <= names
assert 'OpenApiTool' not in vars(types)
exports={}
exec('from azure.ai.agentserver.responses.models import *', exports)
for name in models.__all__:
    assert exports[name] is getattr(models,name)
exec('from azure.ai.agentserver.responses.models._generated.types import *', exports)
tree = ast.parse(Path(types.__file__).read_text(encoding='utf-8'))
contract = next(node for node in tree.body if isinstance(node, ast.If))
expected = {node.name for node in contract.body if isinstance(node, ast.ClassDef)}
actual = {name for name,value in vars(types).items() if not name.startswith('_') and is_typeddict(value)}
assert actual == expected
assert types.OpenApiTool(type='openapi') == {'type':'openapi'}
try:
    types.no_such_contract
except AttributeError:
    pass
else:
    raise AssertionError('invalid export accepted')
""")


def test_concurrent_model_access_preserves_canonical_identity():
    _fresh("""
from concurrent.futures import ThreadPoolExecutor
import pickle
import threading
import typing
from typing_extensions import is_typeddict
from azure.ai.agentserver.responses import models
from azure.ai.agentserver.responses.models import _generated
from azure.ai.agentserver.responses.models._generated import types
names = ['CreateResponse', 'ResponseObject', 'Item', 'OutputItem'] * 2
barrier = threading.Barrier(len(names))
def load(name):
    barrier.wait(timeout=10)
    value = getattr(types, name)
    assert value is getattr(types, name)
    assert value is getattr(_generated, name)
    assert value is getattr(models, name)
    restored = pickle.loads(pickle.dumps(value))
    if name in ('CreateResponse', 'ResponseObject'):
        assert is_typeddict(value)
        assert restored is value
    else:
        assert typing.get_origin(value) is typing.Union
        assert restored == value
        assert typing.get_origin(restored) is typing.get_origin(value)
        assert typing.get_args(restored) == typing.get_args(value)
    return value
with ThreadPoolExecutor(max_workers=len(names)) as pool:
    results = list(pool.map(load, names))
assert all(results[index] is results[index + 4] for index in range(4))
""")


def test_model_pickle_contracts_survive_typing_cache_pressure():
    _fresh("""
import pickle
import typing
from typing_extensions import is_typeddict
from azure.ai.agentserver.responses import models
from azure.ai.agentserver.responses.models import _generated
from azure.ai.agentserver.responses.models._generated import types

names = ('CreateResponse', 'ResponseObject', 'Item', 'OutputItem')
originals = {name: getattr(types, name) for name in names}
payloads = {name: pickle.dumps(value) for name, value in originals.items()}
# Exercise typing's caches using only public APIs. Union reconstruction promises
# equivalent types, not object identity, whether a cache entry survives or not.
pressure = [typing.Union[typing.Literal[index], bytes] for index in range(2048)]
assert len(pressure) == 2048
for name, value in originals.items():
    restored = pickle.loads(payloads[name])
    assert getattr(types, name) is value
    assert getattr(_generated, name) is value
    assert getattr(models, name) is value
    if name in ('CreateResponse', 'ResponseObject'):
        assert is_typeddict(value)
        assert restored is value
    else:
        assert typing.get_origin(value) is typing.Union
        assert restored == value
        assert typing.get_origin(restored) is typing.get_origin(value)
        assert typing.get_args(restored) == typing.get_args(value)
""")


def test_generated_output_is_reproducible():
    import importlib.util

    package = Path(__file__).resolve().parents[2]
    script = package / "_scripts" / "lazy_model_emitter.py"
    spec = importlib.util.spec_from_file_location("lazy_model_emitter_test", script)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.emit(package / "azure" / "ai" / "agentserver" / "responses" / "models" / "_generated", check=True)


def test_generator_rejects_unsupported_class_semantics():
    import importlib.util

    script = Path(__file__).resolve().parents[2] / "_scripts" / "lazy_model_emitter.py"
    spec = importlib.util.spec_from_file_location("lazy_model_emitter_rejection_test", script)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    with pytest.raises(ValueError, match="Unsupported generated model base"):
        module.render_module("class Wrong(dict):\n    field: str\n", "types", {"Wrong"})


def test_normal_extraction_pipeline_runs_lazy_generation(tmp_path):
    from _scripts.extract_model_contracts import finalize
    from _scripts.lazy_model_emitter import canonical

    package = Path(__file__).resolve().parents[2]
    original = package / "azure" / "ai" / "agentserver" / "responses" / "models" / "_generated"
    emitted = tmp_path / "emitter" / "models"
    (emitted / "models").mkdir(parents=True)
    for name in ("types.py", "_unions.py"):
        (emitted / name).write_text(canonical((original / name).read_text()), encoding="utf-8")
    (emitted / "py.typed").write_text("")
    for name in ("__init__.py", "_patch.py"):
        (emitted / "models" / name).write_bytes((original / "models" / name).read_bytes())
    destination = tmp_path / "generated"
    finalize(tmp_path / "emitter", destination)
    for name in ("types.py", "_unions.py", "_catalog.py", "__init__.py"):
        assert (destination / name).read_bytes() == (original / name).read_bytes()
