```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.communication.jobrouter

    class azure.communication.jobrouter.JobRouterAdministrationClient(JobRouterAdministrationClientGenerated): implements ContextManager 

        def __init__(
                self, 
                endpoint: str, 
                credential: AzureKeyCredential, 
                *, 
                api_version: str = ..., 
                **kwargs: Any
            ) -> None: ...

        @classmethod
        def from_connection_string(
                cls, 
                conn_str: str, 
                **kwargs: Any
            ) -> JobRouterAdministrationClient: ...

        def close(self) -> None: ...

        @distributed_trace
        def delete_classification_policy(
                self, 
                classification_policy_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def delete_distribution_policy(
                self, 
                distribution_policy_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def delete_exception_policy(
                self, 
                exception_policy_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def delete_queue(
                self, 
                queue_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get_classification_policy(
                self, 
                classification_policy_id: str, 
                **kwargs: Any
            ) -> ClassificationPolicy: ...

        @distributed_trace
        def get_distribution_policy(
                self, 
                distribution_policy_id: str, 
                **kwargs: Any
            ) -> DistributionPolicy: ...

        @distributed_trace
        def get_exception_policy(
                self, 
                exception_policy_id: str, 
                **kwargs: Any
            ) -> ExceptionPolicy: ...

        @distributed_trace
        def get_queue(
                self, 
                queue_id: str, 
                **kwargs: Any
            ) -> RouterQueue: ...

        @distributed_trace
        def list_classification_policies(
                self, 
                *, 
                results_per_page: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[ClassificationPolicy]: ...

        @distributed_trace
        def list_distribution_policies(
                self, 
                *, 
                results_per_page: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[DistributionPolicy]: ...

        @distributed_trace
        def list_exception_policies(
                self, 
                *, 
                results_per_page: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[ExceptionPolicy]: ...

        @distributed_trace
        def list_queues(
                self, 
                *, 
                results_per_page: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[RouterQueue]: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> HttpResponse: ...

        @overload
        def upsert_classification_policy(
                self, 
                classification_policy_id: str, 
                *, 
                etag: Optional[str] = ..., 
                fallback_queue_id: Optional[str], 
                if_unmodified_since: Optional[datetime] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                name: Optional[str], 
                prioritization_rule: Optional[Union[StaticRouterRule, ExpressionRouterRule, FunctionRouterRule, WebhookRouterRule]], 
                queue_selectors: Optional[List[Union[StaticQueueSelectorAttachment, ConditionalQueueSelectorAttachment, RuleEngineQueueSelectorAttachment, PassThroughQueueSelectorAttachment, WeightedAllocationQueueSelectorAttachment]]], 
                worker_selectors: Optional[List[Union[StaticWorkerSelectorAttachment, ConditionalWorkerSelectorAttachment, RuleEngineWorkerSelectorAttachment, PassThroughWorkerSelectorAttachment, WeightedAllocationWorkerSelectorAttachment]]], 
                **kwargs: Any
            ) -> ClassificationPolicy: ...

        @overload
        def upsert_classification_policy(
                self, 
                classification_policy_id: str, 
                resource: ClassificationPolicy, 
                *, 
                content_type: str = "application/merge-patch+json", 
                etag: Optional[str] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> ClassificationPolicy: ...

        @overload
        def upsert_classification_policy(
                self, 
                classification_policy_id: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/merge-patch+json", 
                etag: Optional[str] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> ClassificationPolicy: ...

        @overload
        def upsert_classification_policy(
                self, 
                classification_policy_id: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/merge-patch+json", 
                etag: Optional[str] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> ClassificationPolicy: ...

        @overload
        def upsert_distribution_policy(
                self, 
                distribution_policy_id: str, 
                *, 
                etag: Optional[str] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                mode: Optional[Union[BestWorkerMode, LongestIdleMode, RoundRobinMode]] = ..., 
                name: Optional[str] = ..., 
                offer_expires_after_seconds: Optional[float] = ..., 
                **kwargs: Any
            ) -> DistributionPolicy: ...

        @overload
        def upsert_distribution_policy(
                self, 
                distribution_policy_id: str, 
                resource: DistributionPolicy, 
                *, 
                content_type: str = "application/merge-patch+json", 
                etag: Optional[str] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> DistributionPolicy: ...

        @overload
        def upsert_distribution_policy(
                self, 
                distribution_policy_id: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/merge-patch+json", 
                etag: Optional[str] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> DistributionPolicy: ...

        @overload
        def upsert_distribution_policy(
                self, 
                distribution_policy_id: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/merge-patch+json", 
                etag: Optional[str] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> DistributionPolicy: ...

        @overload
        def upsert_exception_policy(
                self, 
                exception_policy_id: str, 
                *, 
                etag: Optional[str] = ..., 
                exception_rules: Optional[List[ExceptionRule]], 
                if_unmodified_since: Optional[datetime] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                name: Optional[str], 
                **kwargs: Any
            ) -> ExceptionPolicy: ...

        @overload
        def upsert_exception_policy(
                self, 
                exception_policy_id: str, 
                resource: ExceptionPolicy, 
                *, 
                content_type: str = "application/merge-patch+json", 
                etag: Optional[str] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> ExceptionPolicy: ...

        @overload
        def upsert_exception_policy(
                self, 
                exception_policy_id: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/merge-patch+json", 
                etag: Optional[str] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> ExceptionPolicy: ...

        @overload
        def upsert_exception_policy(
                self, 
                exception_policy_id: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/merge-patch+json", 
                etag: Optional[str] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> ExceptionPolicy: ...

        @overload
        def upsert_queue(
                self, 
                queue_id: str, 
                *, 
                distribution_policy_id: Optional[str], 
                etag: Optional[str] = ..., 
                exception_policy_id: Optional[str], 
                if_unmodified_since: Optional[datetime] = ..., 
                labels: Optional[Dict[str, Union[int, float, str, bool]]], 
                match_condition: Optional[MatchConditions] = ..., 
                name: Optional[str], 
                **kwargs: Any
            ) -> RouterQueue: ...

        @overload
        def upsert_queue(
                self, 
                queue_id: str, 
                resource: RouterQueue, 
                *, 
                content_type: str = "application/merge-patch+json", 
                etag: Optional[str] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> RouterQueue: ...

        @overload
        def upsert_queue(
                self, 
                queue_id: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/merge-patch+json", 
                etag: Optional[str] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> RouterQueue: ...

        @overload
        def upsert_queue(
                self, 
                queue_id: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/merge-patch+json", 
                etag: Optional[str] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> RouterQueue: ...


    class azure.communication.jobrouter.JobRouterClient(JobRouterClientGenerated): implements ContextManager 

        def __init__(
                self, 
                endpoint: str, 
                credential: AzureKeyCredential, 
                *, 
                api_version = ..., 
                **kwargs: Any
            ) -> None: ...

        @classmethod
        def from_connection_string(
                cls, 
                conn_str: str, 
                **kwargs: Any
            ) -> JobRouterClient: ...

        @distributed_trace
        def accept_job_offer(
                self, 
                worker_id: str, 
                offer_id: str, 
                **kwargs: Any
            ) -> AcceptJobOfferResult: ...

        @distributed_trace
        def cancel_job(
                self, 
                job_id: str, 
                options: Optional[Union[CancelJobOptions, JSON, IO]] = None, 
                **kwargs: Any
            ) -> None: ...

        def close(self) -> None: ...

        @distributed_trace
        def close_job(
                self, 
                job_id: str, 
                assignment_id: str, 
                options: Optional[Union[CloseJobOptions, JSON, IO]] = None, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def complete_job(
                self, 
                job_id: str, 
                assignment_id: str, 
                options: Optional[Union[CompleteJobOptions, JSON, IO]] = None, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def decline_job_offer(
                self, 
                worker_id: str, 
                offer_id: str, 
                options: Optional[Union[DeclineJobOfferOptions, JSON, IO]] = None, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def delete_job(
                self, 
                job_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def delete_worker(
                self, 
                worker_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get_job(
                self, 
                job_id: str, 
                **kwargs: Any
            ) -> RouterJob: ...

        @distributed_trace
        def get_queue_position(
                self, 
                job_id: str, 
                **kwargs: Any
            ) -> RouterJobPositionDetails: ...

        @distributed_trace
        def get_queue_statistics(
                self, 
                queue_id: str, 
                **kwargs: Any
            ) -> RouterQueueStatistics: ...

        @distributed_trace
        def get_worker(
                self, 
                worker_id: str, 
                **kwargs: Any
            ) -> RouterWorker: ...

        @distributed_trace
        def list_jobs(
                self, 
                *, 
                channel_id: Optional[str] = ..., 
                classification_policy_id: Optional[str] = ..., 
                queue_id: Optional[str] = ..., 
                results_per_page: Optional[int] = ..., 
                scheduled_after: Optional[Union[str, datetime]] = ..., 
                scheduled_before: Optional[Union[str, datetime]] = ..., 
                status: Optional[Union[str, RouterJobStatus, Literal[all, active]]] = "all", 
                **kwargs: Any
            ) -> ItemPaged[RouterJob]: ...

        @distributed_trace
        def list_workers(
                self, 
                *, 
                channel_id: Optional[str] = ..., 
                has_capacity: Optional[bool] = ..., 
                queue_id: Optional[str] = ..., 
                results_per_page: Optional[int] = ..., 
                state: Optional[Union[str, RouterWorkerState, Literal[all]]] = "all", 
                **kwargs: Any
            ) -> ItemPaged[RouterWorker]: ...

        @distributed_trace
        def reclassify_job(
                self, 
                job_id: str, 
                **kwargs: Any
            ) -> None: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> HttpResponse: ...

        @overload
        def unassign_job(
                self, 
                job_id: str, 
                assignment_id: str, 
                options: Optional[UnassignJobOptions] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> UnassignJobResult: ...

        @overload
        def unassign_job(
                self, 
                job_id: str, 
                assignment_id: str, 
                options: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> UnassignJobResult: ...

        @overload
        def unassign_job(
                self, 
                job_id: str, 
                assignment_id: str, 
                options: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> UnassignJobResult: ...

        @overload
        def upsert_job(
                self, 
                job_id: str, 
                *, 
                channel_id: Optional[str], 
                channel_reference: Optional[str], 
                classification_policy_id: Optional[str], 
                disposition_code: Optional[str], 
                etag: Optional[str] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                labels: Optional[Dict[str, Union[int, float, str, bool, None]]], 
                match_condition: Optional[MatchConditions] = ..., 
                matching_mode: Optional[JobMatchingMode], 
                notes: Optional[Dict[datetime, str]], 
                priority: Optional[int], 
                queue_id: Optional[str], 
                requested_worker_selectors: Optional[List[RouterWorkerSelector]], 
                tags: Optional[Dict[str, Union[int, float, str, bool, None]]], 
                **kwargs: Any
            ) -> RouterJob: ...

        @overload
        def upsert_job(
                self, 
                job_id: str, 
                resource: RouterJob, 
                *, 
                content_type: str = "application/merge-patch+json", 
                etag: Optional[str] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> RouterJob: ...

        @overload
        def upsert_job(
                self, 
                job_id: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/merge-patch+json", 
                etag: Optional[str] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> RouterJob: ...

        @overload
        def upsert_job(
                self, 
                job_id: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/merge-patch+json", 
                etag: Optional[str] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> RouterJob: ...

        @overload
        def upsert_worker(
                self, 
                worker_id: str, 
                *, 
                available_for_offers: Optional[bool], 
                capacity: Optional[int], 
                channels: Optional[List[RouterChannel]], 
                etag: Optional[str] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                labels: Optional[Dict[str, Union[int, float, str, bool]]], 
                match_condition: Optional[MatchConditions] = ..., 
                max_concurrent_offers: Optional[int], 
                queues: Optional[List[str]], 
                tags: Optional[Dict[str, Union[int, float, str, bool]]], 
                **kwargs: Any
            ) -> RouterWorker: ...

        @overload
        def upsert_worker(
                self, 
                worker_id: str, 
                resource: RouterWorker, 
                *, 
                content_type: str = "application/merge-patch+json", 
                etag: Optional[str] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> RouterWorker: ...

        @overload
        def upsert_worker(
                self, 
                worker_id: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/merge-patch+json", 
                etag: Optional[str] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> RouterWorker: ...

        @overload
        def upsert_worker(
                self, 
                worker_id: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/merge-patch+json", 
                etag: Optional[str] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> RouterWorker: ...


namespace azure.communication.jobrouter.aio

    class azure.communication.jobrouter.aio.JobRouterAdministrationClient(JobRouterAdministrationClientGenerated): implements AsyncContextManager 

        def __init__(
                self, 
                endpoint: str, 
                credential: AzureKeyCredential, 
                *, 
                api_version: str = ..., 
                **kwargs: Any
            ) -> None: ...

        @classmethod
        def from_connection_string(
                cls, 
                conn_str: str, 
                **kwargs: Any
            ) -> JobRouterAdministrationClient: ...

        async def close(self) -> None: ...

        @distributed_trace_async
        async def delete_classification_policy(
                self, 
                classification_policy_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def delete_distribution_policy(
                self, 
                distribution_policy_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def delete_exception_policy(
                self, 
                exception_policy_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def delete_queue(
                self, 
                queue_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get_classification_policy(
                self, 
                classification_policy_id: str, 
                **kwargs: Any
            ) -> ClassificationPolicy: ...

        @distributed_trace_async
        async def get_distribution_policy(
                self, 
                distribution_policy_id: str, 
                **kwargs: Any
            ) -> DistributionPolicy: ...

        @distributed_trace_async
        async def get_exception_policy(
                self, 
                exception_policy_id: str, 
                **kwargs: Any
            ) -> ExceptionPolicy: ...

        @distributed_trace_async
        async def get_queue(
                self, 
                queue_id: str, 
                **kwargs: Any
            ) -> RouterQueue: ...

        @distributed_trace
        def list_classification_policies(
                self, 
                *, 
                results_per_page: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[ClassificationPolicy]: ...

        @distributed_trace
        def list_distribution_policies(
                self, 
                *, 
                results_per_page: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[DistributionPolicy]: ...

        @distributed_trace
        def list_exception_policies(
                self, 
                *, 
                results_per_page: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[ExceptionPolicy]: ...

        @distributed_trace
        def list_queues(
                self, 
                *, 
                results_per_page: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[RouterQueue]: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> Awaitable[AsyncHttpResponse]: ...

        @overload
        async def upsert_classification_policy(
                self, 
                classification_policy_id: str, 
                *, 
                etag: Optional[str] = ..., 
                fallback_queue_id: Optional[str], 
                if_unmodified_since: Optional[datetime] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                name: Optional[str], 
                prioritization_rule: Optional[Union[StaticRouterRule, ExpressionRouterRule, FunctionRouterRule, WebhookRouterRule]], 
                queue_selectors: Optional[List[Union[StaticQueueSelectorAttachment, ConditionalQueueSelectorAttachment, RuleEngineQueueSelectorAttachment, PassThroughQueueSelectorAttachment, WeightedAllocationQueueSelectorAttachment]]], 
                worker_selectors: Optional[List[Union[StaticWorkerSelectorAttachment, ConditionalWorkerSelectorAttachment, RuleEngineWorkerSelectorAttachment, PassThroughWorkerSelectorAttachment, WeightedAllocationWorkerSelectorAttachment]]], 
                **kwargs: Any
            ) -> ClassificationPolicy: ...

        @overload
        async def upsert_classification_policy(
                self, 
                classification_policy_id: str, 
                resource: ClassificationPolicy, 
                *, 
                content_type: str = "application/merge-patch+json", 
                etag: Optional[str] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> ClassificationPolicy: ...

        @overload
        async def upsert_classification_policy(
                self, 
                classification_policy_id: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/merge-patch+json", 
                etag: Optional[str] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> ClassificationPolicy: ...

        @overload
        async def upsert_classification_policy(
                self, 
                classification_policy_id: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/merge-patch+json", 
                etag: Optional[str] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> ClassificationPolicy: ...

        @overload
        async def upsert_distribution_policy(
                self, 
                distribution_policy_id: str, 
                *, 
                etag: Optional[str] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                mode: Optional[Union[BestWorkerMode, LongestIdleMode, RoundRobinMode]], 
                name: Optional[str], 
                offer_expires_after_seconds: Optional[float], 
                **kwargs: Any
            ) -> DistributionPolicy: ...

        @overload
        async def upsert_distribution_policy(
                self, 
                distribution_policy_id: str, 
                resource: DistributionPolicy, 
                *, 
                content_type: str = "application/merge-patch+json", 
                etag: Optional[str] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> DistributionPolicy: ...

        @overload
        async def upsert_distribution_policy(
                self, 
                distribution_policy_id: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/merge-patch+json", 
                etag: Optional[str] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> DistributionPolicy: ...

        @overload
        async def upsert_distribution_policy(
                self, 
                distribution_policy_id: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/merge-patch+json", 
                etag: Optional[str] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> DistributionPolicy: ...

        @overload
        async def upsert_exception_policy(
                self, 
                exception_policy_id: str, 
                *, 
                etag: Optional[str] = ..., 
                exception_rules: Optional[List[ExceptionRule]], 
                if_unmodified_since: Optional[datetime] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                name: Optional[str], 
                **kwargs: Any
            ) -> ExceptionPolicy: ...

        @overload
        async def upsert_exception_policy(
                self, 
                exception_policy_id: str, 
                resource: ExceptionPolicy, 
                *, 
                content_type: str = "application/merge-patch+json", 
                etag: Optional[str] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> ExceptionPolicy: ...

        @overload
        async def upsert_exception_policy(
                self, 
                exception_policy_id: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/merge-patch+json", 
                etag: Optional[str] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> ExceptionPolicy: ...

        @overload
        async def upsert_exception_policy(
                self, 
                exception_policy_id: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/merge-patch+json", 
                etag: Optional[str] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> ExceptionPolicy: ...

        @overload
        async def upsert_queue(
                self, 
                queue_id: str, 
                *, 
                distribution_policy_id: Optional[str], 
                etag: Optional[str] = ..., 
                exception_policy_id: Optional[str], 
                if_unmodified_since: Optional[datetime] = ..., 
                labels: Optional[Dict[str, Union[int, float, str, bool]]], 
                match_condition: Optional[MatchConditions] = ..., 
                name: Optional[str], 
                **kwargs: Any
            ) -> RouterQueue: ...

        @overload
        async def upsert_queue(
                self, 
                queue_id: str, 
                resource: RouterQueue, 
                *, 
                content_type: str = "application/merge-patch+json", 
                etag: Optional[str] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> RouterQueue: ...

        @overload
        async def upsert_queue(
                self, 
                queue_id: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/merge-patch+json", 
                etag: Optional[str] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> RouterQueue: ...

        @overload
        async def upsert_queue(
                self, 
                queue_id: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/merge-patch+json", 
                etag: Optional[str] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> RouterQueue: ...


    class azure.communication.jobrouter.aio.JobRouterClient(JobRouterClientGenerated): implements AsyncContextManager 

        def __init__(
                self, 
                endpoint: str, 
                credential: AzureKeyCredential, 
                *, 
                api_version = ..., 
                **kwargs: Any
            ) -> None: ...

        @classmethod
        def from_connection_string(
                cls, 
                conn_str: str, 
                **kwargs: Any
            ) -> JobRouterClient: ...

        @distributed_trace_async
        async def accept_job_offer(
                self, 
                worker_id: str, 
                offer_id: str, 
                **kwargs: Any
            ) -> AcceptJobOfferResult: ...

        @distributed_trace_async
        async def cancel_job(
                self, 
                job_id: str, 
                options: Optional[Union[CancelJobOptions, JSON, IO]] = None, 
                **kwargs: Any
            ) -> None: ...

        async def close(self) -> None: ...

        @distributed_trace_async
        async def close_job(
                self, 
                job_id: str, 
                assignment_id: str, 
                options: Optional[Union[CloseJobOptions, JSON, IO]] = None, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def complete_job(
                self, 
                job_id: str, 
                assignment_id: str, 
                options: Optional[Union[CompleteJobOptions, JSON, IO]] = None, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def decline_job_offer(
                self, 
                worker_id: str, 
                offer_id: str, 
                options: Optional[Union[DeclineJobOfferOptions, JSON, IO]] = None, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def delete_job(
                self, 
                job_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def delete_worker(
                self, 
                worker_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get_job(
                self, 
                job_id: str, 
                **kwargs: Any
            ) -> RouterJob: ...

        @distributed_trace_async
        async def get_queue_position(
                self, 
                job_id: str, 
                **kwargs: Any
            ) -> RouterJobPositionDetails: ...

        @distributed_trace_async
        async def get_queue_statistics(
                self, 
                queue_id: str, 
                **kwargs: Any
            ) -> RouterQueueStatistics: ...

        @distributed_trace_async
        async def get_worker(
                self, 
                worker_id: str, 
                **kwargs: Any
            ) -> RouterWorker: ...

        @distributed_trace
        def list_jobs(
                self, 
                *, 
                channel_id: Optional[str] = ..., 
                classification_policy_id: Optional[str] = ..., 
                queue_id: Optional[str] = ..., 
                results_per_page: Optional[int] = ..., 
                scheduled_after: Optional[Union[str, datetime]] = ..., 
                scheduled_before: Optional[Union[str, datetime]] = ..., 
                status: Optional[Union[str, RouterJobStatus, Literal[all, active]]] = "all", 
                **kwargs: Any
            ) -> AsyncItemPaged[RouterJob]: ...

        @distributed_trace
        def list_workers(
                self, 
                *, 
                channel_id: Optional[str] = ..., 
                has_capacity: Optional[bool] = ..., 
                queue_id: Optional[str] = ..., 
                results_per_page: Optional[int] = ..., 
                state: Optional[Union[str, RouterWorkerState, Literal[all]]] = "all", 
                **kwargs: Any
            ) -> AsyncItemPaged[RouterWorker]: ...

        @distributed_trace_async
        async def reclassify_job(
                self, 
                job_id: str, 
                **kwargs: Any
            ) -> None: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> Awaitable[AsyncHttpResponse]: ...

        @overload
        async def unassign_job(
                self, 
                job_id: str, 
                assignment_id: str, 
                options: Optional[UnassignJobOptions] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> UnassignJobResult: ...

        @overload
        async def unassign_job(
                self, 
                job_id: str, 
                assignment_id: str, 
                options: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> UnassignJobResult: ...

        @overload
        async def unassign_job(
                self, 
                job_id: str, 
                assignment_id: str, 
                options: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> UnassignJobResult: ...

        @overload
        async def upsert_job(
                self, 
                job_id: str, 
                *, 
                channel_id: Optional[str], 
                channel_reference: Optional[str], 
                classification_policy_id: Optional[str], 
                disposition_code: Optional[str], 
                etag: Optional[str] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                labels: Optional[Dict[str, Union[int, float, str, bool, None]]], 
                match_condition: Optional[MatchConditions] = ..., 
                matching_mode: Optional[JobMatchingMode], 
                notes: Optional[Dict[datetime, str]], 
                priority: Optional[int], 
                queue_id: Optional[str], 
                requested_worker_selectors: Optional[List[RouterWorkerSelector]], 
                tags: Optional[Dict[str, Union[int, float, str, bool, None]]], 
                **kwargs: Any
            ) -> RouterJob: ...

        @overload
        async def upsert_job(
                self, 
                job_id: str, 
                resource: RouterJob, 
                *, 
                content_type: str = "application/merge-patch+json", 
                etag: Optional[str] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> RouterJob: ...

        @overload
        async def upsert_job(
                self, 
                job_id: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/merge-patch+json", 
                etag: Optional[str] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> RouterJob: ...

        @overload
        async def upsert_job(
                self, 
                job_id: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/merge-patch+json", 
                etag: Optional[str] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> RouterJob: ...

        @overload
        async def upsert_worker(
                self, 
                worker_id: str, 
                *, 
                available_for_offers: Optional[bool], 
                capacity: Optional[int], 
                channels: Optional[List[RouterChannel]], 
                etag: Optional[str] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                labels: Optional[Dict[str, Union[int, float, str, bool]]], 
                match_condition: Optional[MatchConditions] = ..., 
                max_concurrent_offers: Optional[int], 
                queues: Optional[List[str]], 
                tags: Optional[Dict[str, Union[int, float, str, bool]]], 
                **kwargs: Any
            ) -> RouterWorker: ...

        @overload
        async def upsert_worker(
                self, 
                worker_id: str, 
                resource: RouterWorker, 
                *, 
                content_type: str = "application/merge-patch+json", 
                etag: Optional[str] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> RouterWorker: ...

        @overload
        async def upsert_worker(
                self, 
                worker_id: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/merge-patch+json", 
                etag: Optional[str] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> RouterWorker: ...

        @overload
        async def upsert_worker(
                self, 
                worker_id: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/merge-patch+json", 
                etag: Optional[str] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> RouterWorker: ...


namespace azure.communication.jobrouter.models

    class azure.communication.jobrouter.models.AcceptJobOfferResult(Model):
        assignment_id: str
        job_id: str
        worker_id: str

        @overload
        def __init__(
                self, 
                *, 
                assignment_id: str, 
                job_id: str, 
                worker_id: str
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.communication.jobrouter.models.BestWorkerMode(DistributionMode, discriminator='bestWorker'):
        bypass_selectors: bool
        kind: Literal[DistributionModeKind.BEST_WORKER]
        max_concurrent_offers: int
        min_concurrent_offers: int
        scoring_rule: Optional[RouterRule]
        scoring_rule_options: Optional[ScoringRuleOptions]

        @overload
        def __init__(
                self, 
                *, 
                bypass_selectors: Optional[bool] = ..., 
                max_concurrent_offers: Optional[int] = ..., 
                min_concurrent_offers: Optional[int] = ..., 
                scoring_rule: Optional[RouterRule] = ..., 
                scoring_rule_options: Optional[ScoringRuleOptions] = ...
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.communication.jobrouter.models.CancelExceptionAction(ExceptionAction, discriminator='cancel'):
        disposition_code: Optional[str]
        id: str
        kind: Literal[ExceptionActionKind.CANCEL]
        note: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                disposition_code: Optional[str] = ..., 
                id: Optional[str] = ..., 
                note: Optional[str] = ...
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.communication.jobrouter.models.CancelJobOptions(Model):
        disposition_code: Optional[str]
        note: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                disposition_code: Optional[str] = ..., 
                note: Optional[str] = ...
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.communication.jobrouter.models.ClassificationPolicy(Model):
        etag: str
        fallback_queue_id: Optional[str]
        id: str
        name: Optional[str]
        prioritization_rule: Optional[RouterRule]
        queue_selector_attachments: Optional[List[QueueSelectorAttachment]]
        worker_selector_attachments: Optional[List[WorkerSelectorAttachment]]

        @overload
        def __init__(
                self, 
                *, 
                fallback_queue_id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                prioritization_rule: Optional[RouterRule] = ..., 
                queue_selector_attachments: Optional[List[QueueSelectorAttachment]] = ..., 
                worker_selector_attachments: Optional[List[WorkerSelectorAttachment]] = ...
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.communication.jobrouter.models.CloseJobOptions(Model):
        close_at: Optional[datetime]
        disposition_code: Optional[str]
        note: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                close_at: Optional[datetime] = ..., 
                disposition_code: Optional[str] = ..., 
                note: Optional[str] = ...
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.communication.jobrouter.models.CompleteJobOptions(Model):
        note: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                note: Optional[str] = ...
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.communication.jobrouter.models.ConditionalQueueSelectorAttachment(QueueSelectorAttachment, discriminator='conditional'):
        condition: RouterRule
        kind: Literal[QueueSelectorAttachmentKind.CONDITIONAL]
        queue_selectors: List[RouterQueueSelector]

        @overload
        def __init__(
                self, 
                *, 
                condition: RouterRule, 
                queue_selectors: List[RouterQueueSelector]
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.communication.jobrouter.models.ConditionalWorkerSelectorAttachment(WorkerSelectorAttachment, discriminator='conditional'):
        condition: RouterRule
        kind: Literal[WorkerSelectorAttachmentKind.CONDITIONAL]
        worker_selectors: List[RouterWorkerSelector]

        @overload
        def __init__(
                self, 
                *, 
                condition: RouterRule, 
                worker_selectors: List[RouterWorkerSelector]
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.communication.jobrouter.models.DeclineJobOfferOptions(Model):
        retry_offer_at: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                retry_offer_at: Optional[datetime] = ...
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.communication.jobrouter.models.DirectMapRouterRule(RouterRule, discriminator='directMap'):
        kind: Literal[RouterRuleKind.DIRECT_MAP]

        @overload
        def __init__(
                self, 
                *, 
                kind: str
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.communication.jobrouter.models.DistributionMode(Model):
        bypass_selectors: Optional[bool]
        kind: str
        max_concurrent_offers: Optional[int]
        min_concurrent_offers: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                bypass_selectors: Optional[bool] = ..., 
                kind: str, 
                max_concurrent_offers: Optional[int] = ..., 
                min_concurrent_offers: Optional[int] = ...
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.communication.jobrouter.models.DistributionModeKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BEST_WORKER = "bestWorker"
        LONGEST_IDLE = "longestIdle"
        ROUND_ROBIN = "roundRobin"


    class azure.communication.jobrouter.models.DistributionPolicy(Model):
        etag: str
        id: str
        mode: Optional[DistributionMode]
        name: Optional[str]
        offer_expires_after_seconds: Optional[float]

        @overload
        def __init__(
                self, 
                *, 
                mode: Optional[DistributionMode] = ..., 
                name: Optional[str] = ..., 
                offer_expires_after_seconds: Optional[float] = ...
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.communication.jobrouter.models.ExceptionAction(Model):
        id: Optional[str]
        kind: str

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                kind: str
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.communication.jobrouter.models.ExceptionActionKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCEL = "cancel"
        MANUAL_RECLASSIFY = "manualReclassify"
        RECLASSIFY = "reclassify"


    class azure.communication.jobrouter.models.ExceptionPolicy(Model):
        etag: str
        exception_rules: Optional[List[ExceptionRule]]
        id: str
        name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                exception_rules: Optional[List[ExceptionRule]] = ..., 
                name: Optional[str] = ...
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.communication.jobrouter.models.ExceptionRule(Model):
        actions: List[ExceptionAction]
        id: str
        trigger: ExceptionTrigger

        @overload
        def __init__(
                self, 
                *, 
                actions: List[ExceptionAction], 
                id: str, 
                trigger: ExceptionTrigger
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.communication.jobrouter.models.ExceptionTrigger(Model):
        kind: str

        @overload
        def __init__(
                self, 
                *, 
                kind: str
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.communication.jobrouter.models.ExceptionTriggerKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        QUEUE_LENGTH = "queueLength"
        WAIT_TIME = "waitTime"


    class azure.communication.jobrouter.models.ExpressionRouterRule(RouterRule, discriminator='expression'):
        expression: str
        kind: Literal[RouterRuleKind.EXPRESSION]
        language: Optional[Union[str, ExpressionRouterRuleLanguage]]

        @overload
        def __init__(
                self, 
                *, 
                expression: str, 
                language: Optional[Union[str, ExpressionRouterRuleLanguage]] = ...
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.communication.jobrouter.models.ExpressionRouterRuleLanguage(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        POWER_FX = "powerFx"


    class azure.communication.jobrouter.models.FunctionRouterRule(RouterRule, discriminator='function'):
        credential: Optional[FunctionRouterRuleCredential]
        function_uri: str
        kind: Literal[RouterRuleKind.FUNCTION]

        @overload
        def __init__(
                self, 
                *, 
                credential: Optional[FunctionRouterRuleCredential] = ..., 
                function_uri: str
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.communication.jobrouter.models.FunctionRouterRuleCredential(Model):
        app_key: Optional[str]
        client_id: Optional[str]
        function_key: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                app_key: Optional[str] = ..., 
                client_id: Optional[str] = ..., 
                function_key: Optional[str] = ...
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.communication.jobrouter.models.JobMatchingMode(Model):
        kind: str

        @overload
        def __init__(
                self, 
                *, 
                kind: str
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.communication.jobrouter.models.JobMatchingModeKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        QUEUE_AND_MATCH = "queueAndMatch"
        SCHEDULE_AND_SUSPEND = "scheduleAndSuspend"
        SUSPEND = "suspend"


    class azure.communication.jobrouter.models.LabelOperator(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EQUAL = "equal"
        GREATER_THAN = "greaterThan"
        GREATER_THAN_OR_EQUAL = "greaterThanOrEqual"
        LESS_THAN = "lessThan"
        LESS_THAN_OR_EQUAL = "lessThanOrEqual"
        NOT_EQUAL = "notEqual"


    class azure.communication.jobrouter.models.LongestIdleMode(DistributionMode, discriminator='longestIdle'):
        bypass_selectors: bool
        kind: Literal[DistributionModeKind.LONGEST_IDLE]
        max_concurrent_offers: int
        min_concurrent_offers: int

        @overload
        def __init__(
                self, 
                *, 
                bypass_selectors: Optional[bool] = ..., 
                max_concurrent_offers: Optional[int] = ..., 
                min_concurrent_offers: Optional[int] = ...
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.communication.jobrouter.models.ManualReclassifyExceptionAction(ExceptionAction, discriminator='manualReclassify'):
        id: str
        kind: Literal[ExceptionActionKind.MANUAL_RECLASSIFY]
        priority: Optional[int]
        queue_id: Optional[str]
        worker_selectors: Optional[List[RouterWorkerSelector]]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                priority: Optional[int] = ..., 
                queue_id: Optional[str] = ..., 
                worker_selectors: Optional[List[RouterWorkerSelector]] = ...
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.communication.jobrouter.models.OAuth2WebhookClientCredential(Model):
        client_id: Optional[str]
        client_secret: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                client_id: Optional[str] = ..., 
                client_secret: Optional[str] = ...
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.communication.jobrouter.models.PassThroughQueueSelectorAttachment(QueueSelectorAttachment, discriminator='passThrough'):
        key: str
        kind: Literal[QueueSelectorAttachmentKind.PASS_THROUGH]
        label_operator: Union[str, LabelOperator]

        @overload
        def __init__(
                self, 
                *, 
                key: str, 
                label_operator: Union[str, LabelOperator]
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.communication.jobrouter.models.PassThroughWorkerSelectorAttachment(WorkerSelectorAttachment, discriminator='passThrough'):
        expires_after_seconds: Optional[float]
        key: str
        kind: Literal[WorkerSelectorAttachmentKind.PASS_THROUGH]
        label_operator: Union[str, LabelOperator]

        @overload
        def __init__(
                self, 
                *, 
                expires_after_seconds: Optional[float] = ..., 
                key: str, 
                label_operator: Union[str, LabelOperator]
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.communication.jobrouter.models.QueueAndMatchMode(JobMatchingMode, discriminator='queueAndMatch'):
        kind: Literal[JobMatchingModeKind.QUEUE_AND_MATCH]

        @overload
        def __init__(
                self, 
                *, 
                kind: str
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.communication.jobrouter.models.QueueLengthExceptionTrigger(ExceptionTrigger, discriminator='queueLength'):
        kind: Literal[ExceptionTriggerKind.QUEUE_LENGTH]
        threshold: int

        @overload
        def __init__(
                self, 
                *, 
                threshold: int
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.communication.jobrouter.models.QueueSelectorAttachment(Model):
        kind: str

        @overload
        def __init__(
                self, 
                *, 
                kind: str
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.communication.jobrouter.models.QueueSelectorAttachmentKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONDITIONAL = "conditional"
        PASS_THROUGH = "passThrough"
        RULE_ENGINE = "ruleEngine"
        STATIC = "static"
        WEIGHTED_ALLOCATION = "weightedAllocation"


    class azure.communication.jobrouter.models.QueueWeightedAllocation(Model):
        queue_selectors: List[RouterQueueSelector]
        weight: float

        @overload
        def __init__(
                self, 
                *, 
                queue_selectors: List[RouterQueueSelector], 
                weight: float
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.communication.jobrouter.models.ReclassifyExceptionAction(ExceptionAction, discriminator='reclassify'):
        classification_policy_id: Optional[str]
        id: str
        kind: Literal[ExceptionActionKind.RECLASSIFY]
        labels_to_upsert: Optional[Dict[str, Any]]

        @overload
        def __init__(
                self, 
                *, 
                classification_policy_id: Optional[str] = ..., 
                id: Optional[str] = ..., 
                labels_to_upsert: Optional[Dict[str, Any]] = ...
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.communication.jobrouter.models.RoundRobinMode(DistributionMode, discriminator='roundRobin'):
        bypass_selectors: bool
        kind: Literal[DistributionModeKind.ROUND_ROBIN]
        max_concurrent_offers: int
        min_concurrent_offers: int

        @overload
        def __init__(
                self, 
                *, 
                bypass_selectors: Optional[bool] = ..., 
                max_concurrent_offers: Optional[int] = ..., 
                min_concurrent_offers: Optional[int] = ...
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.communication.jobrouter.models.RouterChannel(Model):
        capacity_cost_per_job: int
        channel_id: str
        max_number_of_jobs: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                capacity_cost_per_job: int, 
                channel_id: str, 
                max_number_of_jobs: Optional[int] = ...
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.communication.jobrouter.models.RouterJob(Model):
        assignments: Optional[Dict[str, RouterJobAssignment]]
        attached_worker_selectors: Optional[List[RouterWorkerSelector]]
        channel_id: Optional[str]
        channel_reference: Optional[str]
        classification_policy_id: Optional[str]
        disposition_code: Optional[str]
        enqueued_at: Optional[datetime]
        etag: str
        id: str
        labels: Optional[Dict[str, Any]]
        matching_mode: Optional[JobMatchingMode]
        notes: Optional[List[RouterJobNote]]
        priority: Optional[int]
        queue_id: Optional[str]
        requested_worker_selectors: Optional[List[RouterWorkerSelector]]
        scheduled_at: Optional[datetime]
        status: Optional[Union[str, RouterJobStatus]]
        tags: Optional[Dict[str, Any]]

        @overload
        def __init__(
                self, 
                *, 
                channel_id: Optional[str] = ..., 
                channel_reference: Optional[str] = ..., 
                classification_policy_id: Optional[str] = ..., 
                disposition_code: Optional[str] = ..., 
                labels: Optional[Dict[str, Any]] = ..., 
                matching_mode: Optional[JobMatchingMode] = ..., 
                notes: Optional[List[RouterJobNote]] = ..., 
                priority: Optional[int] = ..., 
                queue_id: Optional[str] = ..., 
                requested_worker_selectors: Optional[List[RouterWorkerSelector]] = ..., 
                tags: Optional[Dict[str, Any]] = ...
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.communication.jobrouter.models.RouterJobAssignment(Model):
        assigned_at: datetime
        assignment_id: str
        closed_at: Optional[datetime]
        completed_at: Optional[datetime]
        worker_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                assigned_at: datetime, 
                closed_at: Optional[datetime] = ..., 
                completed_at: Optional[datetime] = ..., 
                worker_id: Optional[str] = ...
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.communication.jobrouter.models.RouterJobNote(Model):
        added_at: Optional[datetime]
        message: str

        @overload
        def __init__(
                self, 
                *, 
                added_at: Optional[datetime] = ..., 
                message: str
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.communication.jobrouter.models.RouterJobOffer(Model):
        capacity_cost: int
        expires_at: Optional[datetime]
        job_id: str
        offer_id: str
        offered_at: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                capacity_cost: int, 
                expires_at: Optional[datetime] = ..., 
                job_id: str, 
                offered_at: Optional[datetime] = ...
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.communication.jobrouter.models.RouterJobPositionDetails(Model):
        estimated_wait_time_minutes: float
        job_id: str
        position: int
        queue_id: str
        queue_length: int

        @overload
        def __init__(
                self, 
                *, 
                estimated_wait_time_minutes: float, 
                job_id: str, 
                position: int, 
                queue_id: str, 
                queue_length: int
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.communication.jobrouter.models.RouterJobStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ASSIGNED = "assigned"
        CANCELLED = "cancelled"
        CLASSIFICATION_FAILED = "classificationFailed"
        CLOSED = "closed"
        COMPLETED = "completed"
        CREATED = "created"
        PENDING_CLASSIFICATION = "pendingClassification"
        PENDING_SCHEDULE = "pendingSchedule"
        QUEUED = "queued"
        SCHEDULED = "scheduled"
        SCHEDULE_FAILED = "scheduleFailed"
        WAITING_FOR_ACTIVATION = "waitingForActivation"


    class azure.communication.jobrouter.models.RouterJobStatusSelector(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "active"
        ALL = "all"
        ASSIGNED = "assigned"
        CANCELLED = "cancelled"
        CLASSIFICATION_FAILED = "classificationFailed"
        CLOSED = "closed"
        COMPLETED = "completed"
        CREATED = "created"
        PENDING_CLASSIFICATION = "pendingClassification"
        PENDING_SCHEDULE = "pendingSchedule"
        QUEUED = "queued"
        SCHEDULED = "scheduled"
        SCHEDULE_FAILED = "scheduleFailed"
        WAITING_FOR_ACTIVATION = "waitingForActivation"


    class azure.communication.jobrouter.models.RouterQueue(Model):
        distribution_policy_id: Optional[str]
        etag: str
        exception_policy_id: Optional[str]
        id: str
        labels: Optional[Dict[str, Any]]
        name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                distribution_policy_id: Optional[str] = ..., 
                exception_policy_id: Optional[str] = ..., 
                labels: Optional[Dict[str, Any]] = ..., 
                name: Optional[str] = ...
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.communication.jobrouter.models.RouterQueueSelector(Model):
        key: str
        label_operator: Union[str, LabelOperator]
        value: Optional[Any]

        @overload
        def __init__(
                self, 
                *, 
                key: str, 
                label_operator: Union[str, LabelOperator], 
                value: Optional[Any] = ...
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.communication.jobrouter.models.RouterQueueStatistics(Model):
        estimated_wait_time_minutes: Optional[Dict[str, float]]
        length: int
        longest_job_wait_time_minutes: Optional[float]
        queue_id: str

        @overload
        def __init__(
                self, 
                *, 
                estimated_wait_time_minutes: Optional[Dict[str, float]] = ..., 
                length: int, 
                longest_job_wait_time_minutes: Optional[float] = ..., 
                queue_id: str
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.communication.jobrouter.models.RouterRule(Model):
        kind: str

        @overload
        def __init__(
                self, 
                *, 
                kind: str
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.communication.jobrouter.models.RouterRuleKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DIRECT_MAP = "directMap"
        EXPRESSION = "expression"
        FUNCTION = "function"
        STATIC = "static"
        WEBHOOK = "webhook"


    class azure.communication.jobrouter.models.RouterWorker(Model):
        assigned_jobs: Optional[List[RouterWorkerAssignment]]
        available_for_offers: Optional[bool]
        capacity: Optional[int]
        channels: Optional[List[RouterChannel]]
        etag: str
        id: str
        labels: Optional[Dict[str, Any]]
        load_ratio: Optional[float]
        max_concurrent_offers: Optional[int]
        offers: Optional[List[RouterJobOffer]]
        queues: Optional[List[str]]
        state: Optional[Union[str, RouterWorkerState]]
        tags: Optional[Dict[str, Any]]

        @overload
        def __init__(
                self, 
                *, 
                available_for_offers: Optional[bool] = ..., 
                capacity: Optional[int] = ..., 
                channels: Optional[List[RouterChannel]] = ..., 
                labels: Optional[Dict[str, Any]] = ..., 
                max_concurrent_offers: Optional[int] = ..., 
                queues: Optional[List[str]] = ..., 
                tags: Optional[Dict[str, Any]] = ...
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.communication.jobrouter.models.RouterWorkerAssignment(Model):
        assigned_at: datetime
        assignment_id: str
        capacity_cost: int
        job_id: str

        @overload
        def __init__(
                self, 
                *, 
                assigned_at: datetime, 
                assignment_id: str, 
                capacity_cost: int, 
                job_id: str
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.communication.jobrouter.models.RouterWorkerSelector(Model):
        expedite: Optional[bool]
        expires_after_seconds: Optional[float]
        expires_at: Optional[datetime]
        key: str
        label_operator: Union[str, LabelOperator]
        status: Optional[Union[str, RouterWorkerSelectorStatus]]
        value: Optional[Any]

        @overload
        def __init__(
                self, 
                *, 
                expedite: Optional[bool] = ..., 
                expires_after_seconds: Optional[float] = ..., 
                key: str, 
                label_operator: Union[str, LabelOperator], 
                value: Optional[Any] = ...
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.communication.jobrouter.models.RouterWorkerSelectorStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "active"
        EXPIRED = "expired"


    class azure.communication.jobrouter.models.RouterWorkerState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "active"
        DRAINING = "draining"
        INACTIVE = "inactive"


    class azure.communication.jobrouter.models.RouterWorkerStateSelector(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "active"
        ALL = "all"
        DRAINING = "draining"
        INACTIVE = "inactive"


    class azure.communication.jobrouter.models.RuleEngineQueueSelectorAttachment(QueueSelectorAttachment, discriminator='ruleEngine'):
        kind: Literal[QueueSelectorAttachmentKind.RULE_ENGINE]
        rule: RouterRule

        @overload
        def __init__(
                self, 
                *, 
                rule: RouterRule
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.communication.jobrouter.models.RuleEngineWorkerSelectorAttachment(WorkerSelectorAttachment, discriminator='ruleEngine'):
        kind: Literal[WorkerSelectorAttachmentKind.RULE_ENGINE]
        rule: RouterRule

        @overload
        def __init__(
                self, 
                *, 
                rule: RouterRule
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.communication.jobrouter.models.ScheduleAndSuspendMode(JobMatchingMode, discriminator='scheduleAndSuspend'):
        kind: Literal[JobMatchingModeKind.SCHEDULE_AND_SUSPEND]
        schedule_at: datetime

        @overload
        def __init__(
                self, 
                *, 
                schedule_at: datetime
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.communication.jobrouter.models.ScoringRuleOptions(Model):
        batch_size: Optional[int]
        descending_order: Optional[bool]
        is_batch_scoring_enabled: Optional[bool]
        scoring_parameters: Optional[List[Union[str, ScoringRuleParameterSelector]]]

        @overload
        def __init__(
                self, 
                *, 
                batch_size: Optional[int] = ..., 
                descending_order: Optional[bool] = ..., 
                is_batch_scoring_enabled: Optional[bool] = ..., 
                scoring_parameters: Optional[List[Union[str, ScoringRuleParameterSelector]]] = ...
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.communication.jobrouter.models.ScoringRuleParameterSelector(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        JOB_LABELS = "jobLabels"
        WORKER_SELECTORS = "workerSelectors"


    class azure.communication.jobrouter.models.StaticQueueSelectorAttachment(QueueSelectorAttachment, discriminator='static'):
        kind: Literal[QueueSelectorAttachmentKind.STATIC]
        queue_selector: RouterQueueSelector

        @overload
        def __init__(
                self, 
                *, 
                queue_selector: RouterQueueSelector
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.communication.jobrouter.models.StaticRouterRule(RouterRule, discriminator='static'):
        kind: Literal[RouterRuleKind.STATIC]
        value: Optional[Any]

        @overload
        def __init__(
                self, 
                *, 
                value: Optional[Any] = ...
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.communication.jobrouter.models.StaticWorkerSelectorAttachment(WorkerSelectorAttachment, discriminator='static'):
        kind: Literal[WorkerSelectorAttachmentKind.STATIC]
        worker_selector: RouterWorkerSelector

        @overload
        def __init__(
                self, 
                *, 
                worker_selector: RouterWorkerSelector
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.communication.jobrouter.models.SuspendMode(JobMatchingMode, discriminator='suspend'):
        kind: Literal[JobMatchingModeKind.SUSPEND]

        @overload
        def __init__(
                self, 
                *, 
                kind: str
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.communication.jobrouter.models.UnassignJobOptions(Model):
        suspend_matching: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                suspend_matching: Optional[bool] = ...
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.communication.jobrouter.models.UnassignJobResult(Model):
        job_id: str
        unassignment_count: int

        @overload
        def __init__(
                self, 
                *, 
                job_id: str, 
                unassignment_count: int
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.communication.jobrouter.models.WaitTimeExceptionTrigger(ExceptionTrigger, discriminator='waitTime'):
        kind: Literal[ExceptionTriggerKind.WAIT_TIME]
        threshold_seconds: float

        @overload
        def __init__(
                self, 
                *, 
                threshold_seconds: float
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.communication.jobrouter.models.WebhookRouterRule(RouterRule, discriminator='webhook'):
        authorization_server_uri: Optional[str]
        client_credential: Optional[OAuth2WebhookClientCredential]
        kind: Literal[RouterRuleKind.WEBHOOK]
        webhook_uri: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                authorization_server_uri: Optional[str] = ..., 
                client_credential: Optional[OAuth2WebhookClientCredential] = ..., 
                webhook_uri: Optional[str] = ...
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.communication.jobrouter.models.WeightedAllocationQueueSelectorAttachment(QueueSelectorAttachment, discriminator='weightedAllocation'):
        allocations: List[QueueWeightedAllocation]
        kind: Literal[QueueSelectorAttachmentKind.WEIGHTED_ALLOCATION]

        @overload
        def __init__(
                self, 
                *, 
                allocations: List[QueueWeightedAllocation]
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.communication.jobrouter.models.WeightedAllocationWorkerSelectorAttachment(WorkerSelectorAttachment, discriminator='weightedAllocation'):
        allocations: List[WorkerWeightedAllocation]
        kind: Literal[WorkerSelectorAttachmentKind.WEIGHTED_ALLOCATION]

        @overload
        def __init__(
                self, 
                *, 
                allocations: List[WorkerWeightedAllocation]
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.communication.jobrouter.models.WorkerSelectorAttachment(Model):
        kind: str

        @overload
        def __init__(
                self, 
                *, 
                kind: str
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.communication.jobrouter.models.WorkerSelectorAttachmentKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONDITIONAL = "conditional"
        PASS_THROUGH = "passThrough"
        RULE_ENGINE = "ruleEngine"
        STATIC = "static"
        WEIGHTED_ALLOCATION = "weightedAllocation"


    class azure.communication.jobrouter.models.WorkerWeightedAllocation(Model):
        weight: float
        worker_selectors: List[RouterWorkerSelector]

        @overload
        def __init__(
                self, 
                *, 
                weight: float, 
                worker_selectors: List[RouterWorkerSelector]
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


```