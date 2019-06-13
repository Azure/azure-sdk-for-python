import os
from jinja2 import Environment, FileSystemLoader

if __name__ == "__main__":
    path = os.path.dirname(os.path.realpath(__file__))
    loader = FileSystemLoader(path+'/templates/')
    env = Environment(loader=loader)
    template = env.get_template('test_authentication.pyt')
    target = path+'/tests/test_authentication.py'
    if os.path.exists(target):
        os.remove(target)
    f = open(target,'x')
    f.write(template.render())
    f.close()
    target = path+'/tests/azure_core_asynctests/test_authentication_async.py'
    if os.path.exists(target):
        os.remove(target)
    f = open(target,'x')
    f.write(template.render(_async_prefix='Async', _asyncpytest='@pytest.mark.asyncio', _async='async ', _await='await '))
    #f.write(template.render(_async_prefix='', _asyncpytest='', _async='', _await=''))
    f.close()
