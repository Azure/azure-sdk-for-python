from azure.mgmt.reservations import AzureReservationAPI
from azure.mgmt.reservations.models import Patch, SplitRequest, MergeRequest
from devtools_testutils import AzureMgmtTestCase
import unittest

class MgmtReservationsTest(AzureMgmtTestCase):

    def _validate_reservation_order(self, reservation_order):
        self.assertIsNotNone(reservation_order)
        self.assertIsNotNone(reservation_order.etag)
        self.assertIsNotNone(reservation_order.id)
        self.assertIsNotNone(reservation_order.name)
        self.assertIsNotNone(reservation_order.type)

    def _validate_reservation(self, reservation):
        self.assertIsNotNone(reservation)
        self.assertIsNotNone(reservation.id)
        self.assertIsNotNone(reservation.name)
        self.assertIsNotNone(reservation.sku)
        self.assertIsNotNone(reservation.type)

    def setUp(self):
        super(MgmtReservationsTest, self).setUp()
        self.reservation_client = self.create_basic_client(AzureReservationAPI)
        self.reservation_order_id = "86d9870a-bf1e-4635-94c8-b0f08932bc3a"
        self.reservation_id = "97830c1b-372b-4787-8b86-a54eb55be675"
        self.subscription_id = "917b6752-3ac4-4087-84d7-b587adcca91b"

    def test_reservation_order_get(self):
        reservation_order = self.reservation_client.reservation_order.get(self.reservation_order_id)
        self.assertIsNotNone(reservation_order)
        self._validate_reservation_order(reservation_order)

    def test_reservation_order_list(self):
        reservation_order_list = self.reservation_client.reservation_order.list()
        self.assertIsNotNone(reservation_order_list)
        self.assertTrue(len(reservation_order_list._attribute_map['current_page']) > 0)
        for reservation_order in reservation_order_list:
            self._validate_reservation_order(reservation_order)

    def test_reservation_history_list(self):
        reservation_history = self.reservation_client.reservation.list_revisions(self.reservation_id, self.reservation_order_id)
        for reservation in reservation_history:
            self._validate_reservation(reservation)

    def test_reservation_get(self):
        reservation = self.reservation_client.reservation.get(self.reservation_id, self.reservation_order_id)
        self._validate_reservation(reservation)


    def test_reservation_list(self):
        reservation_list = self.reservation_client.reservation.list(self.reservation_order_id)
        for reservation in reservation_list:
            self._validate_reservation(reservation)


    def test_merge_reservations(self):
        reservation = self.reservation_client.reservation.merge()

    def test_split_reservation(self):
        reservation = self.reservation_client.reservation.split()

    def test_update_reservation_to_single(self):
        patch = Patch("Single", ["/subscriptions/{}".format(self.subscription_id)])
        reservation = self.reservation_client.reservation.update(self.reservation_order_id, self.reservation_id, patch).result()
        self._validate_reservation(reservation)

    def test_update_reservation_to_shared(self):
        patch = Patch("Shared")
        reservation = self.reservation_client.reservation.update(self.reservation_order_id, self.reservation_id, patch).result()
        self._validate_reservation(reservation)

    def test_register_capacity(self):
        provider = self.reservation_client.register_subscription(self.subscription_id)
        expected_id = "/subscriptions/{}/providers/Microsoft.Capacity".format(self.subscription_id)
        self.assertEqual(expected_id, provider.id)
        expected_namespace = "Microsoft.Capacity"
        self.assertEqual(expected_namespace, provider.namespace)
        self.assertIsNotNone(provider.authorization)
        self.assertTrue(len(provider.resource_types) > 0)
        self.assertEqual("Registered", provider.registration_state)

    def test_get_catalog(self):
        catalog_items = self.reservation_client.get_catalog(self.subscription_id)
        for item in catalog_items:
            self.assertIsNotNone(item.resource_type)
            self.assertIsNotNone(item.name)
            self.assertIsNotNone(item.tier)
            self.assertIsNotNone(item.size)
            self.assertTrue(len(item.terms) > 0)
            self.assertTrue(len(item.locations) > 0)

    def test_applied_reservation(self):
        applied_reservation = self.reservation_client.get_applied_reservation_list(self.subscription_id)
        expected_id = "/subscriptions/{}/providers/microsoft.capacity/AppliedReservations/default".format(self.subscription_id)
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

    def test_split(self):
        reservation_id = "/providers/Microsoft.Capacity/reservationOrders/{}/reservations/{}".format(self.reservation_order_id, self.reservation_id)
        split_body = SplitRequest([2, 3], reservation_id)
        split_response = self.reservation_client.reservation.split(self.reservation_order_id, split_body).result()

        split_quantity = 0
        for reservation in split_response:
            self._validate_reservation(reservation)
            if "Succeeded" in reservation.properties.provisioning_state:
                split_quantity += reservation.properties.quantity
        self.assertTrue(split_quantity == 5)

    def test_merge(self):
        split_id1 = "36beb8e4-db5f-4502-ae42-630e464a5437"
        split_id2 = "7f08f1bc-0f4a-4bb7-9d50-d1d8d656179b"
        merge_id1 = "/providers/Microsoft.Capacity/reservationOrders/{}/reservations/{}".format(self.reservation_order_id, split_id1)
        merge_id2 = "/providers/Microsoft.Capacity/reservationOrders/{}/reservations/{}".format(self.reservation_order_id, split_id2)
        merge_body = MergeRequest([merge_id1, merge_id2])
        merge_response = self.reservation_client.reservation.merge(self.reservation_order_id, merge_body).result()
        response = self.reservation_client.reservation_order.get(self.reservation_order_id)
        
        merge_quantity = 0
        for reservation in merge_response:
            self._validate_reservation(reservation)
            if "Succeeded" in reservation.properties.provisioning_state:
                merge_quantity += reservation.properties.quantity
        self.assertTrue(merge_quantity == 5)


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
