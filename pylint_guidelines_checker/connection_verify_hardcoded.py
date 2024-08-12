from pylint.checkers import BaseChecker
from pylint.interfaces import IAstroidChecker

class ConnectionVerifyHardcodedChecker(BaseChecker):
    __implements__ = IAstroidChecker

    name = 'connection_verify_hardcoded'
    priority = -1
    msgs = {
        'C9999': (
            'Avoid hardcoding connection_verify to a boolean value',
            'connection-verify-hardcoded',
            'Ensure connection_verify is not hardcoded to a boolean value',
        ),
    }
    options = ()

    def visit_assign(self, node):
        if isinstance(node.targets[0], astroid.AssignName) and node.targets[0].name == 'connection_verify':
            if isinstance(node.value, astroid.Const) and isinstance(node.value.value, bool):
                self.add_message('connection-verify-hardcoded', node=node)

def register(linter):
    linter.register_checker(ConnectionVerifyHardcodedChecker(linter))
