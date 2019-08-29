from azure.cognitiveservices.language.luis.authoring import LUISAuthoringClient
from baseTest import *
import unittest


class EntityRolesTest(unittest.TestCase):
    @use_client
    def test_add_simple_entity_role(self, client: LUISAuthoringClient):
            entity_id = client.model.add_entity(
                global_app_id, "0.1", "simple entity")
            role_id = client.model.create_entity_role(
                global_app_id, "0.1", entity_id, "simple role")
            roles = client.model.list_entity_roles(
                global_app_id, "0.1", entity_id)
            client.model.delete_entity(global_app_id, "0.1", entity_id)
            found = False
            for r in roles:
                if(r.name == "simple role"):
                    found = True
            assert(found == True)


    @use_client
    def test_add_prebuilt_entity_role(self, client: LUISAuthoringClient):
            entities = client.model.add_prebuilt(global_app_id, "0.1", ["money"])
            entity_id = entities[0].id
            roled_id = client.model.create_prebuilt_entity_role(
                global_app_id, "0.1", entity_id, "simple role")
            roles = client.model.list_prebuilt_entity_roles(
                global_app_id, "0.1", entity_id)
            client.model.delete_prebuilt(global_app_id, "0.1", entity_id)
            found = False
            for r in roles:
                if(r.name == "simple role"):
                    found = True
            assert(found == True)


    @use_client
    def test_add_closed_list_entity_role(self, client: LUISAuthoringClient):
            entity_id = client.model.add_closed_list(
                global_app_id, "0.1", [{'canonical_form': 'tests', 'list': []}], "closed list model")
            role_id = client.model.create_closed_list_entity_role(
                global_app_id, "0.1", entity_id, "simple role")
            roles = client.model.list_closed_list_entity_roles(
                global_app_id, "0.1", entity_id)
            client.model.delete_closed_list(global_app_id, "0.1", entity_id)
            found = False
            for r in roles:
                if(r.name == "simple role"):
                    found = True
            assert(found == True)


    @use_client
    def test_add_regex_entity_role(self, client: LUISAuthoringClient):
            entity_id = client.model.create_regex_entity_model(
                global_app_id, "0.1", "a+", "regex model")
            role_id = client.model.create_regex_entity_role(
                global_app_id, "0.1", entity_id, "simple role")
            roles = client.model.list_regex_entity_roles(
                global_app_id, "0.1", entity_id)
            client.model.delete_regex_entity_model(global_app_id, "0.1", entity_id)
            found = False
            for r in roles:
                if(r.name == "simple role"):
                    found = True
            assert(found == True)


    @use_client
    def test_add_composit_entity_role(self, client: LUISAuthoringClient):
            prebuiltEntitiesAdded = client.model.add_prebuilt(
                global_app_id, "0.1", ["datetimeV2"])
            entity_id = client.model.add_composite_entity(
                global_app_id, "0.1", ["datetimeV2"], "composit model")
            roled_id = client.model.create_composite_entity_role(
                global_app_id, "0.1", entity_id, "simple role")
            roles = client.model.list_composite_entity_roles(
                global_app_id, "0.1", entity_id)
            client.model.delete_composite_entity(global_app_id, "0.1", entity_id)
            for added in prebuiltEntitiesAdded:
                client.model.delete_prebuilt(global_app_id, "0.1", added.id)
            found = False
            for r in roles:
                if(r.name == "simple role"):
                    found = True
            assert(found == True)


    @use_client
    def test_add_patternAny_entity_role(self, client: LUISAuthoringClient):
            entity_id = client.model.create_pattern_any_entity_model(
                global_app_id, "0.1", "Pattern.Any model", [])
            role_id = client.model.create_pattern_any_entity_role(
                global_app_id, "0.1", entity_id, "simple role")
            roles = client.model.list_pattern_any_entity_roles(
                global_app_id, "0.1", entity_id)
            client.model.delete_pattern_any_entity_model(
                global_app_id, "0.1", entity_id)
            found = False
            for r in roles:
                if(r.name == "simple role"):
                    found = True
            assert(found == True)


    @use_client
    def test_add_custom_prebuilt_entity_role(self, client: LUISAuthoringClient):
            entity_id = client.model.add_custom_prebuilt_entity(
                global_app_id, "0.1", "Communication", "ContactName")
            role_id = client.model.create_custom_prebuilt_entity_role(
                global_app_id, "0.1", entity_id, "simple role")
            roles = client.model.list_custom_prebuilt_entity_roles(
                global_app_id, "0.1", entity_id)
            client.model.delete_entity(global_app_id, "0.1", entity_id)
            found = False
            for r in roles:
                if(r.name == "simple role"):
                    found = True
            assert(found == True)


    @use_client
    def test_get_simple_entity_role(self, client: LUISAuthoringClient):
            entity_id = client.model.add_entity(global_app_id, "0.1", "simple entity")
            role_id = client.model.create_entity_role(
                global_app_id, "0.1", entity_id, "simple role")
            role = client.model.get_entity_role(
                global_app_id, "0.1", entity_id, role_id)
            client.model.delete_entity(global_app_id, "0.1", entity_id)
            assert("simple role" == role.name)


    @use_client
    def test_get_prebuilt_entity_role(self, client: LUISAuthoringClient):
            entity_id = (client.model.add_prebuilt(
                global_app_id, "0.1", ["money"]))[0].id
            role_id = client.model.create_prebuilt_entity_role(
                global_app_id, "0.1", entity_id, "simple role")
            role = client.model.get_prebuilt_entity_role(
                global_app_id, "0.1", entity_id, role_id)
            client.model.delete_prebuilt(global_app_id, "0.1", entity_id)
            assert("simple role" == role.name)


    @use_client
    def test_get_closed_list_entity_role(self, client: LUISAuthoringClient):
            entity_id = client.model.add_closed_list(global_app_id, "0.1",  [
                                                {'canonical_form': 'tests', 'list': []}], "closed list model")
            role_id = client.model.create_closed_list_entity_role(
                global_app_id, "0.1", entity_id, "simple role")
            role = client.model.get_closed_list_entity_role(
                global_app_id, "0.1", entity_id, role_id)
            client.model.delete_closed_list(global_app_id, "0.1", entity_id)
            assert("simple role" == role.name)


    @use_client
    def test_get_regex_entity_role(self, client: LUISAuthoringClient):
            entity_id = client.model.create_regex_entity_model(
                global_app_id, "0.1", "a+", "regex model")
            role_id = client.model.create_regex_entity_role(
                global_app_id, "0.1", entity_id, "simple role")
            role = client.model.get_regex_entity_role(
                global_app_id, "0.1", entity_id, role_id)
            client.model.delete_regex_entity_model(global_app_id, "0.1", entity_id)
            assert("simple role" == role.name)


    @use_client
    def test_get_composite_entity_role(self, client: LUISAuthoringClient):
            prebuiltEntitiesAdded = client.model.add_prebuilt(
                global_app_id, "0.1", ["datetimeV2"])
            entity_id = client.model.add_composite_entity(
                global_app_id, "0.1", ["datetimeV2"], "composite model")
            role_id = client.model.create_composite_entity_role(
                global_app_id, "0.1", entity_id, "simple role")
            role = client.model.get_composite_entity_role(
                global_app_id, "0.1", entity_id, role_id)
            client.model.delete_composite_entity(global_app_id, "0.1", entity_id)
            for added in prebuiltEntitiesAdded:
                client.model.delete_prebuilt(global_app_id, "0.1", added.id)
            assert("simple role" == role.name)


    @use_client
    def test_get_pattern_any_entity_role(self, client: LUISAuthoringClient):
            entity_id = client.model.create_pattern_any_entity_model(
                global_app_id, "0.1", "Pattern.Any model", [])
            role_id = client.model.create_pattern_any_entity_role(
                global_app_id, "0.1", entity_id, "simple role")
            role = client.model.get_pattern_any_entity_role(
                global_app_id, "0.1", entity_id, role_id)
            client.model.delete_pattern_any_entity_model(
                global_app_id, "0.1", entity_id)
            assert("simple role" == role.name)


    @use_client
    def test_get_custom_prebuilt_domain_entity_role(self, client: LUISAuthoringClient):
            entity_id = client.model.add_custom_prebuilt_entity(
                global_app_id, "0.1", "Communication", "ContactName")
            role_id = client.model.create_custom_prebuilt_entity_role(
                global_app_id, "0.1", entity_id, "simple role")
            role = client.model.get_custom_entity_role(
                global_app_id, "0.1", entity_id, role_id)
            client.model.delete_entity(global_app_id, "0.1", entity_id)
            assert("simple role" == role.name)


    @use_client
    def test_list_simple_entity_roles(self, client: LUISAuthoringClient):
            entity_id = client.model.add_entity(global_app_id, "0.1", "simple entity")
            role_id = client.model.create_entity_role(
                global_app_id, "0.1", entity_id, "simple role")
            roles = client.model.list_entity_roles(global_app_id, "0.1", entity_id)
            client.model.delete_entity(global_app_id, "0.1", entity_id)

            assert(len(roles) == 1)
            assert(roles[0].name == "simple role")


    @use_client
    def test_list_prebuilt_entity_roles(self, client: LUISAuthoringClient):
            entity_id = (client.model.add_prebuilt(
                global_app_id, "0.1", ["money"]))[0].id
            role_id = client.model.create_prebuilt_entity_role(
                global_app_id, "0.1", entity_id, "simple role")
            roles = client.model.list_prebuilt_entity_roles(
                global_app_id, "0.1", entity_id)
            client.model.delete_prebuilt(global_app_id, "0.1", entity_id)
            assert(len(roles) == 1)
            assert(roles[0].name == "simple role")


    @use_client
    def test_list_closed_list_entity_roles(self, client: LUISAuthoringClient):
            entity_id = client.model.add_closed_list(global_app_id, "0.1", [
                                                {'canonical_form': "test", 'List': []}], "closed list model")
            role_id = client.model.create_closed_list_entity_role(
                global_app_id, "0.1", entity_id, "simple role")
            roles = client.model.list_closed_list_entity_roles(
                global_app_id, "0.1", entity_id)
            client.model.delete_closed_list(global_app_id, "0.1", entity_id)
            assert(len(roles) == 1)
            assert(roles[0].name == "simple role")


    @use_client
    def test_list_regex_entity_roles(self, client: LUISAuthoringClient):
            entity_id = client.model.create_regex_entity_model(
                global_app_id, "0.1", "a+", "regex model")
            role_id = client.model.create_regex_entity_role(
                global_app_id, "0.1", entity_id, "simple role")
            roles = client.model.list_regex_entity_roles(
                global_app_id, "0.1", entity_id)
            client.model.delete_regex_entity_model(global_app_id, "0.1", entity_id)
            assert(len(roles) == 1)
            assert(roles[0].name == "simple role")


    @use_client
    def test_list_composite_entity_roles(self, client: LUISAuthoringClient):
            prebuiltEntitiesAdded = client.model.add_prebuilt(
                global_app_id, "0.1", ["datetimeV2"])
            entity_id = client.model.add_composite_entity(
                global_app_id, "0.1", ["datetimeV2"], "composite model")
            role_id = client.model.create_composite_entity_role(
                global_app_id, "0.1", entity_id, "simple role")
            roles = client.model.list_composite_entity_roles(
                global_app_id, "0.1", entity_id)
            client.model.delete_composite_entity(global_app_id, "0.1", entity_id)
            for added in prebuiltEntitiesAdded:
                client.model.delete_prebuilt(global_app_id, "0.1", added.id)
            assert(len(roles) == 1)
            assert(roles[0].name == "simple role")


    @use_client
    def test_list_pattern_any_entity_roles(self, client: LUISAuthoringClient):
            entity_id = client.model.create_pattern_any_entity_model(
                global_app_id, "0.1", "Pattern.Any model", [])
            role_id = client.model.create_pattern_any_entity_role(
                global_app_id, "0.1", entity_id, "simple role")
            roles = client.model.list_pattern_any_entity_roles(
                global_app_id, "0.1", entity_id)
            client.model.delete_pattern_any_entity_model(
                global_app_id, "0.1", entity_id)
            assert(len(roles) == 1)
            assert(roles[0].name == "simple role")


    @use_client
    def test_list_custom_prebuilt_entity_roles(self, client: LUISAuthoringClient):
            entity_id = client.model.add_custom_prebuilt_entity(
                global_app_id, "0.1", "Communication", "ContactName")
            role_id = client.model.create_custom_prebuilt_entity_role(
                global_app_id, "0.1", entity_id, "simple role")
            roles = client.model.list_custom_prebuilt_entity_roles(
                global_app_id, "0.1", entity_id)
            client.model.delete_entity(global_app_id, "0.1", entity_id)
            assert(len(roles) == 1)
            assert(roles[0].name == "simple role")


    @use_client
    def test_update_entity_role(self, client: LUISAuthoringClient):
            entity_id = client.model.add_entity(global_app_id, "0.1", "simple entity")
            role_id = client.model.create_entity_role(
                global_app_id, "0.1", entity_id, "simple role")
            client.model.update_entity_role(
                global_app_id, "0.1", entity_id, role_id, "simple role 2")
            role = client.model.get_entity_role(
                global_app_id, "0.1", entity_id, role_id)
            client.model.delete_entity(global_app_id, "0.1", entity_id)
            assert(role.name == "simple role 2")


    @use_client
    def test_update_prebuilt_entity_role(self, client: LUISAuthoringClient):
            entity_id = (client.model.add_prebuilt(
                global_app_id, "0.1",  ["money"]))[0].id
            role_id = client.model.create_prebuilt_entity_role(
                global_app_id, "0.1", entity_id, "simple role")
            client.model.update_prebuilt_entity_role(
                global_app_id, "0.1", entity_id, role_id, "simple role 2")
            role = client.model.get_prebuilt_entity_role(
                global_app_id, "0.1", entity_id, role_id)
            client.model.delete_prebuilt(global_app_id, "0.1", entity_id)
            assert(role.name == "simple role 2")


    @use_client
    def test_update_closed_list_entity_role(self, client: LUISAuthoringClient):
            entity_id = client.model.add_closed_list(global_app_id, "0.1", [
                                                {'canonical_form': "test", 'List': []}], "closed list model")
            role_id = client.model.create_closed_list_entity_role(
                global_app_id, "0.1", entity_id, "simple role")
            client.model.update_closed_list_entity_role(
                global_app_id, "0.1", entity_id, role_id, "simple role 2")
            role = client.model.get_closed_list_entity_role(
                global_app_id, "0.1", entity_id, role_id)
            client.model.delete_closed_list(global_app_id, "0.1", entity_id)
            assert(role.name == "simple role 2")


    @use_client
    def test_update_regex_entity_role(self, client: LUISAuthoringClient):
            entity_id = client.model.create_regex_entity_model(
                global_app_id, "0.1",  "a+",  "regex model")
            role_id = client.model.create_regex_entity_role(
                global_app_id, "0.1", entity_id, "simple role")
            client.model.update_regex_entity_role(
                global_app_id, "0.1", entity_id, role_id, "simple role 2")
            role = client.model.get_regex_entity_role(
                global_app_id, "0.1", entity_id, role_id)
            client.model.delete_regex_entity_model(global_app_id, "0.1", entity_id)
            assert(role.name == "simple role 2")


    @use_client
    def test_update_composite_entity_role(self, client: LUISAuthoringClient):
            prebuiltEntitiesAdded = client.model.add_prebuilt(
                global_app_id, "0.1", ["datetimeV2"])
            entity_id = client.model.add_composite_entity(
                global_app_id, "0.1", ["datetimeV2"], "composite model")
            role_id = client.model.create_composite_entity_role(
                global_app_id, "0.1", entity_id, "simple role")
            client.model.update_composite_entity_role(
                global_app_id, "0.1", entity_id, role_id, "simple role 2")
            role = client.model.get_composite_entity_role(
                global_app_id, "0.1", entity_id, role_id)
            client.model.delete_composite_entity(global_app_id, "0.1", entity_id)
            for added in prebuiltEntitiesAdded:
                client.model.delete_prebuilt(global_app_id, "0.1", added.id)
            assert(role.name == "simple role 2")


    @use_client
    def test_update_pattern_any_entity_role(self, client: LUISAuthoringClient):
            entity_id = client.model.create_pattern_any_entity_model(
                global_app_id, "0.1", "Pattern.Any model", [])
            role_id = client.model.create_pattern_any_entity_role(
                global_app_id, "0.1", entity_id, "simple role")
            client.model.update_pattern_any_entity_role(
                global_app_id, "0.1", entity_id, role_id, "simple role 2")
            role = client.model.get_pattern_any_entity_role(
                global_app_id, "0.1", entity_id, role_id)
            client.model.delete_pattern_any_entity_model(
                global_app_id, "0.1", entity_id)
            assert(role.name == "simple role 2")



    @use_client
    def test_update_custom_prebuilt_entity_role(self, client: LUISAuthoringClient):
            entity_id = client.model.add_custom_prebuilt_entity(
                global_app_id, "0.1", "Communication", "ContactName")
            role_id = client.model.create_custom_prebuilt_entity_role(
                global_app_id, "0.1", entity_id, "simple role")
            client.model.update_custom_prebuilt_entity_role(
                global_app_id, "0.1", entity_id, role_id, "simple role 2")
            role = client.model.get_custom_entity_role(
                global_app_id, "0.1", entity_id, role_id)
            client.model.delete_entity(global_app_id, "0.1", entity_id)
            assert(role.name == "simple role 2")


    @use_client
    def test_delete_simple_entity_role(self, client: LUISAuthoringClient):
            entity_id = client.model.add_entity(global_app_id, "0.1", "simple entity")
            role_id = client.model.create_entity_role(
                global_app_id, "0.1", entity_id, "simple role")
            client.model.delete_entity_role(global_app_id, "0.1", entity_id, role_id)
            roles = client.model.list_entity_roles(global_app_id, "0.1", entity_id)
            client.model.delete_entity(global_app_id, "0.1", entity_id)
            assert(len(roles) == 0)


    @use_client
    def test_delete_prebuilt_entity_role(self, client: LUISAuthoringClient):
            entity_id = (client.model.add_prebuilt(
                global_app_id, "0.1", ["money"]))[0].id
            role_id = client.model.create_prebuilt_entity_role(
                global_app_id, "0.1", entity_id, "simple role")
            client.model.delete_prebuilt_entity_role(
                global_app_id, "0.1", entity_id, role_id)
            roles = client.model.list_prebuilt_entity_roles(
                global_app_id, "0.1", entity_id)
            client.model.delete_prebuilt(global_app_id, "0.1", entity_id)
            assert(len(roles) == 0)


    @use_client
    def test_delete_closed_list_entity_role(self, client: LUISAuthoringClient):
            entity_id = client.model.add_closed_list(global_app_id, "0.1", [
                                                {'canonical_form': 'tests', 'list': []}], "closed list model")
            role_id = client.model.create_closed_list_entity_role(
                global_app_id, "0.1", entity_id, "simple role")
            client.model.delete_closed_list_entity_role(
                global_app_id, "0.1", entity_id, role_id)
            roles = client.model.list_closed_list_entity_roles(
                global_app_id, "0.1", entity_id)
            client.model.delete_closed_list(global_app_id, "0.1", entity_id)
            assert(len(roles) == 0)


    @use_client
    def test_delete_regex_entity_role(self, client: LUISAuthoringClient):
            entity_id = client.model.create_regex_entity_model(
                global_app_id, "0.1", "a+", "regex model")
            role_id = client.model.create_regex_entity_role(
                global_app_id, "0.1", entity_id, "simple role")
            client.model.delete_regex_entity_role(
                global_app_id, "0.1", entity_id, role_id)
            roles = client.model.list_regex_entity_roles(
                global_app_id, "0.1", entity_id)
            client.model.delete_regex_entity_model(global_app_id, "0.1", entity_id)
            assert(len(roles) == 0)


    @use_client
    def test_delete_composite_entity_role(self, client: LUISAuthoringClient):
            prebuiltEntitiesAdded = client.model.add_prebuilt(
                global_app_id, "0.1", ["datetimeV2"])
            entity_id = client.model.add_composite_entity(
                global_app_id, "0.1", ["datetimeV2"], "composite model")
            role_id = client.model.create_composite_entity_role(
                global_app_id, "0.1", entity_id, "simple role")
            client.model.delete_composite_entity_role(
                global_app_id, "0.1", entity_id, role_id)
            roles = client.model.list_composite_entity_roles(
                global_app_id, "0.1", entity_id)
            client.model.delete_composite_entity(global_app_id, "0.1", entity_id)
            for added in prebuiltEntitiesAdded:
                client.model.delete_prebuilt(global_app_id, "0.1", added.id)
            assert(len(roles) == 0)


    @use_client
    def test_delete_pattern_any_entity_role(self, client: LUISAuthoringClient):
            entity_id = client.model.create_pattern_any_entity_model(
                global_app_id, "0.1", "Pattern.Any model", [])
            role_id = client.model.create_pattern_any_entity_role(
                global_app_id, "0.1", entity_id, "simple role")
            client.model.delete_pattern_any_entity_role(
                global_app_id, "0.1", entity_id, role_id)
            roles = client.model.list_pattern_any_entity_roles(
                global_app_id, "0.1", entity_id)
            client.model.delete_pattern_any_entity_model(
                global_app_id, "0.1", entity_id)
            assert(len(roles) == 0)



    @use_client
    def test_delete_custom_entity_role(self, client: LUISAuthoringClient):
            entity_id = client.model.add_custom_prebuilt_entity(
                global_app_id, "0.1", "Communication", "ContactName")
            role_id = client.model.create_custom_prebuilt_entity_role(
                global_app_id, "0.1", entity_id, "simple role")
            client.model.delete_custom_entity_role(
                global_app_id, "0.1", entity_id, role_id)
            roles = client.model.list_custom_prebuilt_entity_roles(
                global_app_id, "0.1", entity_id)
            client.model.delete_entity(global_app_id, "0.1", entity_id)
            assert(len(roles) == 0)
