```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.communication.phonenumbers

    class azure.communication.phonenumbers.AvailablePhoneNumber(Model):
        assignment_type: Union[str, PhoneNumberAssignmentType]
        capabilities: PhoneNumberCapabilities
        cost: PhoneNumberCost
        country_code: str
        error: CommunicationError
        id: str
        is_agreement_to_not_resell_required: bool
        phone_number: str
        phone_number_type: Union[str, PhoneNumberType]
        status: Union[str, PhoneNumberAvailabilityStatus]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                assignment_type: Union[str, PhoneNumberAssignmentType], 
                capabilities: PhoneNumberCapabilities, 
                country_code: str, 
                error: Optional[CommunicationError] = ..., 
                phone_number_type: Union[str, PhoneNumberType], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.communication.phonenumbers.BillingFrequency(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MONTHLY = "monthly"


    class azure.communication.phonenumbers.CommunicationError(Model):
        code: str
        details: list[CommunicationError]
        inner_error: CommunicationError
        message: str
        target: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                code: str, 
                message: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.communication.phonenumbers.OperatorInformation(Model):
        international_format: str
        iso_country_code: str
        national_format: str
        number_type: Union[str, OperatorNumberType]
        operator_details: OperatorDetails
        phone_number: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                international_format: Optional[str] = ..., 
                iso_country_code: Optional[str] = ..., 
                national_format: Optional[str] = ..., 
                number_type: Optional[Union[str, OperatorNumberType]] = ..., 
                operator_details: Optional[OperatorDetails] = ..., 
                phone_number: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.communication.phonenumbers.OperatorInformationOptions(Model):
        include_additional_operator_details: bool

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                include_additional_operator_details: Optional[bool] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.communication.phonenumbers.OperatorInformationResult(Model):
        values: list[OperatorInformation]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                values: Optional[List[OperatorInformation]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.communication.phonenumbers.PhoneNumberAdministrativeDivision(Model):
        abbreviated_name: str
        localized_name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                abbreviated_name: str, 
                localized_name: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.communication.phonenumbers.PhoneNumberAreaCode(Model):
        area_code: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                area_code: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.communication.phonenumbers.PhoneNumberAssignmentType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "application"
        PERSON = "person"


    class azure.communication.phonenumbers.PhoneNumberAvailabilityStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AVAILABLE = "available"
        ERROR = "error"
        EXPIRED = "expired"
        PURCHASED = "purchased"
        RESERVED = "reserved"


    class azure.communication.phonenumbers.PhoneNumberCapabilities(Model):
        calling: Union[str, PhoneNumberCapabilityType]
        sms: Union[str, PhoneNumberCapabilityType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                calling: Union[str, PhoneNumberCapabilityType], 
                sms: Union[str, PhoneNumberCapabilityType], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.communication.phonenumbers.PhoneNumberCapabilityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INBOUND = "inbound"
        INBOUND_OUTBOUND = "inbound+outbound"
        NONE = "none"
        OUTBOUND = "outbound"


    class azure.communication.phonenumbers.PhoneNumberCost(Model):
        amount: float
        billing_frequency: Union[str, BillingFrequency]
        currency_code: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                amount: float, 
                billing_frequency: Union[str, BillingFrequency], 
                currency_code: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.communication.phonenumbers.PhoneNumberCountry(Model):
        country_code: str
        localized_name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                country_code: str, 
                localized_name: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.communication.phonenumbers.PhoneNumberLocality(Model):
        administrative_division: PhoneNumberAdministrativeDivision
        localized_name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                administrative_division: Optional[PhoneNumberAdministrativeDivision] = ..., 
                localized_name: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.communication.phonenumbers.PhoneNumberOffering(Model):
        assignment_type: Union[str, PhoneNumberAssignmentType]
        available_capabilities: PhoneNumberCapabilities
        cost: PhoneNumberCost
        phone_number_type: Union[str, PhoneNumberType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                assignment_type: Optional[Union[str, PhoneNumberAssignmentType]] = ..., 
                available_capabilities: Optional[PhoneNumberCapabilities] = ..., 
                cost: PhoneNumberCost, 
                phone_number_type: Optional[Union[str, PhoneNumberType]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.communication.phonenumbers.PhoneNumberSearchResult(Model):
        assignment_type: Union[str, PhoneNumberAssignmentType]
        capabilities: PhoneNumberCapabilities
        cost: PhoneNumberCost
        error: Union[str, PhoneNumberSearchResultError]
        error_code: int
        is_agreement_to_not_resell_required: bool
        phone_number_type: Union[str, PhoneNumberType]
        phone_numbers: list[str]
        search_expires_by: datetime
        search_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                assignment_type: Union[str, PhoneNumberAssignmentType], 
                capabilities: PhoneNumberCapabilities, 
                cost: PhoneNumberCost, 
                error: Optional[Union[str, PhoneNumberSearchResultError]] = ..., 
                error_code: Optional[int] = ..., 
                is_agreement_to_not_resell_required: Optional[bool] = ..., 
                phone_number_type: Union[str, PhoneNumberType], 
                phone_numbers: List[str], 
                search_expires_by: datetime, 
                search_id: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.communication.phonenumbers.PhoneNumberSearchResultError(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALL_NUMBERS_NOT_ACQUIRED = "AllNumbersNotAcquired"
        AUTHORIZATION_DENIED = "AuthorizationDenied"
        BILLING_UNAVAILABLE = "BillingUnavailable"
        INVALID_ADDRESS = "InvalidAddress"
        INVALID_OFFER_MODEL = "InvalidOfferModel"
        MISSING_ADDRESS = "MissingAddress"
        NOT_ENOUGH_CREDIT = "NotEnoughCredit"
        NOT_ENOUGH_LICENSES = "NotEnoughLicenses"
        NO_ERROR = "NoError"
        NO_WALLET = "NoWallet"
        NUMBERS_PARTIALLY_ACQUIRED = "NumbersPartiallyAcquired"
        OUT_OF_STOCK = "OutOfStock"
        PROVISIONING_FAILED = "ProvisioningFailed"
        PURCHASE_FAILED = "PurchaseFailed"
        RESERVATION_EXPIRED = "ReservationExpired"
        UNKNOWN_ERROR_CODE = "UnknownErrorCode"
        UNKNOWN_SEARCH_ERROR = "UnknownSearchError"


    class azure.communication.phonenumbers.PhoneNumberType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        GEOGRAPHIC = "geographic"
        MOBILE = "mobile"
        TOLL_FREE = "tollFree"


    class azure.communication.phonenumbers.PhoneNumbersBrowseResult(Model):
        phone_numbers: list[AvailablePhoneNumber]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                phone_numbers: List[AvailablePhoneNumber], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.communication.phonenumbers.PhoneNumbersClient:

        def __init__(
                self, 
                endpoint: str, 
                credential: Union[TokenCredential, AzureKeyCredential], 
                *, 
                accepted_language: str = ..., 
                api_version: str = ..., 
                **kwargs: Any
            ) -> None: ...

        @classmethod
        def from_connection_string(
                cls, 
                conn_str: str, 
                **kwargs: Any
            ) -> PhoneNumbersClient: ...

        @distributed_trace
        def begin_purchase_phone_numbers(
                self, 
                search_id: str, 
                *, 
                agree_to_not_resell: bool = False, 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = True, 
                polling_interval: int = _DEFAULT_POLLING_INTERVAL_IN_SECONDS, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_purchase_reservation(
                self, 
                reservation_id: str, 
                *, 
                agree_to_not_resell: bool = False, 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = True, 
                polling_interval: int = _DEFAULT_POLLING_INTERVAL_IN_SECONDS, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_release_phone_number(
                self, 
                phone_number: str, 
                *, 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = True, 
                polling_interval: int = _DEFAULT_POLLING_INTERVAL_IN_SECONDS, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_search_available_phone_numbers(
                self, 
                country_code: str, 
                phone_number_type: Union[PhoneNumberType, str], 
                assignment_type: Union[PhoneNumberAssignmentType, str], 
                capabilities: PhoneNumberCapabilities, 
                *, 
                area_code: Optional[str] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = True, 
                polling_interval: int = _DEFAULT_POLLING_INTERVAL_IN_SECONDS, 
                quantity: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[PhoneNumberSearchResult]: ...

        @distributed_trace
        def begin_update_phone_number_capabilities(
                self, 
                phone_number: str, 
                sms: Optional[Union[str, PhoneNumberCapabilityType]] = None, 
                calling: Optional[Union[str, PhoneNumberCapabilityType]] = None, 
                *, 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = True, 
                polling_interval: int = _DEFAULT_POLLING_INTERVAL_IN_SECONDS, 
                **kwargs: Any
            ) -> LROPoller[PurchasedPhoneNumber]: ...

        @distributed_trace
        def browse_available_phone_numbers(
                self, 
                *, 
                assignment_type: Optional[Union[str, PhoneNumberAssignmentType]] = ..., 
                calling_capability: Optional[Union[str, PhoneNumberCapabilityType]] = ..., 
                country_code: str, 
                phone_number_prefixes: Optional[List[str]] = ..., 
                phone_number_type: Union[str, PhoneNumberType], 
                sms_capability: Optional[Union[str, PhoneNumberCapabilityType]] = ..., 
                **kwargs: Any
            ) -> PhoneNumbersBrowseResult: ...

        @distributed_trace
        def create_or_update_reservation(
                self, 
                *, 
                numbers_to_add: Optional[List[AvailablePhoneNumber]] = ..., 
                numbers_to_remove: Optional[List[str]] = ..., 
                reservation_id: str, 
                **kwargs: Any
            ) -> PhoneNumbersReservation: ...

        @distributed_trace
        def delete_reservation(
                self, 
                reservation_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get_purchased_phone_number(
                self, 
                phone_number: str, 
                **kwargs: Any
            ) -> PurchasedPhoneNumber: ...

        @distributed_trace
        def get_reservation(
                self, 
                reservation_id: str, 
                **kwargs: Any
            ) -> PhoneNumbersReservation: ...

        @distributed_trace
        def list_available_area_codes(
                self, 
                country_code: str, 
                phone_number_type: Union[PhoneNumberType, str], 
                *, 
                administrative_division: Optional[str] = ..., 
                assignment_type: Optional[Union[PhoneNumberAssignmentType, str]] = ..., 
                locality: Optional[str] = ..., 
                skip: int = 0, 
                **kwargs: Any
            ) -> ItemPaged[PhoneNumberAreaCode]: ...

        @distributed_trace
        def list_available_countries(
                self, 
                *, 
                skip: int = 0, 
                **kwargs: Any
            ) -> ItemPaged[PhoneNumberCountry]: ...

        @distributed_trace
        def list_available_localities(
                self, 
                country_code: str, 
                *, 
                administrative_division: Optional[str] = ..., 
                phone_number_type: Optional[Union[PhoneNumberType, str]] = ..., 
                skip: int = 0, 
                **kwargs: Any
            ) -> ItemPaged[PhoneNumberLocality]: ...

        @distributed_trace
        def list_available_offerings(
                self, 
                country_code: str, 
                *, 
                assignment_type: Optional[Union[PhoneNumberAssignmentType, str]] = ..., 
                phone_number_type: Optional[Union[PhoneNumberType, str]] = ..., 
                skip: int = 0, 
                **kwargs: Any
            ) -> ItemPaged[PhoneNumberOffering]: ...

        @distributed_trace
        def list_purchased_phone_numbers(
                self, 
                *, 
                skip: int = 0, 
                top: int = 100, 
                **kwargs: Any
            ) -> ItemPaged[PurchasedPhoneNumber]: ...

        @distributed_trace
        def list_reservations(
                self, 
                *, 
                max_page_size: int = 100, 
                **kwargs: Any
            ) -> ItemPaged[PhoneNumbersReservation]: ...

        @distributed_trace
        def search_operator_information(
                self, 
                phone_numbers: Union[str, List[str]], 
                *, 
                options: Optional[OperatorInformationOptions] = ..., 
                **kwargs: Any
            ) -> OperatorInformationResult: ...


    class azure.communication.phonenumbers.PhoneNumbersReservation(Model):
        expires_at: datetime
        id: str
        phone_numbers: dict[str, AvailablePhoneNumber]
        status: Union[str, ReservationStatus]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                phone_numbers: Optional[Dict[str, AvailablePhoneNumber]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.communication.phonenumbers.PurchasedPhoneNumber(Model):
        assignment_type: Union[str, PhoneNumberAssignmentType]
        capabilities: PhoneNumberCapabilities
        cost: PhoneNumberCost
        country_code: str
        id: str
        phone_number: str
        phone_number_type: Union[str, PhoneNumberType]
        purchase_date: datetime

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                assignment_type: Union[str, PhoneNumberAssignmentType], 
                capabilities: PhoneNumberCapabilities, 
                cost: PhoneNumberCost, 
                country_code: str, 
                id: str, 
                phone_number: str, 
                phone_number_type: Union[str, PhoneNumberType], 
                purchase_date: datetime, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.communication.phonenumbers.ReservationStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "active"
        COMPLETED = "completed"
        EXPIRED = "expired"
        SUBMITTED = "submitted"


namespace azure.communication.phonenumbers.aio

    class azure.communication.phonenumbers.aio.PhoneNumbersClient: implements AsyncContextManager 

        def __init__(
                self, 
                endpoint: str, 
                credential: Union[AsyncTokenCredential, AzureKeyCredential], 
                *, 
                accepted_language: str = ..., 
                api_version: str = ..., 
                **kwargs: Any
            ) -> None: ...

        @classmethod
        def from_connection_string(
                cls, 
                conn_str: str, 
                **kwargs: Any
            ) -> PhoneNumbersClient: ...

        @distributed_trace_async
        async def begin_purchase_phone_numbers(
                self, 
                search_id: str, 
                *, 
                agree_to_not_resell: bool = False, 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = True, 
                polling_interval: int = _DEFAULT_POLLING_INTERVAL_IN_SECONDS, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_purchase_reservation(
                self, 
                reservation_id: str, 
                *, 
                agree_to_not_resell: bool = False, 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = True, 
                polling_interval: int = _DEFAULT_POLLING_INTERVAL_IN_SECONDS, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_release_phone_number(
                self, 
                phone_number: str, 
                *, 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = True, 
                polling_interval: int = _DEFAULT_POLLING_INTERVAL_IN_SECONDS, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_search_available_phone_numbers(
                self, 
                country_code: str, 
                phone_number_type: Union[PhoneNumberType, str], 
                assignment_type: Union[PhoneNumberAssignmentType, str], 
                capabilities: PhoneNumberCapabilities, 
                *, 
                area_code: Optional[str] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = True, 
                polling_interval: int = _DEFAULT_POLLING_INTERVAL_IN_SECONDS, 
                quantity: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[PhoneNumberSearchResult]: ...

        @distributed_trace_async
        async def begin_update_phone_number_capabilities(
                self, 
                phone_number: str, 
                sms: Optional[Union[str, PhoneNumberCapabilityType]] = None, 
                calling: Optional[Union[str, PhoneNumberCapabilityType]] = None, 
                *, 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = True, 
                polling_interval: int = _DEFAULT_POLLING_INTERVAL_IN_SECONDS, 
                **kwargs: Any
            ) -> AsyncLROPoller[PurchasedPhoneNumber]: ...

        @distributed_trace_async
        async def browse_available_phone_numbers(
                self, 
                *, 
                assignment_type: Optional[Union[str, PhoneNumberAssignmentType]] = ..., 
                calling_capability: Optional[Union[str, PhoneNumberCapabilityType]] = ..., 
                country_code: str, 
                phone_number_prefixes: Optional[List[str]] = ..., 
                phone_number_type: Union[str, PhoneNumberType], 
                sms_capability: Optional[Union[str, PhoneNumberCapabilityType]] = ..., 
                **kwargs: Any
            ) -> PhoneNumbersBrowseResult: ...

        async def close(self) -> None: ...

        @distributed_trace_async
        async def create_or_update_reservation(
                self, 
                *, 
                numbers_to_add: Optional[List[AvailablePhoneNumber]] = ..., 
                numbers_to_remove: Optional[List[str]] = ..., 
                reservation_id: str, 
                **kwargs: Any
            ) -> PhoneNumbersReservation: ...

        @distributed_trace_async
        async def delete_reservation(
                self, 
                reservation_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get_purchased_phone_number(
                self, 
                phone_number: str, 
                **kwargs: Any
            ) -> PurchasedPhoneNumber: ...

        @distributed_trace_async
        async def get_reservation(
                self, 
                reservation_id: str, 
                **kwargs: Any
            ) -> PhoneNumbersReservation: ...

        @distributed_trace
        def list_available_area_codes(
                self, 
                country_code: str, 
                phone_number_type: Union[PhoneNumberType, str], 
                *, 
                administrative_division: Optional[str] = ..., 
                assignment_type: Optional[Union[PhoneNumberAssignmentType, str]] = ..., 
                locality: Optional[str] = ..., 
                skip: int = 0, 
                **kwargs: Any
            ) -> AsyncItemPaged[PhoneNumberAreaCode]: ...

        @distributed_trace
        def list_available_countries(
                self, 
                *, 
                skip: int = 0, 
                **kwargs: Any
            ) -> AsyncItemPaged[PhoneNumberCountry]: ...

        @distributed_trace
        def list_available_localities(
                self, 
                country_code: str, 
                *, 
                administrative_division: Optional[str] = ..., 
                phone_number_type: Optional[Union[PhoneNumberType, str]] = ..., 
                skip: int = 0, 
                **kwargs: Any
            ) -> AsyncItemPaged[PhoneNumberLocality]: ...

        @distributed_trace
        def list_available_offerings(
                self, 
                country_code: str, 
                *, 
                assignment_type: Optional[Union[PhoneNumberAssignmentType, str]] = ..., 
                phone_number_type: Optional[Union[PhoneNumberType, str]] = ..., 
                skip: int = 0, 
                **kwargs: Any
            ) -> AsyncItemPaged[PhoneNumberOffering]: ...

        @distributed_trace
        def list_purchased_phone_numbers(
                self, 
                *, 
                skip: int = 0, 
                top: int = 100, 
                **kwargs: Any
            ) -> AsyncItemPaged[PurchasedPhoneNumber]: ...

        @distributed_trace
        def list_reservations(
                self, 
                *, 
                max_page_size: int = 100, 
                **kwargs: Any
            ) -> AsyncItemPaged[PhoneNumbersReservation]: ...

        @distributed_trace_async
        async def search_operator_information(
                self, 
                phone_numbers: Union[str, List[str]], 
                *, 
                options: Optional[OperatorInformationOptions] = ..., 
                **kwargs: Any
            ) -> OperatorInformationResult: ...


namespace azure.communication.phonenumbers.siprouting

    class azure.communication.phonenumbers.siprouting.SipRoutingClient: implements ContextManager 

        def __init__(
                self, 
                endpoint: str, 
                credential: Union[TokenCredential, AzureKeyCredential], 
                *, 
                api_version: str = ..., 
                **kwargs: Any
            ) -> None: ...

        @classmethod
        def from_connection_string(
                cls, 
                conn_str: str, 
                **kwargs: Any
            ) -> SipRoutingClient: ...

        def close(self) -> None: ...

        @distributed_trace
        def delete_trunk(
                self, 
                trunk_fqdn: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get_trunk(
                self, 
                trunk_fqdn: str, 
                **kwargs: Any
            ) -> SipTrunk: ...

        @distributed_trace
        def list_routes(self, **kwargs: Any) -> ItemPaged[SipTrunkRoute]: ...

        @distributed_trace
        def list_trunks(self, **kwargs: Any) -> ItemPaged[SipTrunk]: ...

        @distributed_trace
        def set_routes(
                self, 
                routes: List[SipTrunkRoute], 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def set_trunk(
                self, 
                trunk: SipTrunk, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def set_trunks(
                self, 
                trunks: List[SipTrunk], 
                **kwargs: Any
            ) -> None: ...


    class azure.communication.phonenumbers.siprouting.SipTrunk:
        fqdn: str
        sip_signaling_port: int

        def __init__(
                self, 
                *, 
                fqdn: str = ..., 
                sip_signaling_port: int = ..., 
                **kwargs
            ): ...


    class azure.communication.phonenumbers.siprouting.SipTrunkRoute:
        description: str
        name: str
        number_pattern: str
        trunks: list[str]

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                name: str = ..., 
                number_pattern: str = ..., 
                trunks: Optional[List[str]] = ..., 
                **kwargs
            ): ...


namespace azure.communication.phonenumbers.siprouting.aio

    class azure.communication.phonenumbers.siprouting.aio.SipRoutingClient: implements AsyncContextManager 

        def __init__(
                self, 
                endpoint: str, 
                credential: Union[AsyncTokenCredential, AzureKeyCredential], 
                *, 
                api_version: str = ..., 
                **kwargs: Any
            ) -> None: ...

        @classmethod
        def from_connection_string(
                cls, 
                conn_str: str, 
                **kwargs: Any
            ) -> SipRoutingClient: ...

        async def close(self) -> None: ...

        @distributed_trace_async
        async def delete_trunk(
                self, 
                trunk_fqdn: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get_trunk(
                self, 
                trunk_fqdn: str, 
                **kwargs: Any
            ) -> SipTrunk: ...

        @distributed_trace
        def list_routes(self, **kwargs: Any) -> AsyncItemPaged[SipTrunkRoute]: ...

        @distributed_trace
        def list_trunks(self, **kwargs: Any) -> AsyncItemPaged[SipTrunk]: ...

        @distributed_trace_async
        async def set_routes(
                self, 
                routes: List[SipTrunkRoute], 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def set_trunk(
                self, 
                trunk: SipTrunk, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def set_trunks(
                self, 
                trunks: List[SipTrunk], 
                **kwargs: Any
            ) -> None: ...


```