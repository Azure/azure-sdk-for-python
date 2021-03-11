class FarmClient():
    def __init__(
        self,
        farmbeats_client
    ):
        self.client = farmbeats_client

    def get_all(
        self,
        farmer_id=None,
        farm_ids=None,
        names=None,
        property_filters=None,
        statuses=None,
        min_created_date_time=None,
        max_created_date_time=None,
        min_last_modified_date_time=None,
        max_last_modified_date_time=None,
        # limit=1000
    ):
        if farmer_id is not None:
            return self.client.get_farms(
                farmer_id,
                farm_ids,
                names,
                property_filters,
                statuses,
                min_created_date_time,
                max_created_date_time,
                min_last_modified_date_time,
                max_last_modified_date_time,
                1000
            ).value
        else:
            return self.client.get_all_farms(
                farm_ids,
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
        farm_id,
        farm=None,
    ):
        return self.client.create_farm(
            farmer_id,
            farm_id,
            farm
        )
