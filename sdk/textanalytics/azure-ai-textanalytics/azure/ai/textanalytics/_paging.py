from azure.core.paging import ItemPaged
from azure.core.async_paging import AsyncItemPaged

class HealthcareItemPaged(ItemPaged):
    def __init__(self, model_version, statistics, *args, **kwargs):
        super(HealthcareItemPaged, self).__init__(*args, **kwargs)

        self.model_version = model_version
        self.statistics = statistics


class HealthcareItemPagedAsync(AsyncItemPaged):
    def __init__(self, model_version, statistics, *args, **kwargs):
        super(HealthcareItemPagedAsync, self).__init__(*args, **kwargs)

        self.model_version = model_version
        self.statistics = statistics