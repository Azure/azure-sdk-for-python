from unittest import mock

from azure.projects import export, provision, Parameter
from azure.projects.resources.storage import StorageAccount
from azure.projects.resources.resourcegroup import ResourceGroup
from azure.projects.resources.managedidentity import UserAssignedIdentity
from azure.projects.resources.ai import AIServices
from azure.projects.resources.ai.deployment import AIDeployment, AIChat, AIEmbeddings




# def test_export_resource(export_dir):
    
#     test_param = Parameter('TestAccessTier', varname='STORAGE_ACCESS_TIER', default="Hot")
#     rg = ResourceGroup.reference(name='antisch-cmtest')
#     ua = UserAssignedIdentity.reference(name='uatest', resource_group='foo')
#     r = StorageAccount(user_role='Storage Blob Data Owner', access_tier=test_param)
#     export(
#         rg, ua, r,
#         config={'TestAccessTier': 'Cold'},
#         name="test",
#         output_dir=export_dir,
#     )

