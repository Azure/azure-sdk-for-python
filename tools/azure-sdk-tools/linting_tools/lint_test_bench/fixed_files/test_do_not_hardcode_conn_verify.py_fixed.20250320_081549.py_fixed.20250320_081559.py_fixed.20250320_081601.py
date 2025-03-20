class FunctionKeywordArgumentsErrors:
    def create(self, x, connection_verify):
        if connection_verify:
            return x + 1
        return x

    def run(self, connection_verify=False):
        client = self.create(x=0, connection_verify=connection_verify)
        return client
