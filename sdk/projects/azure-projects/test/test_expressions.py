import pytest
from azure.projects._bicep import expressions as exp


def test_expression():
    e = exp.Expression("foo")
    e2 = exp.Expression("foo")
    e3 = exp.Expression("bar")
    e4 = exp.Expression(e)

    assert str(e) == "foo"
    assert repr(e) == "foo"
    assert e.value == "foo"
    assert e4.value == "foo"
    l = [e]
    assert e in l
    d = {e: e2}
    assert e in d
    assert e == e2
    assert e != e3
    assert str(e4) == "foo"
    assert repr(e4) == "foo"
    assert e == e4
    assert e.format() == "${foo}"
    assert e.format("https://{}.com") == "https://${foo}.com"


def test_expression_subscription():
    sub = exp.Subscription()
    assert sub.value == "subscription()"
    assert sub.subscription_id.value == "subscription().subscriptionId"
    assert repr(sub) == "subscription(<default>)"

    sub = exp.Subscription("foobar")
    assert sub.value == "subscription('foobar')"
    assert sub.subscription_id.value == "subscription('foobar').subscriptionId"
    assert repr(sub) == "subscription(foobar)"


def test_expression_resourcesymbol():
    symbol = exp.ResourceSymbol("foo")
    assert repr(symbol) == "resource(foo)"
    assert symbol.value == "foo"
    assert symbol.name.value == "foo.name"
    assert symbol.id.value == "foo.id"
    with pytest.raises(ValueError):
        symbol.principal_id

    symbol = exp.ResourceSymbol("foo", principal_id=True)
    assert repr(symbol) == "resource(foo)"
    assert symbol.value == "foo"
    assert symbol.name.value == "foo.name"
    assert symbol.id.value == "foo.id"
    assert symbol.principal_id.value == "foo.properties.principalId"


def test_expression_parameter():
    param = exp.Parameter("test")
    assert param.name == "test"
    assert param.default == exp.Default.MISSING
    assert param.type == "string"
    assert param.value == "test"
    assert repr(param) == "parameter(test)"
    assert param.__bicep__() == "param test string\n\n"
    assert param.__obj__() == {}

    param = exp.Parameter("test", default="foo")
    assert param.default == "foo"
    assert param.__bicep__() == "param test string = 'foo'\n\n"

    param = exp.Parameter("test", description="test param")
    assert param.__bicep__() == "@sys.description('test param')\nparam test string\n\n"

    param = exp.Parameter("test", secure=True)
    assert param.__bicep__() == "@sys.secure()\nparam test string\n\n"

    param = exp.Parameter("test", allowed=["foo", "bar"])
    assert param.__bicep__() == "@sys.allowed([\n  'foo'\n  'bar'\n])\nparam test string\n\n"

    param = exp.Parameter("test", max_length=10, min_length=1)
    assert param.__bicep__() == "@sys.maxLength(10)\n@sys.minLength(1)\nparam test string\n\n"

    param = exp.Parameter("test", type="int", min_value=1, max_value=100)
    assert param.__bicep__() == "@sys.maxValue(100)\n@sys.minValue(1)\nparam test int\n\n"

    param = exp.Parameter("test", env_var="TEST_ENV_NAME")
    assert param.__obj__() == {"test": {"value": "${TEST_ENV_NAME}"}}

    param = exp.Parameter("test", env_var="TEST_ENV_NAME", default="foo")
    assert param.__obj__() == {"test": {"value": "${TEST_ENV_NAME}"}}
