# tests/test_smoke.py
"""
Ultra-minimal smoke test to ensure the package imports so CI doesn't fail with
'no tests collected' (exit code 5). Extend with real tests as the API stabilizes.
"""

def test_can_import_package():
    import azure.ai.voicelive as sdk  # noqa: F401
    assert sdk is not None