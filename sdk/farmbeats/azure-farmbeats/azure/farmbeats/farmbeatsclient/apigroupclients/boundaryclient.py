class BoundaryClient():
    def __init__(
        self,
        farmbeats_client
    ):
        self.client = farmbeats_client

    def create(
        self,
        farmer_id,
        boundary_id,
        boundary
    ):
        return self.client.create_boundary(
            farmer_id,
            boundary_id,
            boundary,
        )

    def get_all(
        self,
        farmer_id=None,
        is_primary=None,
        parent_type=None,
        parent_ids=None,
        min_acreage=None,
        max_acreage=None,
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
        if farmer_id is not None:
            return self.client.get_boundaries(
                farmer_id,
                is_primary,
                parent_type,
                parent_ids,
                min_acreage,
                max_acreage,
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
            return self.client.get_all_boundaries(
                is_primary,
                parent_type,
                parent_ids,
                min_acreage,
                max_acreage,
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
