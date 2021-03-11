class FieldClient():
    def __init__(
        self,
        farmbeats_client
    ):
        self.client = farmbeats_client

    def get_all(
        self,
        farmer_id,
        farm_ids,
        ids,
        names,
        property_filters,
        statuses,
        min_created_date_time,
        max_created_date_time,
        min_last_modified_date_time,
        max_last_modified_date_time,
        # limit=1000
    ):
        if farmer_id is not None:
            return self.client.get_fields(
                farmer_id,
                farm_ids,
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
        else:
            return self.client.get_all_fields(
                farm_ids,
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
        field_id,
        field=None,
    ):
        return self.client.create_field(
            farmer_id,
            field_id,
            field,
        )
