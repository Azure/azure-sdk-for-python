class ComputeNodeAdministrationClient(object):
    """A Client for the AppConfiguration Service.
    
    :param str account_url: The URL for the service.
    :param AsyncTokenCredential credential: The credentials to authenticate with the service.
    """

    def __init__(self, account_url: str, credential: "AsyncTokenCredential", **kwargs):
        pass

    async def create_compute_node(self, user_name, os_choice, node_name, **kwargs):
        # type: (str, enum, str) -> ComputeNode
        """Create a compute node with the OS of your choice

        :param str user_name: The compute node's user name
        :param OSChoiceEnum os_choice: The desired OS for the ComputeNode
        :param str name: The name of the ComputeNode for easy access.
        
        :keyword str e_tag: 
        """
        pass
    
    async def begin_calculate_pi(self, node_name, decimals, **kwargs):
        # type: (str, int) -> LROPoller
        """Trigger a pi 

        :param str user_name: The compute node's user name
        :param OSChoiceEnum os_choice: The desired OS for the ComputeNode
        :param str name: The name of the ComputeNode for easy access.
        
        :keyword str e_tag: 

        :raises ~azure.core.exceptions.HttpResponseError: If there was an error triggering this operation
        """
        pass