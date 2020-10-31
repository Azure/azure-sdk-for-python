from azure.core.paging import ItemPaged
from azure.core.async_paging import AsyncItemPaged

class AnalyzeHealthcareResult(ItemPaged):
    def __init__(self, model_version, statistics, *args, **kwargs):
        super(AnalyzeHealthcareResult, self).__init__(*args, **kwargs)

        self.model_version = model_version
        self.statistics = statistics


class AnalyzeHealthcareResultAsync(AsyncItemPaged):
    def __init__(self, model_version, statistics, *args, **kwargs):
        super(AnalyzeHealthcareResultAsync, self).__init__(*args, **kwargs)

        self.model_version = model_version
        self.statistics = statistics
