class ComputeNodeAdministrationClient(object):
    """A Client for the Example Service.
    
    :param TokenCredential credential: The credentials to authenticate with the service.
    :param str node_name: The name of the node to create.
    """

    def __init__(self, credential, **kwargs):
        # type: (TokenCredential, str) -> None
        pass

    def create_compute_node(self, user_name, os_choice, node_name, **kwargs):
        # type: (str, enum, str) -> ComputeNode
        """Create a compute node with the OS of your choice

        :param str user_name: The compute node's user name
        :param OSChoiceEnum os_choice: The desired OS for the ComputeNode
        :param str name: The name of the ComputeNode for easy access.
        
        :keyword str e_tag: 
        """
        pass
    
    def begin_calculate_pi(self, node_name, decimals, **kwargs):
        # type: (str, int) -> LROPoller
        """Trigger a pi 

        :param str user_name: The compute node's user name
        :param OSChoiceEnum os_choice: The desired OS for the ComputeNode
        :param str name: The name of the ComputeNode for easy access.
        
        :keyword str e_tag: 

        :raises ~azure.core.exceptions.HttpResponseError: If there was an error triggering this operation
        """
        pass