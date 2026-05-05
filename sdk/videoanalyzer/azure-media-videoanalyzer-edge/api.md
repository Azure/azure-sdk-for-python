```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.media.videoanalyzeredge

    class azure.media.videoanalyzeredge.CertificateSource(Model):
        type: str

        def __init__(self, **kwargs): ...


    class azure.media.videoanalyzeredge.CognitiveServicesVisionProcessor(ProcessorNodeBase):
        endpoint: EndpointBase
        image: ImageProperties
        inputs: list[NodeInput]
        name: str
        operation: SpatialAnalysisOperationBase
        sampling_options: SamplingOptions
        type: str

        def __init__(
                self, 
                *, 
                endpoint: EndpointBase, 
                image: Optional[ImageProperties] = ..., 
                inputs: List[NodeInput], 
                name: str, 
                operation: SpatialAnalysisOperationBase, 
                sampling_options: Optional[SamplingOptions] = ..., 
                **kwargs
            ): ...


    class azure.media.videoanalyzeredge.CredentialsBase(Model):
        type: str

        def __init__(self, **kwargs): ...


    class azure.media.videoanalyzeredge.DiscoveredOnvifDevice(Model):
        endpoints: list[str]
        remote_ip_address: str
        scopes: list[str]
        service_identifier: str

        def __init__(
                self, 
                *, 
                endpoints: Optional[List[str]] = ..., 
                remote_ip_address: Optional[str] = ..., 
                scopes: Optional[List[str]] = ..., 
                service_identifier: Optional[str] = ..., 
                **kwargs
            ): ...


    class azure.media.videoanalyzeredge.DiscoveredOnvifDeviceCollection(Model):
        value: list[DiscoveredOnvifDevice]

        def __init__(
                self, 
                *, 
                value: Optional[List[DiscoveredOnvifDevice]] = ..., 
                **kwargs
            ): ...


    class azure.media.videoanalyzeredge.EndpointBase(Model):
        credentials: CredentialsBase
        type: str
        url: str

        def __init__(
                self, 
                *, 
                credentials: Optional[CredentialsBase] = ..., 
                url: str, 
                **kwargs
            ): ...


    class azure.media.videoanalyzeredge.ExtensionProcessorBase(ProcessorNodeBase):
        endpoint: EndpointBase
        image: ImageProperties
        inputs: list[NodeInput]
        name: str
        sampling_options: SamplingOptions
        type: str

        def __init__(
                self, 
                *, 
                endpoint: EndpointBase, 
                image: ImageProperties, 
                inputs: List[NodeInput], 
                name: str, 
                sampling_options: Optional[SamplingOptions] = ..., 
                **kwargs
            ): ...


    class azure.media.videoanalyzeredge.FileSink(SinkNodeBase):
        base_directory_path: str
        file_name_pattern: str
        inputs: list[NodeInput]
        maximum_size_mi_b: str
        name: str
        type: str

        def __init__(
                self, 
                *, 
                base_directory_path: str, 
                file_name_pattern: str, 
                inputs: List[NodeInput], 
                maximum_size_mi_b: str, 
                name: str, 
                **kwargs
            ): ...


    class azure.media.videoanalyzeredge.GrpcExtension(ExtensionProcessorBase):
        data_transfer: GrpcExtensionDataTransfer
        endpoint: EndpointBase
        extension_configuration: str
        image: ImageProperties
        inputs: list[NodeInput]
        name: str
        sampling_options: SamplingOptions
        type: str

        def __init__(
                self, 
                *, 
                data_transfer: GrpcExtensionDataTransfer, 
                endpoint: EndpointBase, 
                extension_configuration: Optional[str] = ..., 
                image: ImageProperties, 
                inputs: List[NodeInput], 
                name: str, 
                sampling_options: Optional[SamplingOptions] = ..., 
                **kwargs
            ): ...


    class azure.media.videoanalyzeredge.GrpcExtensionDataTransfer(Model):
        mode: Union[str, GrpcExtensionDataTransferMode]
        shared_memory_size_mi_b: str

        def __init__(
                self, 
                *, 
                mode: Union[str, GrpcExtensionDataTransferMode], 
                shared_memory_size_mi_b: Optional[str] = ..., 
                **kwargs
            ): ...


    class azure.media.videoanalyzeredge.GrpcExtensionDataTransferMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EMBEDDED = "embedded"
        SHARED_MEMORY = "sharedMemory"


    class azure.media.videoanalyzeredge.H264Configuration(Model):
        gov_length: float
        profile: Union[str, H264Profile]

        def __init__(
                self, 
                *, 
                gov_length: Optional[float] = ..., 
                profile: Optional[Union[str, H264Profile]] = ..., 
                **kwargs
            ): ...


    class azure.media.videoanalyzeredge.H264Profile(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BASELINE = "Baseline"
        EXTENDED = "Extended"
        HIGH = "High"
        MAIN = "Main"


    class azure.media.videoanalyzeredge.HttpExtension(ExtensionProcessorBase):
        endpoint: EndpointBase
        image: ImageProperties
        inputs: list[NodeInput]
        name: str
        sampling_options: SamplingOptions
        type: str

        def __init__(
                self, 
                *, 
                endpoint: EndpointBase, 
                image: ImageProperties, 
                inputs: List[NodeInput], 
                name: str, 
                sampling_options: Optional[SamplingOptions] = ..., 
                **kwargs
            ): ...


    class azure.media.videoanalyzeredge.HttpHeaderCredentials(CredentialsBase):
        header_name: str
        header_value: str
        type: str

        def __init__(
                self, 
                *, 
                header_name: str, 
                header_value: str, 
                **kwargs
            ): ...


    class azure.media.videoanalyzeredge.ImageFormatBmp(ImageFormatProperties):
        type: str

        def __init__(self, **kwargs): ...


    class azure.media.videoanalyzeredge.ImageFormatJpeg(ImageFormatProperties):
        quality: str
        type: str

        def __init__(
                self, 
                *, 
                quality: Optional[str] = ..., 
                **kwargs
            ): ...


    class azure.media.videoanalyzeredge.ImageFormatPng(ImageFormatProperties):
        type: str

        def __init__(self, **kwargs): ...


    class azure.media.videoanalyzeredge.ImageFormatProperties(Model):
        type: str

        def __init__(self, **kwargs): ...


    class azure.media.videoanalyzeredge.ImageFormatRaw(ImageFormatProperties):
        pixel_format: Union[str, ImageFormatRawPixelFormat]
        type: str

        def __init__(
                self, 
                *, 
                pixel_format: Union[str, ImageFormatRawPixelFormat], 
                **kwargs
            ): ...


    class azure.media.videoanalyzeredge.ImageFormatRawPixelFormat(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ABGR = "abgr"
        ARGB = "argb"
        BGR24 = "bgr24"
        BGRA = "bgra"
        RGB24 = "rgb24"
        RGB555_BE = "rgb555be"
        RGB555_LE = "rgb555le"
        RGB565_BE = "rgb565be"
        RGB565_LE = "rgb565le"
        RGBA = "rgba"
        YUV420_P = "yuv420p"


    class azure.media.videoanalyzeredge.ImageProperties(Model):
        format: ImageFormatProperties
        scale: ImageScale

        def __init__(
                self, 
                *, 
                format: Optional[ImageFormatProperties] = ..., 
                scale: Optional[ImageScale] = ..., 
                **kwargs
            ): ...


    class azure.media.videoanalyzeredge.ImageScale(Model):
        height: str
        mode: Union[str, ImageScaleMode]
        width: str

        def __init__(
                self, 
                *, 
                height: Optional[str] = ..., 
                mode: Optional[Union[str, ImageScaleMode]] = ..., 
                width: Optional[str] = ..., 
                **kwargs
            ): ...


    class azure.media.videoanalyzeredge.ImageScaleMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PAD = "pad"
        PRESERVE_ASPECT_RATIO = "preserveAspectRatio"
        STRETCH = "stretch"


    class azure.media.videoanalyzeredge.IotHubDeviceConnection(Model):
        credentials: CredentialsBase
        device_id: str

        def __init__(
                self, 
                *, 
                credentials: Optional[CredentialsBase] = ..., 
                device_id: str, 
                **kwargs
            ): ...


    class azure.media.videoanalyzeredge.IotHubMessageSink(SinkNodeBase):
        hub_output_name: str
        inputs: list[NodeInput]
        name: str
        type: str

        def __init__(
                self, 
                *, 
                hub_output_name: str, 
                inputs: List[NodeInput], 
                name: str, 
                **kwargs
            ): ...


    class azure.media.videoanalyzeredge.IotHubMessageSource(SourceNodeBase):
        hub_input_name: str
        name: str
        type: str

        def __init__(
                self, 
                *, 
                hub_input_name: Optional[str] = ..., 
                name: str, 
                **kwargs
            ): ...


    class azure.media.videoanalyzeredge.LineCrossingProcessor(ProcessorNodeBase):
        inputs: list[NodeInput]
        lines: list[NamedLineBase]
        name: str
        type: str

        def __init__(
                self, 
                *, 
                inputs: List[NodeInput], 
                lines: List[NamedLineBase], 
                name: str, 
                **kwargs
            ): ...


    class azure.media.videoanalyzeredge.LivePipeline(Model):
        name: str
        properties: LivePipelineProperties
        system_data: SystemData

        def __init__(
                self, 
                *, 
                name: str, 
                properties: Optional[LivePipelineProperties] = ..., 
                system_data: Optional[SystemData] = ..., 
                **kwargs
            ): ...


    class azure.media.videoanalyzeredge.LivePipelineActivateRequest(MethodRequestEmptyBodyBase):
        api_version: str
        method_name: str
        name: str

        def __init__(
                self, 
                *, 
                api_version: Optional[str] = "1.1", 
                name: str, 
                **kwargs
            ): ...


    class azure.media.videoanalyzeredge.LivePipelineCollection(Model):
        continuation_token: str
        value: list[LivePipeline]

        def __init__(
                self, 
                *, 
                continuation_token: Optional[str] = ..., 
                value: Optional[List[LivePipeline]] = ..., 
                **kwargs
            ): ...


    class azure.media.videoanalyzeredge.LivePipelineDeactivateRequest(MethodRequestEmptyBodyBase):
        api_version: str
        method_name: str
        name: str

        def __init__(
                self, 
                *, 
                api_version: Optional[str] = "1.1", 
                name: str, 
                **kwargs
            ): ...


    class azure.media.videoanalyzeredge.LivePipelineDeleteRequest(MethodRequestEmptyBodyBase):
        api_version: str
        method_name: str
        name: str

        def __init__(
                self, 
                *, 
                api_version: Optional[str] = "1.1", 
                name: str, 
                **kwargs
            ): ...


    class azure.media.videoanalyzeredge.LivePipelineGetRequest(MethodRequestEmptyBodyBase):
        api_version: str
        method_name: str
        name: str

        def __init__(
                self, 
                *, 
                api_version: Optional[str] = "1.1", 
                name: str, 
                **kwargs
            ): ...


    class azure.media.videoanalyzeredge.LivePipelineListRequest(MethodRequest):
        api_version: str
        method_name: str

        def __init__(
                self, 
                *, 
                api_version: Optional[str] = "1.1", 
                **kwargs
            ): ...


    class azure.media.videoanalyzeredge.LivePipelineProperties(Model):
        description: str
        parameters: list[ParameterDefinition]
        state: Union[str, LivePipelineState]
        topology_name: str

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                parameters: Optional[List[ParameterDefinition]] = ..., 
                state: Optional[Union[str, LivePipelineState]] = ..., 
                topology_name: Optional[str] = ..., 
                **kwargs
            ): ...


    class azure.media.videoanalyzeredge.LivePipelineSetRequest(MethodRequest):
        api_version: str
        live_pipeline: LivePipeline
        method_name: str

        def __init__(
                self, 
                *, 
                api_version: Optional[str] = "1.1", 
                live_pipeline: LivePipeline, 
                **kwargs
            ): ...

        def _OverrideInstanceSetRequestSerialize(self): ...


    class azure.media.videoanalyzeredge.LivePipelineSetRequestBody(LivePipeline, MethodRequest):
        api_version: str
        method_name: str
        name: str
        properties: LivePipelineProperties
        system_data: SystemData

        def __init__(
                self, 
                *, 
                api_version: Optional[str] = "1.1", 
                name: str, 
                properties: Optional[LivePipelineProperties] = ..., 
                system_data: Optional[SystemData] = ..., 
                **kwargs
            ): ...


    class azure.media.videoanalyzeredge.LivePipelineState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVATING = "activating"
        ACTIVE = "active"
        DEACTIVATING = "deactivating"
        INACTIVE = "inactive"


    class azure.media.videoanalyzeredge.MPEG4Configuration(Model):
        gov_length: float
        profile: Union[str, MPEG4Profile]

        def __init__(
                self, 
                *, 
                gov_length: Optional[float] = ..., 
                profile: Optional[Union[str, MPEG4Profile]] = ..., 
                **kwargs
            ): ...


    class azure.media.videoanalyzeredge.MPEG4Profile(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ASP = "ASP"
        SP = "SP"


    class azure.media.videoanalyzeredge.MediaProfile(Model):
        media_uri: any
        name: str
        video_encoder_configuration: VideoEncoderConfiguration

        def __init__(
                self, 
                *, 
                media_uri: Optional[Any] = ..., 
                name: Optional[str] = ..., 
                video_encoder_configuration: Optional[VideoEncoderConfiguration] = ..., 
                **kwargs
            ): ...


    class azure.media.videoanalyzeredge.MediaUri(Model):
        uri: str

        def __init__(
                self, 
                *, 
                uri: Optional[str] = ..., 
                **kwargs
            ): ...


    class azure.media.videoanalyzeredge.MethodRequest(Model):
        api_version: str
        method_name: str

        def __init__(
                self, 
                *, 
                api_version: Optional[str] = "1.1", 
                **kwargs
            ): ...


    class azure.media.videoanalyzeredge.MethodRequestEmptyBodyBase(MethodRequest):
        api_version: str
        method_name: str
        name: str

        def __init__(
                self, 
                *, 
                api_version: Optional[str] = "1.1", 
                name: str, 
                **kwargs
            ): ...


    class azure.media.videoanalyzeredge.MotionDetectionProcessor(ProcessorNodeBase):
        event_aggregation_window: str
        inputs: list[NodeInput]
        name: str
        output_motion_region: bool
        sensitivity: Union[str, MotionDetectionSensitivity]
        type: str

        def __init__(
                self, 
                *, 
                event_aggregation_window: Optional[str] = ..., 
                inputs: List[NodeInput], 
                name: str, 
                output_motion_region: Optional[bool] = ..., 
                sensitivity: Optional[Union[str, MotionDetectionSensitivity]] = ..., 
                **kwargs
            ): ...


    class azure.media.videoanalyzeredge.MotionDetectionSensitivity(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HIGH = "high"
        LOW = "low"
        MEDIUM = "medium"


    class azure.media.videoanalyzeredge.NamedLineBase(Model):
        name: str
        type: str

        def __init__(
                self, 
                *, 
                name: str, 
                **kwargs
            ): ...


    class azure.media.videoanalyzeredge.NamedLineString(NamedLineBase):
        line: str
        name: str
        type: str

        def __init__(
                self, 
                *, 
                line: str, 
                name: str, 
                **kwargs
            ): ...


    class azure.media.videoanalyzeredge.NamedPolygonBase(Model):
        name: str
        type: str

        def __init__(
                self, 
                *, 
                name: str, 
                **kwargs
            ): ...


    class azure.media.videoanalyzeredge.NamedPolygonString(NamedPolygonBase):
        name: str
        polygon: str
        type: str

        def __init__(
                self, 
                *, 
                name: str, 
                polygon: str, 
                **kwargs
            ): ...


    class azure.media.videoanalyzeredge.NodeInput(Model):
        node_name: str
        output_selectors: list[OutputSelector]

        def __init__(
                self, 
                *, 
                node_name: str, 
                output_selectors: Optional[List[OutputSelector]] = ..., 
                **kwargs
            ): ...


    class azure.media.videoanalyzeredge.ObjectTrackingAccuracy(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HIGH = "high"
        LOW = "low"
        MEDIUM = "medium"


    class azure.media.videoanalyzeredge.ObjectTrackingProcessor(ProcessorNodeBase):
        accuracy: Union[str, ObjectTrackingAccuracy]
        inputs: list[NodeInput]
        name: str
        type: str

        def __init__(
                self, 
                *, 
                accuracy: Optional[Union[str, ObjectTrackingAccuracy]] = ..., 
                inputs: List[NodeInput], 
                name: str, 
                **kwargs
            ): ...


    class azure.media.videoanalyzeredge.OnvifDevice(Model):
        dns: OnvifDns
        hostname: OnvifHostName
        media_profiles: list[MediaProfile]
        system_date_time: OnvifSystemDateTime

        def __init__(
                self, 
                *, 
                dns: Optional[OnvifDns] = ..., 
                hostname: Optional[OnvifHostName] = ..., 
                media_profiles: Optional[List[MediaProfile]] = ..., 
                system_date_time: Optional[OnvifSystemDateTime] = ..., 
                **kwargs
            ): ...


    class azure.media.videoanalyzeredge.OnvifDeviceDiscoverRequest(MethodRequest):
        api_version: str
        discovery_duration: str
        method_name: str

        def __init__(
                self, 
                *, 
                api_version: Optional[str] = "1.1", 
                discovery_duration: Optional[str] = ..., 
                **kwargs
            ): ...


    class azure.media.videoanalyzeredge.OnvifDeviceGetRequest(MethodRequest):
        api_version: str
        endpoint: EndpointBase
        method_name: str

        def __init__(
                self, 
                *, 
                api_version: Optional[str] = "1.1", 
                endpoint: EndpointBase, 
                **kwargs
            ): ...


    class azure.media.videoanalyzeredge.OnvifDns(Model):
        from_dhcp: bool
        ipv4_address: list[str]
        ipv6_address: list[str]

        def __init__(
                self, 
                *, 
                from_dhcp: Optional[bool] = ..., 
                ipv4_address: Optional[List[str]] = ..., 
                ipv6_address: Optional[List[str]] = ..., 
                **kwargs
            ): ...


    class azure.media.videoanalyzeredge.OnvifHostName(Model):
        from_dhcp: bool
        hostname: str

        def __init__(
                self, 
                *, 
                from_dhcp: Optional[bool] = ..., 
                hostname: Optional[str] = ..., 
                **kwargs
            ): ...


    class azure.media.videoanalyzeredge.OnvifSystemDateTime(Model):
        time: str
        time_zone: str
        type: Union[str, OnvifSystemDateTimeType]

        def __init__(
                self, 
                *, 
                time: Optional[str] = ..., 
                time_zone: Optional[str] = ..., 
                type: Optional[Union[str, OnvifSystemDateTimeType]] = ..., 
                **kwargs
            ): ...


    class azure.media.videoanalyzeredge.OnvifSystemDateTimeType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MANUAL = "Manual"
        NTP = "Ntp"


    class azure.media.videoanalyzeredge.OutputSelector(Model):
        operator: Union[str, OutputSelectorOperator]
        property: Union[str, OutputSelectorProperty]
        value: str

        def __init__(
                self, 
                *, 
                operator: Optional[Union[str, OutputSelectorOperator]] = ..., 
                property: Optional[Union[str, OutputSelectorProperty]] = ..., 
                value: Optional[str] = ..., 
                **kwargs
            ): ...


    class azure.media.videoanalyzeredge.OutputSelectorOperator(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        IS_ENUM = "is"
        IS_NOT = "isNot"


    class azure.media.videoanalyzeredge.OutputSelectorProperty(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MEDIA_TYPE = "mediaType"


    class azure.media.videoanalyzeredge.ParameterDeclaration(Model):
        default: str
        description: str
        name: str
        type: Union[str, ParameterType]

        def __init__(
                self, 
                *, 
                default: Optional[str] = ..., 
                description: Optional[str] = ..., 
                name: str, 
                type: Union[str, ParameterType], 
                **kwargs
            ): ...


    class azure.media.videoanalyzeredge.ParameterDefinition(Model):
        name: str
        value: str

        def __init__(
                self, 
                *, 
                name: str, 
                value: Optional[str] = ..., 
                **kwargs
            ): ...


    class azure.media.videoanalyzeredge.ParameterType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BOOL = "bool"
        DOUBLE = "double"
        INT = "int"
        SECRET_STRING = "secretString"
        STRING = "string"


    class azure.media.videoanalyzeredge.PemCertificateList(CertificateSource):
        certificates: list[str]
        type: str

        def __init__(
                self, 
                *, 
                certificates: List[str], 
                **kwargs
            ): ...


    class azure.media.videoanalyzeredge.PipelineTopology(Model):
        name: str
        properties: PipelineTopologyProperties
        system_data: SystemData

        def __init__(
                self, 
                *, 
                name: str, 
                properties: Optional[PipelineTopologyProperties] = ..., 
                system_data: Optional[SystemData] = ..., 
                **kwargs
            ): ...


    class azure.media.videoanalyzeredge.PipelineTopologyCollection(Model):
        continuation_token: str
        value: list[PipelineTopology]

        def __init__(
                self, 
                *, 
                continuation_token: Optional[str] = ..., 
                value: Optional[List[PipelineTopology]] = ..., 
                **kwargs
            ): ...


    class azure.media.videoanalyzeredge.PipelineTopologyDeleteRequest(MethodRequestEmptyBodyBase):
        api_version: str
        method_name: str
        name: str

        def __init__(
                self, 
                *, 
                api_version: Optional[str] = "1.1", 
                name: str, 
                **kwargs
            ): ...


    class azure.media.videoanalyzeredge.PipelineTopologyGetRequest(MethodRequestEmptyBodyBase):
        api_version: str
        method_name: str
        name: str

        def __init__(
                self, 
                *, 
                api_version: Optional[str] = "1.1", 
                name: str, 
                **kwargs
            ): ...


    class azure.media.videoanalyzeredge.PipelineTopologyListRequest(MethodRequest):
        api_version: str
        method_name: str

        def __init__(
                self, 
                *, 
                api_version: Optional[str] = "1.1", 
                **kwargs
            ): ...


    class azure.media.videoanalyzeredge.PipelineTopologyProperties(Model):
        description: str
        parameters: list[ParameterDeclaration]
        processors: list[ProcessorNodeBase]
        sinks: list[SinkNodeBase]
        sources: list[SourceNodeBase]

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                parameters: Optional[List[ParameterDeclaration]] = ..., 
                processors: Optional[List[ProcessorNodeBase]] = ..., 
                sinks: Optional[List[SinkNodeBase]] = ..., 
                sources: Optional[List[SourceNodeBase]] = ..., 
                **kwargs
            ): ...


    class azure.media.videoanalyzeredge.PipelineTopologySetRequest(MethodRequest):
        api_version: str
        method_name: str
        pipeline_topology: PipelineTopology

        def __init__(
                self, 
                *, 
                api_version: Optional[str] = "1.1", 
                pipeline_topology: PipelineTopology, 
                **kwargs
            ): ...

        def _OverrideTopologySetRequestSerialize(self): ...


    class azure.media.videoanalyzeredge.PipelineTopologySetRequestBody(PipelineTopology, MethodRequest):
        api_version: str
        method_name: str
        name: str
        properties: PipelineTopologyProperties
        system_data: SystemData

        def __init__(
                self, 
                *, 
                api_version: Optional[str] = "1.1", 
                name: str, 
                properties: Optional[PipelineTopologyProperties] = ..., 
                system_data: Optional[SystemData] = ..., 
                **kwargs
            ): ...


    class azure.media.videoanalyzeredge.ProcessorNodeBase(Model):
        inputs: list[NodeInput]
        name: str
        type: str

        def __init__(
                self, 
                *, 
                inputs: List[NodeInput], 
                name: str, 
                **kwargs
            ): ...


    class azure.media.videoanalyzeredge.RateControl(Model):
        bit_rate_limit: float
        encoding_interval: float
        frame_rate_limit: float
        guaranteed_frame_rate: bool

        def __init__(
                self, 
                *, 
                bit_rate_limit: Optional[float] = ..., 
                encoding_interval: Optional[float] = ..., 
                frame_rate_limit: Optional[float] = ..., 
                guaranteed_frame_rate: Optional[bool] = ..., 
                **kwargs
            ): ...


    class azure.media.videoanalyzeredge.RemoteDeviceAdapter(Model):
        name: str
        properties: RemoteDeviceAdapterProperties
        system_data: SystemData

        def __init__(
                self, 
                *, 
                name: str, 
                properties: Optional[RemoteDeviceAdapterProperties] = ..., 
                system_data: Optional[SystemData] = ..., 
                **kwargs
            ): ...


    class azure.media.videoanalyzeredge.RemoteDeviceAdapterCollection(Model):
        continuation_token: str
        value: list[RemoteDeviceAdapter]

        def __init__(
                self, 
                *, 
                continuation_token: Optional[str] = ..., 
                value: Optional[List[RemoteDeviceAdapter]] = ..., 
                **kwargs
            ): ...


    class azure.media.videoanalyzeredge.RemoteDeviceAdapterDeleteRequest(MethodRequestEmptyBodyBase):
        api_version: str
        method_name: str
        name: str

        def __init__(
                self, 
                *, 
                api_version: Optional[str] = "1.1", 
                name: str, 
                **kwargs
            ): ...


    class azure.media.videoanalyzeredge.RemoteDeviceAdapterGetRequest(MethodRequestEmptyBodyBase):
        api_version: str
        method_name: str
        name: str

        def __init__(
                self, 
                *, 
                api_version: Optional[str] = "1.1", 
                name: str, 
                **kwargs
            ): ...


    class azure.media.videoanalyzeredge.RemoteDeviceAdapterListRequest(MethodRequest):
        api_version: str
        method_name: str

        def __init__(
                self, 
                *, 
                api_version: Optional[str] = "1.1", 
                **kwargs
            ): ...


    class azure.media.videoanalyzeredge.RemoteDeviceAdapterProperties(Model):
        description: str
        iot_hub_device_connection: IotHubDeviceConnection
        target: RemoteDeviceAdapterTarget

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                iot_hub_device_connection: IotHubDeviceConnection, 
                target: RemoteDeviceAdapterTarget, 
                **kwargs
            ): ...


    class azure.media.videoanalyzeredge.RemoteDeviceAdapterSetRequest(MethodRequest):
        api_version: str
        method_name: str
        remote_device_adapter: RemoteDeviceAdapter

        def __init__(
                self, 
                *, 
                api_version: Optional[str] = "1.1", 
                remote_device_adapter: RemoteDeviceAdapter, 
                **kwargs
            ): ...

        def _OverrideRemoteDeviceAdapterSetRequestSerialize(self): ...


    class azure.media.videoanalyzeredge.RemoteDeviceAdapterSetRequestBody(RemoteDeviceAdapter, MethodRequest):
        api_version: str
        method_name: str
        name: str
        properties: RemoteDeviceAdapterProperties
        system_data: SystemData

        def __init__(
                self, 
                *, 
                api_version: Optional[str] = "1.1", 
                name: str, 
                properties: Optional[RemoteDeviceAdapterProperties] = ..., 
                system_data: Optional[SystemData] = ..., 
                **kwargs
            ): ...


    class azure.media.videoanalyzeredge.RemoteDeviceAdapterTarget(Model):
        host: str

        def __init__(
                self, 
                *, 
                host: str, 
                **kwargs
            ): ...


    class azure.media.videoanalyzeredge.RtspSource(SourceNodeBase):
        endpoint: EndpointBase
        name: str
        transport: Union[str, RtspTransport]
        type: str

        def __init__(
                self, 
                *, 
                endpoint: EndpointBase, 
                name: str, 
                transport: Optional[Union[str, RtspTransport]] = ..., 
                **kwargs
            ): ...


    class azure.media.videoanalyzeredge.RtspTransport(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HTTP = "http"
        TCP = "tcp"


    class azure.media.videoanalyzeredge.SamplingOptions(Model):
        maximum_samples_per_second: str
        skip_samples_without_annotation: str

        def __init__(
                self, 
                *, 
                maximum_samples_per_second: Optional[str] = ..., 
                skip_samples_without_annotation: Optional[str] = ..., 
                **kwargs
            ): ...


    class azure.media.videoanalyzeredge.SignalGateProcessor(ProcessorNodeBase):
        activation_evaluation_window: str
        activation_signal_offset: str
        inputs: list[NodeInput]
        maximum_activation_time: str
        minimum_activation_time: str
        name: str
        type: str

        def __init__(
                self, 
                *, 
                activation_evaluation_window: Optional[str] = ..., 
                activation_signal_offset: Optional[str] = ..., 
                inputs: List[NodeInput], 
                maximum_activation_time: Optional[str] = ..., 
                minimum_activation_time: Optional[str] = ..., 
                name: str, 
                **kwargs
            ): ...


    class azure.media.videoanalyzeredge.SinkNodeBase(Model):
        inputs: list[NodeInput]
        name: str
        type: str

        def __init__(
                self, 
                *, 
                inputs: List[NodeInput], 
                name: str, 
                **kwargs
            ): ...


    class azure.media.videoanalyzeredge.SourceNodeBase(Model):
        name: str
        type: str

        def __init__(
                self, 
                *, 
                name: str, 
                **kwargs
            ): ...


    class azure.media.videoanalyzeredge.SpatialAnalysisCustomOperation(SpatialAnalysisOperationBase):
        extension_configuration: str
        type: str

        def __init__(
                self, 
                *, 
                extension_configuration: str, 
                **kwargs
            ): ...


    class azure.media.videoanalyzeredge.SpatialAnalysisOperationBase(Model):
        type: str

        def __init__(self, **kwargs): ...


    class azure.media.videoanalyzeredge.SpatialAnalysisOperationEventBase(Model):
        focus: Union[str, SpatialAnalysisOperationFocus]
        threshold: str

        def __init__(
                self, 
                *, 
                focus: Optional[Union[str, SpatialAnalysisOperationFocus]] = ..., 
                threshold: Optional[str] = ..., 
                **kwargs
            ): ...


    class azure.media.videoanalyzeredge.SpatialAnalysisOperationFocus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BOTTOM_CENTER = "bottomCenter"
        CENTER = "center"
        FOOTPRINT = "footprint"


    class azure.media.videoanalyzeredge.SpatialAnalysisPersonCountEvent(SpatialAnalysisOperationEventBase):
        focus: Union[str, SpatialAnalysisOperationFocus]
        output_frequency: str
        threshold: str
        trigger: Union[str, SpatialAnalysisPersonCountEventTrigger]

        def __init__(
                self, 
                *, 
                focus: Optional[Union[str, SpatialAnalysisOperationFocus]] = ..., 
                output_frequency: Optional[str] = ..., 
                threshold: Optional[str] = ..., 
                trigger: Optional[Union[str, SpatialAnalysisPersonCountEventTrigger]] = ..., 
                **kwargs
            ): ...


    class azure.media.videoanalyzeredge.SpatialAnalysisPersonCountEventTrigger(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EVENT = "event"
        INTERVAL = "interval"


    class azure.media.videoanalyzeredge.SpatialAnalysisPersonCountOperation(SpatialAnalysisTypedOperationBase):
        calibration_configuration: str
        camera_calibrator_node_configuration: str
        camera_configuration: str
        debug: str
        detector_node_configuration: str
        enable_face_mask_classifier: str
        tracker_node_configuration: str
        type: str
        zones: list[SpatialAnalysisPersonCountZoneEvents]

        def __init__(
                self, 
                *, 
                calibration_configuration: Optional[str] = ..., 
                camera_calibrator_node_configuration: Optional[str] = ..., 
                camera_configuration: Optional[str] = ..., 
                debug: Optional[str] = ..., 
                detector_node_configuration: Optional[str] = ..., 
                enable_face_mask_classifier: Optional[str] = ..., 
                tracker_node_configuration: Optional[str] = ..., 
                zones: List[SpatialAnalysisPersonCountZoneEvents], 
                **kwargs
            ): ...


    class azure.media.videoanalyzeredge.SpatialAnalysisPersonCountZoneEvents(Model):
        events: list[SpatialAnalysisPersonCountEvent]
        zone: NamedPolygonBase

        def __init__(
                self, 
                *, 
                events: Optional[List[SpatialAnalysisPersonCountEvent]] = ..., 
                zone: NamedPolygonBase, 
                **kwargs
            ): ...


    class azure.media.videoanalyzeredge.SpatialAnalysisPersonDistanceEvent(SpatialAnalysisOperationEventBase):
        focus: Union[str, SpatialAnalysisOperationFocus]
        maximum_distance_threshold: str
        minimum_distance_threshold: str
        output_frequency: str
        threshold: str
        trigger: Union[str, SpatialAnalysisPersonDistanceEventTrigger]

        def __init__(
                self, 
                *, 
                focus: Optional[Union[str, SpatialAnalysisOperationFocus]] = ..., 
                maximum_distance_threshold: Optional[str] = ..., 
                minimum_distance_threshold: Optional[str] = ..., 
                output_frequency: Optional[str] = ..., 
                threshold: Optional[str] = ..., 
                trigger: Optional[Union[str, SpatialAnalysisPersonDistanceEventTrigger]] = ..., 
                **kwargs
            ): ...


    class azure.media.videoanalyzeredge.SpatialAnalysisPersonDistanceEventTrigger(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EVENT = "event"
        INTERVAL = "interval"


    class azure.media.videoanalyzeredge.SpatialAnalysisPersonDistanceOperation(SpatialAnalysisTypedOperationBase):
        calibration_configuration: str
        camera_calibrator_node_configuration: str
        camera_configuration: str
        debug: str
        detector_node_configuration: str
        enable_face_mask_classifier: str
        tracker_node_configuration: str
        type: str
        zones: list[SpatialAnalysisPersonDistanceZoneEvents]

        def __init__(
                self, 
                *, 
                calibration_configuration: Optional[str] = ..., 
                camera_calibrator_node_configuration: Optional[str] = ..., 
                camera_configuration: Optional[str] = ..., 
                debug: Optional[str] = ..., 
                detector_node_configuration: Optional[str] = ..., 
                enable_face_mask_classifier: Optional[str] = ..., 
                tracker_node_configuration: Optional[str] = ..., 
                zones: List[SpatialAnalysisPersonDistanceZoneEvents], 
                **kwargs
            ): ...


    class azure.media.videoanalyzeredge.SpatialAnalysisPersonDistanceZoneEvents(Model):
        events: list[SpatialAnalysisPersonDistanceEvent]
        zone: NamedPolygonBase

        def __init__(
                self, 
                *, 
                events: Optional[List[SpatialAnalysisPersonDistanceEvent]] = ..., 
                zone: NamedPolygonBase, 
                **kwargs
            ): ...


    class azure.media.videoanalyzeredge.SpatialAnalysisPersonLineCrossingEvent(SpatialAnalysisOperationEventBase):
        focus: Union[str, SpatialAnalysisOperationFocus]
        threshold: str

        def __init__(
                self, 
                *, 
                focus: Optional[Union[str, SpatialAnalysisOperationFocus]] = ..., 
                threshold: Optional[str] = ..., 
                **kwargs
            ): ...


    class azure.media.videoanalyzeredge.SpatialAnalysisPersonLineCrossingLineEvents(Model):
        events: list[SpatialAnalysisPersonLineCrossingEvent]
        line: NamedLineBase

        def __init__(
                self, 
                *, 
                events: Optional[List[SpatialAnalysisPersonLineCrossingEvent]] = ..., 
                line: NamedLineBase, 
                **kwargs
            ): ...


    class azure.media.videoanalyzeredge.SpatialAnalysisPersonLineCrossingOperation(SpatialAnalysisTypedOperationBase):
        calibration_configuration: str
        camera_calibrator_node_configuration: str
        camera_configuration: str
        debug: str
        detector_node_configuration: str
        enable_face_mask_classifier: str
        lines: list[SpatialAnalysisPersonLineCrossingLineEvents]
        tracker_node_configuration: str
        type: str

        def __init__(
                self, 
                *, 
                calibration_configuration: Optional[str] = ..., 
                camera_calibrator_node_configuration: Optional[str] = ..., 
                camera_configuration: Optional[str] = ..., 
                debug: Optional[str] = ..., 
                detector_node_configuration: Optional[str] = ..., 
                enable_face_mask_classifier: Optional[str] = ..., 
                lines: List[SpatialAnalysisPersonLineCrossingLineEvents], 
                tracker_node_configuration: Optional[str] = ..., 
                **kwargs
            ): ...


    class azure.media.videoanalyzeredge.SpatialAnalysisPersonZoneCrossingEvent(SpatialAnalysisOperationEventBase):
        event_type: Union[str, SpatialAnalysisPersonZoneCrossingEventType]
        focus: Union[str, SpatialAnalysisOperationFocus]
        threshold: str

        def __init__(
                self, 
                *, 
                event_type: Optional[Union[str, SpatialAnalysisPersonZoneCrossingEventType]] = ..., 
                focus: Optional[Union[str, SpatialAnalysisOperationFocus]] = ..., 
                threshold: Optional[str] = ..., 
                **kwargs
            ): ...


    class azure.media.videoanalyzeredge.SpatialAnalysisPersonZoneCrossingEventType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ZONE_CROSSING = "zoneCrossing"
        ZONE_DWELL_TIME = "zoneDwellTime"


    class azure.media.videoanalyzeredge.SpatialAnalysisPersonZoneCrossingOperation(SpatialAnalysisTypedOperationBase):
        calibration_configuration: str
        camera_calibrator_node_configuration: str
        camera_configuration: str
        debug: str
        detector_node_configuration: str
        enable_face_mask_classifier: str
        tracker_node_configuration: str
        type: str
        zones: list[SpatialAnalysisPersonZoneCrossingZoneEvents]

        def __init__(
                self, 
                *, 
                calibration_configuration: Optional[str] = ..., 
                camera_calibrator_node_configuration: Optional[str] = ..., 
                camera_configuration: Optional[str] = ..., 
                debug: Optional[str] = ..., 
                detector_node_configuration: Optional[str] = ..., 
                enable_face_mask_classifier: Optional[str] = ..., 
                tracker_node_configuration: Optional[str] = ..., 
                zones: List[SpatialAnalysisPersonZoneCrossingZoneEvents], 
                **kwargs
            ): ...


    class azure.media.videoanalyzeredge.SpatialAnalysisPersonZoneCrossingZoneEvents(Model):
        events: list[SpatialAnalysisPersonZoneCrossingEvent]
        zone: NamedPolygonBase

        def __init__(
                self, 
                *, 
                events: Optional[List[SpatialAnalysisPersonZoneCrossingEvent]] = ..., 
                zone: NamedPolygonBase, 
                **kwargs
            ): ...


    class azure.media.videoanalyzeredge.SpatialAnalysisTypedOperationBase(SpatialAnalysisOperationBase):
        calibration_configuration: str
        camera_calibrator_node_configuration: str
        camera_configuration: str
        debug: str
        detector_node_configuration: str
        enable_face_mask_classifier: str
        tracker_node_configuration: str
        type: str

        def __init__(
                self, 
                *, 
                calibration_configuration: Optional[str] = ..., 
                camera_calibrator_node_configuration: Optional[str] = ..., 
                camera_configuration: Optional[str] = ..., 
                debug: Optional[str] = ..., 
                detector_node_configuration: Optional[str] = ..., 
                enable_face_mask_classifier: Optional[str] = ..., 
                tracker_node_configuration: Optional[str] = ..., 
                **kwargs
            ): ...


    class azure.media.videoanalyzeredge.SymmetricKeyCredentials(CredentialsBase):
        key: str
        type: str

        def __init__(
                self, 
                *, 
                key: str, 
                **kwargs
            ): ...


    class azure.media.videoanalyzeredge.SystemData(Model):
        created_at: datetime
        last_modified_at: datetime

        def __init__(
                self, 
                *, 
                created_at: Optional[datetime] = ..., 
                last_modified_at: Optional[datetime] = ..., 
                **kwargs
            ): ...


    class azure.media.videoanalyzeredge.TlsEndpoint(EndpointBase):
        credentials: CredentialsBase
        trusted_certificates: CertificateSource
        type: str
        url: str
        validation_options: TlsValidationOptions

        def __init__(
                self, 
                *, 
                credentials: Optional[CredentialsBase] = ..., 
                trusted_certificates: Optional[CertificateSource] = ..., 
                url: str, 
                validation_options: Optional[TlsValidationOptions] = ..., 
                **kwargs
            ): ...


    class azure.media.videoanalyzeredge.TlsValidationOptions(Model):
        ignore_hostname: str
        ignore_signature: str

        def __init__(
                self, 
                *, 
                ignore_hostname: Optional[str] = ..., 
                ignore_signature: Optional[str] = ..., 
                **kwargs
            ): ...


    class azure.media.videoanalyzeredge.UnsecuredEndpoint(EndpointBase):
        credentials: CredentialsBase
        type: str
        url: str

        def __init__(
                self, 
                *, 
                credentials: Optional[CredentialsBase] = ..., 
                url: str, 
                **kwargs
            ): ...


    class azure.media.videoanalyzeredge.UsernamePasswordCredentials(CredentialsBase):
        password: str
        type: str
        username: str

        def __init__(
                self, 
                *, 
                password: str, 
                username: str, 
                **kwargs
            ): ...


    class azure.media.videoanalyzeredge.VideoCreationProperties(Model):
        description: str
        retention_period: str
        segment_length: str
        title: str

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                retention_period: Optional[str] = ..., 
                segment_length: Optional[str] = ..., 
                title: Optional[str] = ..., 
                **kwargs
            ): ...


    class azure.media.videoanalyzeredge.VideoEncoderConfiguration(Model):
        encoding: Union[str, VideoEncoding]
        h264: H264Configuration
        mpeg4: MPEG4Configuration
        quality: float
        rate_control: RateControl
        resolution: VideoResolution

        def __init__(
                self, 
                *, 
                encoding: Optional[Union[str, VideoEncoding]] = ..., 
                h264: Optional[H264Configuration] = ..., 
                mpeg4: Optional[MPEG4Configuration] = ..., 
                quality: Optional[float] = ..., 
                rate_control: Optional[RateControl] = ..., 
                resolution: Optional[VideoResolution] = ..., 
                **kwargs
            ): ...


    class azure.media.videoanalyzeredge.VideoEncoding(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        H264 = "H264"
        JPEG = "JPEG"
        MPEG4 = "MPEG4"


    class azure.media.videoanalyzeredge.VideoPublishingOptions(Model):
        enable_video_preview_image: str

        def __init__(
                self, 
                *, 
                enable_video_preview_image: Optional[str] = ..., 
                **kwargs
            ): ...


    class azure.media.videoanalyzeredge.VideoResolution(Model):
        height: float
        width: float

        def __init__(
                self, 
                *, 
                height: Optional[float] = ..., 
                width: Optional[float] = ..., 
                **kwargs
            ): ...


    class azure.media.videoanalyzeredge.VideoSink(SinkNodeBase):
        inputs: list[NodeInput]
        local_media_cache_maximum_size_mi_b: str
        local_media_cache_path: str
        name: str
        type: str
        video_creation_properties: VideoCreationProperties
        video_name: str
        video_publishing_options: VideoPublishingOptions

        def __init__(
                self, 
                *, 
                inputs: List[NodeInput], 
                local_media_cache_maximum_size_mi_b: str, 
                local_media_cache_path: str, 
                name: str, 
                video_creation_properties: Optional[VideoCreationProperties] = ..., 
                video_name: str, 
                video_publishing_options: Optional[VideoPublishingOptions] = ..., 
                **kwargs
            ): ...


```