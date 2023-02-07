# TODO determine where this file should live.

from os import PathLike
from pathlib import Path
from azure.ai.ml.entities._resource import Resource
from azure.ai.ml.entities._assets import Data
from typing import Any, Dict, List
from azure.ai.ml._utils.utils import load_yaml
from azure.ai.ml.entities._util import load_from_dict
from azure.ai.ml._utils.utils import dump_yaml_to_file
from typing import IO, AnyStr, Dict, List, Optional, Union
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY, PARAMS_OVERRIDE_KEY

# Entity representation of a federated learning silo.
# Used by Federated Learning DSL nodes as inputs for creating
# FL subgraphs in pipelines.
# The functionality of this entity is limited, and it exists mostly
# To simplify the process of loading and validating these objects from YAML.
# TODO better/any error messaging
class FederatedLearningSilo(): # TODO should this inherit from the Resource class despite note being a true resource? abc.ABC doesn't feel appropriate either

    def __init__(
        self,
        *,
        # TODO Determine optionality - assume all fields are required for now.
        compute: str,
        datastore: str,
        inputs: List[Data],
        **kwargs,
    ):
        """
        A pseudo-entity that represents a federated learning silo, which is an isolated compute with its own
        datastore and input targets. This is meant to be used in conjunction with the 
        Federated Learning DSL node to create federated learning pipelines. This does NOT represent any specific 
        AML resource, and is instead merely meant to simply client-side experiences with managing FL data distribution.
        Standard usage involves the "load_list" classmethod to load a list of these objects from YAML, which serves
        as a necessary input for FL processes.

        
        :param compute: The resource id of a compute.
        :type compute: str
        :param datastore: The resource id of a datastore.
        :type datastore: str
        :param inputs: A list of Data entities that exist in the previously specified datastore.
        :type inputs: list[Data]
        :param kwargs: A dictionary of additional configuration parameters.
        :type kwargs: dict
        """
        self.compute = compute
        self.datastore = datastore
        self.inputs = inputs



    def dump(
        self,
        dest: Union[str, PathLike, IO[AnyStr]],
        **kwargs,  # pylint: disable=unused-argument
    ) -> None:
        """Dump the Federated Learning Silo spec into a file in yaml format.

        :param path: Path to a local file as the target, new file will be created, raises exception if the file exists.
        :type path: str
        """
        yaml_serialized = self._to_dict()
        dump_yaml_to_file(dest, yaml_serialized, default_flow_style=False)


    def _to_dict(self) -> Dict:
        # JIT import to avoid experimental warnings on unrelated calls
        from azure.ai.ml._schema.assets.federated_learning_silo import FederatedLearningSiloSchema

        # pylint: disable=no-member
        schema = FederatedLearningSiloSchema(context={BASE_PATH_CONTEXT_KEY: "./"})
        return schema.dump(self)

    @classmethod
    def _load_from_dict(
        cls,
        silo_dict: dict
    ) -> "FederatedLearningSilo":
        data_input = silo_dict.get("inputs", [])
        if type(data_input) is not list:
            data_input = [data_input]
        data_objs = [Data(**datum) for datum in data_input]
        return FederatedLearningSilo(
            compute=silo_dict["compute"],
            datastore=silo_dict["datastore"],
            inputs=data_objs
            )

    #simple load based off mltable metadata loading style
    @classmethod
    def _load(
        cls,
        yaml_path: Optional[Union[PathLike, str]] = None,
        **kwargs,
    ) -> "FederatedLearningSilo":
        yaml_dict = load_yaml(yaml_path)
        return FederatedLearningSilo._load_from_dict(silo_dict=yaml_dict)

    @classmethod
    def load_list(
        cls,
        *,
        yaml_path: Optional[Union[PathLike, str]],
        list_arg: str,
        **kwargs, 
    ) -> List["FederatedLearningSilo"]:
        """
        Loads a list of federated learning silos from YAML. This is the expected entry point
        for this class; load a list of these, then supply them to the federated learning DSL
        package node in order to produce an FL pipeline.

        The structure of the supplied YAML file is assumed to be a list of FL silos under the
        name specified by the list_arg input, as shown below.

        list_arg:
        - silo 1 ...
        - silo 2 ...

        param yaml_path: A path leading to a local YAML file which contains a list of
            FederatedLearningSilo objects.
        type yaml_path: Optional[Union[PathLike, str]]
        param list_arg: A string that names the top-level value which contains the list
            of FL silos.
        type list_arg: str
        """
        yaml_dict = load_yaml(yaml_path)
        return [FederatedLearningSilo._load_from_dict(silo_dict=silo_yaml_dict) for silo_yaml_dict in  yaml_dict[list_arg]]



    # There are no to/from rest object functions because this object has no
    # rest object equivalent. Any conversions should be done as part of the 
    # to/from rest object functions of OTHER entity objects.