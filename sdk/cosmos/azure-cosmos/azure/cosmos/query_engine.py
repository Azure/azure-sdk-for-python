from typing import Protocol, Optional, Union, Dict, List, Any


class DataRequest(Protocol):
    @property
    def pkrange_id(self) -> str:
        raise NotImplementedError

    @property
    def continuation(self) -> str:
        raise NotImplementedError


class PipelineResult(Protocol):
    @property
    def items(self) -> List[str]:
        raise NotImplementedError

    @property
    def requests(self) -> List[DataRequest]:
        raise NotImplementedError

    @property
    def terminated(self) -> bool:
        raise NotImplementedError


class QueryPipeline(Protocol):
    def close(self) -> None:
        raise NotImplementedError

    def query(self) -> str:
        raise NotImplementedError

    def next_batch(self) -> PipelineResult:
        raise NotImplementedError

    def provide_data(self, pkrangeid: str, data: List[Dict[str, Any]], continuation: Optional[str]) -> None:
        raise NotImplementedError


class QueryEngine(Protocol):
    def create_pipeline(self, query: Optional[Union[str, Dict[str, Any]]], plan: Dict[str, Any], pkranges: List[Dict[str, Any]]) -> QueryPipeline:
        raise NotImplementedError
