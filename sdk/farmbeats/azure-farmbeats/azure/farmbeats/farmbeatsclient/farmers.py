class FarmerClient():
    def __init__(
        self,
        farmbeats_client
    ):
        self.client = farmbeats_client

    def get_all(
        self,
        ids=None,
        names=None,
        property_filters=None,
        statuses=None,
        min_created_date_time=None,
        max_created_date_time=None,
        min_last_modified_date_time=None,
        max_last_modified_date_time=None,
        # limit=1000
    ):
        return self.client.get_farmers(
            ids,
            names,
            property_filters,
            statuses,
            min_created_date_time,
            max_created_date_time,
            min_last_modified_date_time,
            max_last_modified_date_time,
            1000
        ).value

    def create(
        self,
        farmer_id,
        farmer=None,
    ):
        return self.client.create_farmer(
            farmer_id,
            farmer
        )

    
