import traceback
import sys


class AsyncTestSuite:
    """Async test cases
    Test must be asynchronous and follow the pattern `test*`.
    """

    async def run(self):
        """Run the tests an print the results."""
        print("".join(("-" * 8, type(self).__name__, "-" * 8)))
        for method_name in dir(self):
            if not method_name.startswith("test"):
                continue
            print(method_name, end="... ")
            try:
                await getattr(self, method_name)()
            except AssertionError:
                print("FAIL")
                traceback.print_exception(*sys.exc_info())
            except Exception:  # pylint: disable=broad-except
                print("ERROR")
                traceback.print_exception(*sys.exc_info())
            else:
                print("PASS")
            print()
