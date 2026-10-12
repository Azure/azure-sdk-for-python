# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Models for the RLE Execute Rollout operation.

Execute Rollout runs one complete episode of a published RLE environment version and returns
what it produced. The service owns the loop -- it resets the environment, asks the model for a
completion, applies the action, and repeats until the environment terminates or the version's
step budget is spent. The caller supplies only the task and the model binding.

That is the difference from the instance-level reset/step operations, where the caller owns the
loop and drives an instance it leased. Here nothing is leased and nothing is stepped by hand; a
rollout is one request and one result.

The result carries both halves of what a training run needs: ``reward`` (and ``success`` where a
grader produced a verdict) and ``rollout``, the Capture Proxy graph, whose ``sequences`` hold the
``input_ids``/``loss_mask``/``logprobs`` of every model turn the episode sampled.
"""

from typing import Any, List, Literal, Mapping, Optional, overload

from .._utils.model_base import Model as _Model, rest_discriminator, rest_field

__all__ = [
    "RLERolloutPolicy",
    "RLELoomPolicy",
    "RLESamplingOptions",
    "RLERolloutRequest",
    "RLERolloutResult",
    "RLERolloutEpisode",
    "RLERolloutStep",
]

_VISIBILITY = ["read", "create", "update", "delete", "query"]


class RLERolloutPolicy(_Model):
    """Where a rollout's weights come from, discriminated by ``type``.

    A rollout has to say which backend resolves its weights before it can say anything about
    them, because the fields that identify weights mean different things to different backends.
    ``type`` is that statement; the concrete subclass carries whatever its backend requires.

    :ivar type: Discriminator naming the backend. Required.
    :vartype type: str
    """

    __mapping__: dict[str, _Model] = {}
    type: str = rest_discriminator(name="type", visibility=_VISIBILITY)
    """Discriminator naming the backend that resolves this policy's weights. Required."""


class RLELoomPolicy(RLERolloutPolicy, discriminator="loom"):
    """Weights held in a Loom training session, pinned to one immutable checkpoint.

    A rollout never samples from a deployment by name alone. ``session_id`` and ``checkpoint_id``
    pin it to exact weights, which is what makes the returned trajectory on-policy for that
    checkpoint and therefore trainable. The two are supplied together; the service rejects one
    without the other.

    ``project_endpoint`` is supplied per rollout rather than taken from the client, because one
    RLE deployment serves callers from many projects and the caller's token is presented against
    this endpoint.

    :ivar type: Always ``"loom"``. Required.
    :vartype type: str
    :ivar model_name: Training model to sample from. Required.
    :vartype model_name: str
    :ivar project_endpoint: Foundry project endpoint whose Loom sampler serves this rollout. Required.
    :vartype project_endpoint: str
    :ivar session_id: Loom training session holding the weights. Required, with ``checkpoint_id``.
    :vartype session_id: str
    :ivar checkpoint_id: Immutable Loom checkpoint identifier. Required, with ``session_id``.
    :vartype checkpoint_id: str
    :ivar sequence_id: Optional Loom sequence identifier for this rollout.
    :vartype sequence_id: int
    """

    type: Literal["loom"] = rest_discriminator(name="type", visibility=_VISIBILITY)  # type: ignore
    """Always ``\"loom\"``. Required."""
    model_name: str = rest_field(visibility=_VISIBILITY)
    """Training model to sample from. Required."""
    project_endpoint: str = rest_field(visibility=_VISIBILITY)
    """Foundry project endpoint whose Loom sampler serves this rollout. Required."""
    session_id: str = rest_field(visibility=_VISIBILITY)
    """Loom training session holding the weights. Required, with ``checkpoint_id``."""
    checkpoint_id: str = rest_field(visibility=_VISIBILITY)
    """Immutable Loom checkpoint identifier. Required, with ``session_id``."""
    sequence_id: Optional[int] = rest_field(visibility=_VISIBILITY)
    """Optional Loom sequence identifier for this rollout."""

    @overload
    def __init__(
        self,
        *,
        model_name: str,
        project_endpoint: str,
        session_id: str,
        checkpoint_id: str,
        sequence_id: Optional[int] = None,
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None:
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, type="loom", **kwargs)


