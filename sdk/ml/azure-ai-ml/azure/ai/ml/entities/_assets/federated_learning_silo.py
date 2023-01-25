# TODO determine where this file should live.

from azure.ai.ml.entities._resource import Resource


# Entity representation of a federated learning silo.
# Used by Federated Learning DSL nodes as inputs for creating
# FL subgraphs in pipelines.
# The functionality of this entity is limited, and it exists mostly
# To simplify the process of loading and validating these objects from YAML.
class FederatedLearningSilo(Resource):

    def __init__(
        self,
        # TODO determine inputs
        **kwargs,
    ):
        pass

    def validate(self):
        pass