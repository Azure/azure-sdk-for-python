```py
namespace azure.mgmt.costmanagementpriceestimation

    class azure.mgmt.costmanagementpriceestimation.CostManagementClient: implements ContextManager 
        operations: Operations
        price_estimation: PriceEstimationOperations

        def __init__(
                self, 
                credential: TokenCredential, 
                subscription_id: str, 
                base_url: Optional[str] = None, 
                *, 
                api_version: str = ..., 
                cloud_setting: Optional[AzureClouds] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        def close(self) -> None: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> HttpResponse: ...


namespace azure.mgmt.costmanagementpriceestimation.aio

    class azure.mgmt.costmanagementpriceestimation.aio.CostManagementClient: implements AsyncContextManager 
        operations: Operations
        price_estimation: PriceEstimationOperations

        def __init__(
                self, 
                credential: AsyncTokenCredential, 
                subscription_id: str, 
                base_url: Optional[str] = None, 
                *, 
                api_version: str = ..., 
                cloud_setting: Optional[AzureClouds] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        async def close(self) -> None: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> Awaitable[AsyncHttpResponse]: ...


namespace azure.mgmt.costmanagementpriceestimation.aio.operations

    class azure.mgmt.costmanagementpriceestimation.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Operation]: ...


    class azure.mgmt.costmanagementpriceestimation.aio.operations.PriceEstimationOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_estimate_prices(
                self, 
                body: EstimateContent, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EstimateResult]: ...

        @overload
        async def begin_estimate_prices(
                self, 
                body: EstimateContent, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EstimateResult]: ...

        @overload
        async def begin_estimate_prices(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EstimateResult]: ...

        @distributed_trace_async
        async def begin_get_estimate_prices_operation_result(
                self, 
                operation_id: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[EstimateResult]: ...


namespace azure.mgmt.costmanagementpriceestimation.models

    class azure.mgmt.costmanagementpriceestimation.models.ActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTERNAL = "Internal"


    class azure.mgmt.costmanagementpriceestimation.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.costmanagementpriceestimation.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.costmanagementpriceestimation.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.costmanagementpriceestimation.models.EstimateAppliedValue(_Model):
        field: str
        value: EstimateValue


    class azure.mgmt.costmanagementpriceestimation.models.EstimateArrayValue(EstimateValue, discriminator='array'):
        items_property: list[EstimateValue]
        kind: Literal[EstimateValueKind.ARRAY]

        @overload
        def __init__(
                self, 
                *, 
                items_property: list[EstimateValue]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.costmanagementpriceestimation.models.EstimateBooleanValue(EstimateValue, discriminator='boolean'):
        kind: Literal[EstimateValueKind.BOOLEAN]
        value: bool

        @overload
        def __init__(
                self, 
                *, 
                value: bool
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.costmanagementpriceestimation.models.EstimateComponentResult(_Model):
        component: str
        meter_ids: Optional[list[str]]
        monthly: EstimateCostSummary
        upfront: EstimateCostSummary


    class azure.mgmt.costmanagementpriceestimation.models.EstimateContent(_Model):
        resources: list[EstimateResourceInput]

        @overload
        def __init__(
                self, 
                *, 
                resources: list[EstimateResourceInput]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.costmanagementpriceestimation.models.EstimateCostStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMPLETE = "Complete"
        PARTIAL = "Partial"
        UNAVAILABLE = "Unavailable"


    class azure.mgmt.costmanagementpriceestimation.models.EstimateCostSummary(_Model):
        amount: Optional[float]
        known_amount: Optional[float]
        status: Union[str, EstimateCostStatus]


    class azure.mgmt.costmanagementpriceestimation.models.EstimateDiagnostic(_Model):
        code: str
        component: Optional[str]
        message: str
        target: Optional[str]


    class azure.mgmt.costmanagementpriceestimation.models.EstimateEffectiveConfiguration(_Model):
        applied_values: list[EstimateAppliedValue]
        assumed_usage_fields: list[str]
        defaulted_fields: list[str]
        resource_api_version: str
        resource_type: str


    class azure.mgmt.costmanagementpriceestimation.models.EstimateNamedValue(_Model):
        name: str
        value: EstimateValue

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                value: EstimateValue
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.costmanagementpriceestimation.models.EstimateNumberValue(EstimateValue, discriminator='number'):
        kind: Literal[EstimateValueKind.NUMBER]
        value: float

        @overload
        def __init__(
                self, 
                *, 
                value: float
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.costmanagementpriceestimation.models.EstimateObjectValue(EstimateValue, discriminator='object'):
        kind: Literal[EstimateValueKind.OBJECT]
        members: list[EstimateNamedValue]

        @overload
        def __init__(
                self, 
                *, 
                members: list[EstimateNamedValue]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.costmanagementpriceestimation.models.EstimateResourceInput(_Model):
        inputs: list[EstimateNamedValue]
        resource_api_version: str
        resource_type: str

        @overload
        def __init__(
                self, 
                *, 
                inputs: list[EstimateNamedValue], 
                resource_api_version: str, 
                resource_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.costmanagementpriceestimation.models.EstimateResourceResult(_Model):
        assumptions: list[EstimateDiagnostic]
        components: list[EstimateComponentResult]
        configuration: Optional[EstimateEffectiveConfiguration]
        input_index: int
        issues: list[EstimateDiagnostic]
        monthly: EstimateCostSummary
        upfront: EstimateCostSummary


    class azure.mgmt.costmanagementpriceestimation.models.EstimateResult(_Model):
        assumptions: list[EstimateDiagnostic]
        coverage: Literal["SubmittedPricingInputs"]
        currency: str
        pricing_as_of: datetime
        results: list[EstimateResourceResult]
        totals: EstimateTotals

        def __init__(
                self, 
                *args: Any, 
                **kwargs: Any
            ) -> None: ...


    class azure.mgmt.costmanagementpriceestimation.models.EstimateStringValue(EstimateValue, discriminator='string'):
        kind: Literal[EstimateValueKind.STRING]
        value: str

        @overload
        def __init__(
                self, 
                *, 
                value: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.costmanagementpriceestimation.models.EstimateTotals(_Model):
        monthly: EstimateCostSummary
        upfront: EstimateCostSummary


    class azure.mgmt.costmanagementpriceestimation.models.EstimateValue(_Model):
        kind: str

        @overload
        def __init__(
                self, 
                *, 
                kind: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.costmanagementpriceestimation.models.EstimateValueKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ARRAY = "array"
        BOOLEAN = "boolean"
        NUMBER = "number"
        OBJECT = "object"
        STRING = "string"


    class azure.mgmt.costmanagementpriceestimation.models.Operation(_Model):
        action_type: Optional[Union[str, ActionType]]
        display: Optional[OperationDisplay]
        is_data_action: Optional[bool]
        name: Optional[str]
        origin: Optional[Union[str, Origin]]

        @overload
        def __init__(
                self, 
                *, 
                display: Optional[OperationDisplay] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.costmanagementpriceestimation.models.OperationDisplay(_Model):
        description: Optional[str]
        operation: Optional[str]
        provider: Optional[str]
        resource: Optional[str]


    class azure.mgmt.costmanagementpriceestimation.models.Origin(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM = "system"
        USER = "user"
        USER_SYSTEM = "user,system"


namespace azure.mgmt.costmanagementpriceestimation.operations

    class azure.mgmt.costmanagementpriceestimation.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Operation]: ...


    class azure.mgmt.costmanagementpriceestimation.operations.PriceEstimationOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_estimate_prices(
                self, 
                body: EstimateContent, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EstimateResult]: ...

        @overload
        def begin_estimate_prices(
                self, 
                body: EstimateContent, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EstimateResult]: ...

        @overload
        def begin_estimate_prices(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EstimateResult]: ...

        @distributed_trace
        def begin_get_estimate_prices_operation_result(
                self, 
                operation_id: str, 
                **kwargs: Any
            ) -> LROPoller[EstimateResult]: ...


namespace azure.mgmt.costmanagementpriceestimation.types

    class azure.mgmt.costmanagementpriceestimation.types.EstimateArrayValue(TypedDict, total=False):
        key "items": Required[list[EstimateValue]]
        key "kind": Required[Literal[EstimateValueKind.ARRAY]]
        items: list[EstimateValue]
        kind: Literal[EstimateValueKind.ARRAY]


    class azure.mgmt.costmanagementpriceestimation.types.EstimateBooleanValue(TypedDict, total=False):
        key "kind": Required[Literal[EstimateValueKind.BOOLEAN]]
        key "value": Required[bool]
        kind: Literal[EstimateValueKind.BOOLEAN]
        value: bool


    class azure.mgmt.costmanagementpriceestimation.types.EstimateContent(TypedDict, total=False):
        key "resources": Required[list[EstimateResourceInput]]
        resources: list[EstimateResourceInput]


    class azure.mgmt.costmanagementpriceestimation.types.EstimateNamedValue(TypedDict, total=False):
        key "name": Required[str]
        key "value": Required[EstimateValue]
        name: str
        value: EstimateValue


    class azure.mgmt.costmanagementpriceestimation.types.EstimateNumberValue(TypedDict, total=False):
        key "kind": Required[Literal[EstimateValueKind.NUMBER]]
        key "value": Required[float]
        kind: Literal[EstimateValueKind.NUMBER]
        value: float


    class azure.mgmt.costmanagementpriceestimation.types.EstimateObjectValue(TypedDict, total=False):
        key "kind": Required[Literal[EstimateValueKind.OBJECT]]
        key "members": Required[list[EstimateNamedValue]]
        kind: Literal[EstimateValueKind.OBJECT]
        members: list[EstimateNamedValue]


    class azure.mgmt.costmanagementpriceestimation.types.EstimateResourceInput(TypedDict, total=False):
        key "inputs": Required[list[EstimateNamedValue]]
        key "resourceApiVersion": Required[str]
        key "resourceType": Required[str]
        inputs: list[EstimateNamedValue]
        resourceApiVersion: str
        resourceType: str


    class azure.mgmt.costmanagementpriceestimation.types.EstimateStringValue(TypedDict, total=False):
        key "kind": Required[Literal[EstimateValueKind.STRING]]
        key "value": Required[str]
        kind: Literal[EstimateValueKind.STRING]
        value: str


    class azure.mgmt.costmanagementpriceestimation.types.EstimateValueKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ARRAY = "array"
        BOOLEAN = "boolean"
        NUMBER = "number"
        OBJECT = "object"
        STRING = "string"


```