class RLESamplingOptions(_Model):
    """How a rollout's completions are sampled and rendered.

    Separate from :class:`RLERolloutPolicy` on purpose: a renderer describes how a completion is
    turned into tokens, not where the weights came from, so it applies to every policy kind that
    captures a trainable graph rather than being a property of one of them.

    :ivar renderer_name: Optional Capture Proxy renderer profile. The service picks a compatible
     default when omitted.
    :vartype renderer_name: str
    """

    renderer_name: Optional[str] = rest_field(visibility=_VISIBILITY)
    """Optional Capture Proxy renderer profile."""

    @overload
    def __init__(self, *, renderer_name: Optional[str] = None) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None:
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


class RLERolloutRequest(_Model):
    """Request body for one Execute Rollout call.

    ``task`` is one opaque JSON value -- normally a complete dataset row -- forwarded unchanged to
    the environment's ``reset``. The service does not inspect or reinterpret it, so its schema is
    the environment's own contract, not RLE's.

    :ivar rollout_id: Caller-generated identifier, reserved within the project before any resource
     is allocated and returned unchanged. Required.
    :vartype rollout_id: str
    :ivar task: Opaque task record passed verbatim to the environment's reset. Required.
    :vartype task: any
    :ivar policy: Where this rollout's weights come from. Required.
    :vartype policy: ~azure.ai.projects.models.RLERolloutPolicy
    :ivar sampling: How this rollout's completions are sampled and rendered. Optional.
    :vartype sampling: ~azure.ai.projects.models.RLESamplingOptions
    """

    rollout_id: str = rest_field(visibility=_VISIBILITY)
    """Caller-generated identifier, returned unchanged. Required."""
    task: Any = rest_field(visibility=_VISIBILITY)
    """Opaque task record passed verbatim to the environment's reset. Required."""
    policy: RLERolloutPolicy = rest_field(visibility=_VISIBILITY)
    """Where this rollout's weights come from. Required."""
    sampling: Optional[RLESamplingOptions] = rest_field(visibility=_VISIBILITY)
    """How this rollout's completions are sampled and rendered."""

    @overload
    def __init__(
        self,
        *,
        rollout_id: str,
        task: Any,
        policy: RLERolloutPolicy,
        sampling: Optional[RLESamplingOptions] = None,
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None:
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


class RLERolloutStep(_Model):
    """One environment step of a Gym/OpenEnv episode, bound to the model turn that produced it.

    :ivar capture_node_id: Capture Proxy model-turn identifier that produced this action.
    :vartype capture_node_id: str
    :ivar reward: Environment reward returned for this action.
    :vartype reward: float
    :ivar episode_done: Whether the environment ended the episode on this step.
    :vartype episode_done: bool
    """

    capture_node_id: Optional[str] = rest_field(visibility=_VISIBILITY)
    """Capture Proxy model-turn identifier that produced this action."""
    reward: Optional[float] = rest_field(visibility=_VISIBILITY)
    """Environment reward returned for this action."""
    episode_done: Optional[bool] = rest_field(visibility=_VISIBILITY)
    """Whether the environment ended the episode on this step."""

    @overload
    def __init__(
        self,
        *,
        capture_node_id: Optional[str] = None,
        reward: Optional[float] = None,
        episode_done: Optional[bool] = None,
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None:
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


class RLERolloutEpisode(_Model):
    """Gym/OpenEnv episode annotations. Absent for Harness and BYOH targets, which have no episode.

    :ivar kind: Discriminator for the episode shape.
    :vartype kind: str
    :ivar termination_reason: Why the episode stopped.
    :vartype termination_reason: str
    :ivar steps: Ordered environment steps.
    :vartype steps: list[~azure.ai.projects.models.RLERolloutStep]
    :ivar ungraded: Set when the episode ended without the environment ever reporting termination,
     so its reward is a running sum rather than a grade. Omitted when the environment did grade it,
     which keeps a genuine zero distinguishable from an episode that was never scored.
    :vartype ungraded: bool
    """

    kind: Optional[str] = rest_field(visibility=_VISIBILITY)
    """Discriminator for the episode shape."""
    termination_reason: Optional[str] = rest_field(visibility=_VISIBILITY)
    """Why the episode stopped."""
    steps: Optional[List[RLERolloutStep]] = rest_field(visibility=_VISIBILITY)
    """Ordered environment steps."""
    ungraded: Optional[bool] = rest_field(visibility=_VISIBILITY)
    """Set when the episode ended without the environment ever reporting termination."""

    @overload
    def __init__(
        self,
        *,
        kind: Optional[str] = None,
        termination_reason: Optional[str] = None,
        steps: Optional[List[RLERolloutStep]] = None,
        ungraded: Optional[bool] = None,
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None:
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


class RLERolloutResult(_Model):
    """What one completed rollout produced.

    ``success`` is a grader's verdict and is therefore absent for Gym/OpenEnv, which has no
    grader: an environment reports reward, and inferring a boolean from it would state a result
    the environment never gave. Read ``reward`` for those, and ``success`` only where a Harness
    grader supplied it.

    :ivar rollout_id: The identifier supplied on the request, returned unchanged.
    :vartype rollout_id: str
    :ivar rollout: Capture Proxy graph for the episode, with credentials and routing metadata
     removed. Its ``sequences`` carry the ``input_ids``, ``loss_mask`` and ``logprobs`` of every
     model turn.
    :vartype rollout: dict[str, any]
    :ivar reward: Reward for the rollout. For Gym/OpenEnv this is the undiscounted sum of every
     per-step reward in ``episode``, each of which is also reported individually.
    :vartype reward: float
    :ivar success: Task-level verdict from a Harness grader. Absent for Gym/OpenEnv.
    :vartype success: bool
    :ivar result: Optional structured target result, with protected runtime values removed.
    :vartype result: any
    :ivar episode: Gym/OpenEnv episode annotations. Absent for Harness and BYOH.
    :vartype episode: ~azure.ai.projects.models.RLERolloutEpisode
    """

    rollout_id: str = rest_field(visibility=_VISIBILITY)
    """The identifier supplied on the request, returned unchanged."""
    rollout: Optional[Any] = rest_field(visibility=_VISIBILITY)
    """Capture Proxy graph for the episode."""
    reward: Optional[float] = rest_field(visibility=_VISIBILITY)
    """Reward for the rollout."""
    success: Optional[bool] = rest_field(visibility=_VISIBILITY)
    """Task-level verdict from a Harness grader. Absent for Gym/OpenEnv."""
    result: Optional[Any] = rest_field(visibility=_VISIBILITY)
    """Optional structured target result."""
    episode: Optional[RLERolloutEpisode] = rest_field(visibility=_VISIBILITY)
    """Gym/OpenEnv episode annotations."""

    @overload
    def __init__(
        self,
        *,
        rollout_id: str,
        rollout: Optional[Any] = None,
        reward: Optional[float] = None,
        success: Optional[bool] = None,
        result: Optional[Any] = None,
        episode: Optional[RLERolloutEpisode] = None,
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None:
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

    @property
    def sequences(self) -> List[Any]:
        """The graph's trainable sequences, one per root-to-leaf path, or ``[]`` if it has none.

        Each carries ``input_ids``, ``loss_mask`` and ``logprobs`` for the turns along that path.
        An eval-level capture returns no sequences, so this is empty rather than absent -- callers
        building training data should check it before assuming the rollout is trainable.
        """
        rollout = self.rollout
        if not isinstance(rollout, Mapping):
            return []
        sequences = rollout.get("sequences")
        return list(sequences) if isinstance(sequences, list) else []
