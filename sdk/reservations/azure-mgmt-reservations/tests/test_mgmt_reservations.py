from azure.mgmt.reservations import AzureReservationAPI
from azure.mgmt.reservations.models import *
from devtools_testutils import AzureMgmtTestCase
from azure.mgmt.reservations.models import (
    ReservedResourceType,
    InstanceFlexibility,
    AppliedScopeType
)
from datetime import (
    datetime,
    timedelta,
    tzinfo
)
import unittest

# change the custom endpoint to set the environment
_CUSTOM_ENDPOINT = "https://management.azure.com/"

ZERO = timedelta(0)

class UTC(tzinfo):
  def utcoffset(self, dt):
    return ZERO
  def tzname(self, dt):
    return "UTC"
  def dst(self, dt):
    return ZERO

class MgmtReservationsTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtReservationsTest, self).setUp()
        # self._register_equality_checkers()
        self.reservation_client = self.create_basic_client(AzureReservationAPI, base_url=_CUSTOM_ENDPOINT)
        # self.reservation_client = self.create_basic_client(AzureReservationAPI)

    def _register_equality_checkers(self):
        self.addTypeEqualityFunc(AutoQuotaIncreaseDetail, self._test_aqi_details_equality)
        self.addTypeEqualityFunc(Actions, self._test_actions_equality)
        self.addTypeEqualityFunc(EmailActions, self._test_email_actions_equality)
        self.addTypeEqualityFunc(EmailAction, self._test_email_action_equality)
        self.addTypeEqualityFunc(SupportRequestAction, self._test_support_action_equality)
        self.addTypeEqualityFunc(AqiSettings, self._test_aqi_settings_equality)

    def _test_actions_equality(self, expected, actual, msg=None):
        self.assertEqual(
            expected.email_actions,
            actual.email_actions,
            msg
        )

    def _test_email_actions_equality(self, expected, actual, msg=None):
        self.assertEqual(
            expected.email_addresses,
            actual.email_addresses,
            msg
        )

    def _test_email_action_equality(self, expected, actual, msg=None):
        self.assertEqual(
            expected.email_address,
            actual.email_address,
            msg
        )

    def _test_support_action_equality(self, expected, actual, msg=None):
        self.assertEqual(
            expected.alternate_email_addresses,
            actual.alternate_email_addresses,
            msg
        )
        self.assertEqual(
            expected.severity,
            actual.severity,
            msg
        )
        self.assertEqual(
            expected.first_name,
            actual.first_name,
            msg
        )
        self.assertEqual(
            expected.last_name,
            actual.last_name,
            msg
        )
        self.assertEqual(
            expected.country,
            actual.country,
            msg
        )
        self.assertEqual(
            expected.phone_number,
            actual.phone_number,
            msg
        )
        self.assertEqual(
            expected.primary_email_address,
            actual.primary_email_address,
            msg
        )
        self.assertEqual(
            expected.support_language,
            actual.support_language,
            msg
        )
        self.assertEqual(
            expected.preferred_contact_method,
            actual.preferred_contact_method,
            msg
        )

    def _test_aqi_settings_equality(self, expected, actual, msg=None):
        self.assertEqual(
            expected.auto_quota_increase_state,
            actual.auto_quota_increase_state,
            msg)

    def _test_aqi_details_equality(self, expected, actual, msg=None):
        self.assertEqual(
            expected.settings,
            actual.settings,
            msg)
        self.assertEqual(
            expected.on_failure,
            actual.on_failure,
            msg
        )
        self.assertEqual(
            expected.on_success,
            actual.on_success,
            msg
        )
        self.assertEqual(
            expected.support_ticket_action,
            actual.support_ticket_action,
            msg
        )
        
    def _validate_reservation_order(self, reservation_order):
        self.assertIsNotNone(reservation_order)
        self.assertIsNotNone(reservation_order.id)
        self.assertIsNotNone(reservation_order.name)
        self.assertIsNotNone(reservation_order.type)

    def _validate_reservation(self, reservation):
        self.assertIsNotNone(reservation)
        self.assertIsNotNone(reservation.id)
        self.assertIsNotNone(reservation.name)
        self.assertIsNotNone(reservation.sku)
        self.assertIsNotNone(reservation.type)
        self.assertIsNotNone(reservation.properties)
        self.assertIsNotNone(reservation.properties.applied_scope_type)
        self.assertIsNotNone(reservation.properties.quantity)
        self.assertIsNotNone(reservation.properties.provisioning_state)
        self.assertIsNotNone(reservation.properties.display_name)
        self.assertIsNotNone(reservation.properties.effective_date_time)
        self.assertIsNotNone(reservation.properties.last_updated_date_time)
        self.assertIsNotNone(reservation.properties.reserved_resource_type)
        self.assertIsNotNone(reservation.properties.instance_flexibility)
        self.assertIsNotNone(reservation.properties.sku_description)

    def _create_purchase_request(self):
        return PurchaseRequest(
            sku=SkuName(name="Standard_F1"),
            location="eastus",
            reserved_resource_type="VirtualMachines",
            billing_scope_id="/subscriptions/{}".format(self.settings.SUBSCRIPTION_ID),
            term="P1Y",
            quantity=2,
            display_name="TestPythonPurchase",
            applied_scope_type="Single",
            applied_scopes=["/subscriptions/{}".format(self.settings.SUBSCRIPTION_ID)],
            reserved_resource_properties=PurchaseRequestPropertiesReservedResourceProperties(instance_flexibility="On"))

    def _calculate_reservation_order(self):
        purchase_request = self._create_purchase_request()
        calculate_response = self.reservation_client.reservation_order.calculate(purchase_request)
        return calculate_response.properties.reservation_order_id

    def _purchase_reservation_order(self, reservation_order_id):
        purchase_request = self._create_purchase_request()
        self.reservation_client.reservation_order.purchase(reservation_order_id, purchase_request).result()

    def _test_reservation_order_get(self, reservation_order_id):
        reservation_order = self.reservation_client.reservation_order.get(reservation_order_id)
        self.assertIsNotNone(reservation_order)
        self._validate_reservation_order(reservation_order)

        return reservation_order

    def _test_reservation_get(self, reservation_order_id, reservation_id):
        reservation = self.reservation_client.reservation.get(reservation_id, reservation_order_id)
        self._validate_reservation(reservation)

    def _test_update_reservation_to_shared(self, reservation_order_id, reservation_id):
        patch = Patch(applied_scope_type=AppliedScopeType.shared, applied_scopes=None, instance_flexibility=InstanceFlexibility.on)
        reservation = self.reservation_client.reservation.update(reservation_order_id, reservation_id, patch).result()
        self._validate_reservation(reservation)

    def _test_update_reservation_to_single(self, reservation_order_id, reservation_id):
        scope = ["/subscriptions/{}".format(self.settings.SUBSCRIPTION_ID)]
        patch = Patch(applied_scope_type=AppliedScopeType.single, applied_scopes=scope, instance_flexibility=InstanceFlexibility.on)
        reservation = self.reservation_client.reservation.update(reservation_order_id, reservation_id, patch).result()
        self._validate_reservation(reservation)

    def _test_split(self, reservation_order_id, reservation_id):
        reservation_list = self.reservation_client.reservation.list(reservation_order_id)
        for reservation in reservation_list:
            if "Succeeded" in reservation.properties.provisioning_state:
                reservation_to_update = reservation
        split_reservation_id = reservation_to_update.id.split('/')[6]
        reservation_id = "/providers/Microsoft.Capacity/reservationOrders/{}/reservations/{}".format(reservation_order_id, split_reservation_id)
        split_response = self.reservation_client.reservation.split(reservation_order_id, [1, 1], reservation_id).result()

        split_quantity = 0
        for reservation in split_response:
            self._validate_reservation(reservation)
            if "Succeeded" in reservation.properties.provisioning_state:
                split_quantity += reservation.properties.quantity
        self.assertTrue(split_quantity == 2)

    def _test_merge(self, reservation_order_id):
        reservation_list = self.reservation_client.reservation.list(reservation_order_id)
        split_id1 = None
        split_id2 = None
        for reservation in reservation_list:
            if "Succeeded" in reservation.properties.provisioning_state:
                if split_id1 is None:
                    split_id1 = reservation.id.split('/')[6]
                else:
                    split_id2 = reservation.id.split('/')[6]
        merge_id1 = "/providers/Microsoft.Capacity/reservationOrders/{}/reservations/{}".format(reservation_order_id, split_id1)
        merge_id2 = "/providers/Microsoft.Capacity/reservationOrders/{}/reservations/{}".format(reservation_order_id, split_id2)
        merge_response = self.reservation_client.reservation.merge(reservation_order_id, [merge_id1, merge_id2]).result()
        
        merge_quantity = 0
        for reservation in merge_response:
            self._validate_reservation(reservation)
            if "Succeeded" in reservation.properties.provisioning_state:
                merge_quantity += reservation.properties.quantity
        self.assertTrue(merge_quantity == 2)

    def _test_reservation_history_list(self, reservation_order_id, reservation_id):
        reservation_history = self.reservation_client.reservation.list_revisions(reservation_id, reservation_order_id)
        for reservation in reservation_history:
            self._validate_reservation(reservation)

    def _test_reservation_list(self, reservation_order_id):
        reservation_list = self.reservation_client.reservation.list(reservation_order_id)
        for reservation in reservation_list:
            self._validate_reservation(reservation)

    def _create_auto_quota_increase_details(self, enabled):
        if (enabled):
            return AutoQuotaIncreaseDetail(
                settings = AqiSettings(auto_quota_increase_state = "Enabled"),
                on_failure = Actions(
                    email_actions = EmailActions(
                        email_addresses = [
                            EmailAction(
                                email_address = "failure@contoso.com"
                            ),
                            EmailAction(
                                email_address = "failure1@contoso.com"
                            )
                        ]
                    )
                ),
                on_success = Actions(
                    email_actions = EmailActions(
                        email_addresses = [
                            EmailAction(
                                email_address = "success@contoso.com"
                            ),
                            EmailAction(
                                email_address = "success1@contoso.com"
                            )
                        ]
                    )
                ),
                support_ticket_action = SupportRequestAction(
                    severity = "Minimal",
                    first_name = "Jane",
                    last_name = "Doe",
                    country = "United States",
                    phone_number = "+1 555-555-5555",
                    primary_email_address = "primary@contoso.com",
                    support_language = "en-US",
                    preferred_contact_method = "Email",
                    alternate_email_addresses = [
                        "support1@contoso.com",
                        "support2@contoso.com"
                    ]
                )
            )
        else:
            return AutoQuotaIncreaseDetail(
                settings = AqiSettings(auto_quota_increase_state = "Disabled")
            )

    def _test_auto_quota_increase_create(self, enabled):
        aqi_details = self._create_auto_quota_increase_details(enabled)
        create_response = self.reservation_client.auto_quota_increase.create(
            self.settings.SUBSCRIPTION_ID,
            aqi_details
        )
        self.assertEqual(aqi_details, create_response)
        # Now validate that we can get back the same results as well
        get_response = \
            self.reservation_client.auto_quota_increase.get_properties(
                self.settings.SUBSCRIPTION_ID
            )
        self.assertEqual(aqi_details, get_response)

    @unittest.skip("skip")
    def test_reservation_operations(self):
        reservation_order_id = self._calculate_reservation_order()
        self._purchase_reservation_order(reservation_order_id)

        reservation_order = self._test_reservation_order_get(reservation_order_id)
        reservation_id = reservation_order.reservations[0].id.split("reservations/")[1]
        self._test_reservation_get(reservation_order_id, reservation_id)

        self._test_update_reservation_to_shared(reservation_order_id, reservation_id)
        self._test_update_reservation_to_single(reservation_order_id, reservation_id)

        self._test_split(reservation_order_id, reservation_id)
        self._test_merge(reservation_order_id)

        self._test_reservation_history_list(reservation_order_id, reservation_id)
        self._test_reservation_list(reservation_order_id)

    @unittest.skip("skip")
    def test_reservation_order_list(self):
        reservation_order_list = self.reservation_client.reservation_order.list()
        self.assertIsNotNone(reservation_order_list)
        self.assertTrue(len(reservation_order_list._attribute_map['current_page']) > 0)
        for reservation_order in reservation_order_list:
            self._validate_reservation_order(reservation_order)

    def test_get_catalog(self):
        catalog_items = self.reservation_client.get_catalog(self.settings.SUBSCRIPTION_ID, ReservedResourceType.virtual_machines, "westus")
        for item in catalog_items:
            self.assertIsNotNone(item.resource_type)
            self.assertIsNotNone(item.name)
            self.assertTrue(len(item.terms) > 0)
            self.assertTrue(len(item.locations) > 0)
            self.assertTrue(len(item.sku_properties) > 0)
        catalog_items = self.reservation_client.get_catalog(self.settings.SUBSCRIPTION_ID, ReservedResourceType.sql_databases, "southeastasia")
        for item in catalog_items:
            self.assertIsNotNone(item.resource_type)
            self.assertIsNotNone(item.name)
            self.assertTrue(len(item.terms) > 0)
            self.assertTrue(len(item.locations) > 0)
            self.assertTrue(len(item.sku_properties) > 0)
        catalog_items = self.reservation_client.get_catalog(self.settings.SUBSCRIPTION_ID, ReservedResourceType.suse_linux)
        for item in catalog_items:
            self.assertIsNotNone(item.resource_type)
            self.assertIsNotNone(item.name)
            self.assertTrue(len(item.terms) > 0)
            self.assertTrue(len(item.sku_properties) > 0)

    @unittest.skip("skip")
    def test_applied_reservation(self):
        applied_reservation = self.reservation_client.get_applied_reservation_list(self.settings.SUBSCRIPTION_ID)
        expected_id = "/subscriptions/{}/providers/microsoft.capacity/AppliedReservations/default".format(self.settings.SUBSCRIPTION_ID)
        self.assertEqual(expected_id, applied_reservation.id)
        self.assertEqual("default", applied_reservation.name)
        self.assertEqual("Microsoft.Capacity/AppliedReservations", applied_reservation.type)
        for order_id in applied_reservation.reservation_order_ids.value:
            self.assertIn("/providers/Microsoft.Capacity/reservationorders/", order_id)

    def test_get_operation(self):
        operations = self.reservation_client.operation.list()
        for operation in operations:
            self.assertIsNotNone(operation.name)
            self.assertIsNotNone(operation.display)

    @unittest.skip("skip")
    def test_auto_quota_increase_enabled(self):
        self._test_auto_quota_increase_create(True)

    @unittest.skip("skip")
    def test_auto_quota_increase_disabled(self):
        self._test_auto_quota_increase_create(False)

    def _test_list_quota(
        self,
        resource_provider,
        location,
        sku,
        resource_type):
        quota = self.reservation_client.quota.list(
            self.settings.SUBSCRIPTION_ID,
            resource_provider,
            location
        )
        for quota_page in quota:
            if sku is None:
                self.assertGreater(quota_page.properties.limit, 0)
                return quota_page
            if (sku is None or (quota_page.properties.name.value == sku
                and quota_page.properties.resource_type == resource_type)
                ):
                self.assertGreater(quota_page.properties.limit, 0)
                return quota_page
        self.fail("Did not find specified sku: {sku}".format(sku = sku))

    def _test_update_quota(
        self,
        resource_provider,
        location,
        sku,
        resource_type):
        current_quota = self._test_list_quota(
            resource_provider,
            location,
            sku,
            resource_type
        )
        current_quota.properties.limit += 1
        new_quota = self.reservation_client.quota.update(
            self.settings.SUBSCRIPTION_ID,
            resource_provider,
            location,
            sku,
            current_quota.properties
        ).result()
        self.assertEqual(current_quota.properties.limit, new_quota['properties']['limit'])

    def test_list_quota_compute(self):
        self._test_list_quota(
            "Microsoft.Compute",
            "WestUS",
            "standardDv2Family",
            None
        )

    def test_list_quota_batch_ai(self):
        self._test_list_quota(
            "Microsoft.MachineLearningServices",
            "WestUS",
            "standardDv2Family",
            "dedicated"
        )

    @unittest.skip("skip")
    def test_update_quota_compute(self):
        val = self._test_update_quota(
            "Microsoft.Compute",
            "WestUS",
            "standardDv2Family",
            None
        )

    def test_update_quota_batch_ai(self):
        val = self._test_update_quota(
            "Microsoft.MachineLearningServices",
            "westus",
            "standardDv2Family",
            "dedicated"
        )

    def _test_list_quota_request_status(self, provider_id, location):
        utc = UTC()
        last_year = datetime.now(utc)
        last_year = last_year.replace(year = last_year.year - 1)
        statuses = self.reservation_client.quota_request_status.list(
             self.settings.SUBSCRIPTION_ID,
             provider_id,
             location
        )
        fail = True
        for status in statuses:
            fail = False
            self.assertTrue(
                status.name.startswith(self.settings.SUBSCRIPTION_ID)
            )
            self.assertIsNotNone(status.provisioning_state)
            self.assertGreaterEqual(
                status.request_submit_time,
                last_year
            )
            self.assertEqual("Microsoft.Capacity/serviceLimitsRequests", status.type)
        if fail:
            self.fail("Did not retrieve any statuses.")

    @unittest.skip("skip")
    def test_list_quota_request_status_compute(self):
        statuses = self._test_list_quota_request_status(
            "Microsoft.Compute",
            "WestUS"
        )

    @unittest.skip("skip")
    def test_list_quota_request_status_batch_ai(self):
        statuses = self._test_list_quota_request_status(
            "Microsoft.MachineLearningServices",
            "westus"
        )
#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
