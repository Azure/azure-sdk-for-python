# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
# mypy: disable-error-code="assignment"

from langgraph.types import Interrupt

from azure.ai.agentserver.core.models import projects as project_models

from ..human_in_the_loop_helper import HumanInTheLoopHelper
from ..utils import extract_function_call


class ItemResourceHelper:
    """Base helper for building and accumulating a single :class:`ItemResource`.

    Subclasses specialise the item type and implement
    :meth:`add_aggregate_content` and :meth:`get_aggregated_content`.
    """

    def __init__(self, item_type: str, item_id: str | None = None) -> None:
        """
        :param item_type: The item type constant (e.g. ``ItemType.FUNCTION_CALL``).
        :type item_type: str
        :param item_id: Optional identifier for this item resource.
        :type item_id: str | None
        """
        self.item_type = item_type
        self.item_id = item_id

    def create_item_resource(self, is_done: bool) -> project_models.ItemResource | None:
        """Create the item resource in its current state.

        :param is_done: Whether the item is fully streamed (``True``) or still in progress.
        :type is_done: bool
        :return: The constructed :class:`ItemResource`, or ``None`` if not yet ready.
        :rtype: project_models.ItemResource | None
        """
        pass

    def add_aggregate_content(self, item: object) -> None:
        """Accumulate a streamed content chunk into internal state.

        :param item: The content chunk to accumulate.
        :type item: object
        """
        pass

    def get_aggregated_content(self) -> project_models.ItemResource | None:
        """Return the fully-aggregated item resource.

        :return: The completed :class:`ItemResource`.
        :rtype: project_models.ItemResource | None
        """
        pass


class FunctionCallItemResourceHelper(ItemResourceHelper):
    """Helper for ``function_call`` item resources."""

    def __init__(self, item_id: str | None = None, tool_call: dict | None = None) -> None:
        """
        :param item_id: Identifier for this function-call item.
        :type item_id: str | None
        :param tool_call: Optional tool-call dict to extract the initial name and call ID from.
        :type tool_call: dict | None
        """
        super().__init__(project_models.ItemType.FUNCTION_CALL, item_id)
        self.call_id = None
        self.name = None
        self.arguments = ""
        if tool_call:
            self.name, self.call_id, _ = extract_function_call(tool_call)

    def create_item_resource(self, is_done: bool) -> project_models.ItemResource:
        """Build a function-call :class:`ItemResource`.

        :param is_done: ``True`` sets status to ``"completed"``; ``False`` sets ``"in_progress"``.
        :type is_done: bool
        :return: The constructed function-call item resource.
        :rtype: project_models.ItemResource
        """
        content = {
            "id": self.item_id,
            "type": self.item_type,
            "call_id": self.call_id,
            "name": self.name,
            "arguments": self.arguments if self.arguments else "",
            "status": "in_progress" if not is_done else "completed",
        }
        return project_models.ItemResource(content)

    def add_aggregate_content(self, item: str | dict) -> None:
        """Accumulate streamed argument chunks.

        :param item: A plain string argument fragment, or a dict containing the argument.
        :type item: str | dict
        """
        if isinstance(item, str):
            self.arguments += item
            return
        if not isinstance(item, dict):
            return
        if item.get("type") != project_models.ItemType.FUNCTION_CALL:
            return
        _, _, argument = extract_function_call(item)
        if argument:
            self.arguments += argument

    def get_aggregated_content(self) -> project_models.ItemResource:
        """Return the completed function-call item resource.

        :return: Completed :class:`ItemResource`.
        :rtype: project_models.ItemResource
        """
        return self.create_item_resource(is_done=True)


class FunctionCallInterruptItemResourceHelper(ItemResourceHelper):
    """Helper for HITL (human-in-the-loop) interrupt function-call item resources."""

    def __init__(
        self,
        item_id: str | None = None,
        hitl_helper: HumanInTheLoopHelper | None = None,
        interrupt: Interrupt | None = None,
    ) -> None:
        """
        :param item_id: Identifier for this item resource.
        :type item_id: str | None
        :param hitl_helper: Helper used to convert the interrupt into a function-call item resource.
        :type hitl_helper: HumanInTheLoopHelper | None
        :param interrupt: The LangGraph interrupt value to convert.
        :type interrupt: Interrupt | None
        """
        super().__init__(project_models.ItemType.FUNCTION_CALL, item_id)
        self.hitl_helper = hitl_helper
        self.interrupt = interrupt

    def create_item_resource(self, is_done: bool) -> project_models.ItemResource | None:
        """Convert the stored interrupt into a function-call :class:`ItemResource`.

        :param is_done: When ``False``, clears the arguments field (stream not finished).
        :type is_done: bool
        :return: The converted item resource, or ``None`` if helper or interrupt is absent.
        :rtype: project_models.ItemResource | None
        """
        if self.hitl_helper is None or self.interrupt is None:
            return None
        item_resource = self.hitl_helper.convert_interrupt(self.interrupt)
        if item_resource is not None and not is_done:
            if hasattr(item_resource, 'arguments'):
                item_resource.arguments = ""  # type: ignore[union-attr]
        return item_resource

    def add_aggregate_content(self, item: object) -> None:
        """No-op: interrupt items have no streamed content.

        :param item: Ignored.
        :type item: object
        """

    def get_aggregated_content(self) -> project_models.ItemResource | None:
        """Return the completed interrupt item resource.

        :return: Completed :class:`ItemResource`.
        :rtype: project_models.ItemResource | None
        """
        return self.create_item_resource(is_done=True)


class FunctionCallOutputItemResourceHelper(ItemResourceHelper):
    """Helper for ``function_call_output`` item resources."""

    def __init__(self, item_id: str | None = None, call_id: str | None = None) -> None:
        """
        :param item_id: Identifier for this item resource.
        :type item_id: str | None
        :param call_id: The call ID that this output corresponds to.
        :type call_id: str | None
        """
        super().__init__(project_models.ItemType.FUNCTION_CALL_OUTPUT, item_id)
        self.call_id = call_id
        self.content = ""

    def create_item_resource(self, is_done: bool) -> project_models.ItemResource:
        """Build a function-call-output :class:`ItemResource`.

        :param is_done: ``True`` sets status to ``"completed"``; ``False`` sets ``"in_progress"``.
        :type is_done: bool
        :return: The constructed function-call-output item resource.
        :rtype: project_models.ItemResource
        """
        content = {
            "id": self.item_id,
            "type": self.item_type,
            "status": "in_progress" if not is_done else "completed",
            "call_id": self.call_id,
            "output": self.content,
        }
        return project_models.ItemResource(content)

    def add_aggregate_content(self, item: str | dict) -> None:
        """Accumulate a streamed output chunk.

        :param item: A plain string or a dict with a ``"text"`` key.
        :type item: str | dict
        """
        if isinstance(item, str):
            self.content += item
            return
        if not isinstance(item, dict):
            return
        content = item.get("text")
        if isinstance(content, str):
            self.content += content

    def get_aggregated_content(self) -> project_models.ItemResource:
        """Return the completed function-call-output item resource.

        :return: Completed :class:`ItemResource`.
        :rtype: project_models.ItemResource
        """
        return self.create_item_resource(is_done=True)


class MessageItemResourceHelper(ItemResourceHelper):
    """Helper for ``message`` item resources."""

    def __init__(self, item_id: str, role: project_models.ResponsesMessageRole) -> None:
        """
        :param item_id: Identifier for this message item.
        :type item_id: str
        :param role: The role of the message (e.g. ``ASSISTANT``, ``USER``).
        :type role: project_models.ResponsesMessageRole
        """
        super().__init__(project_models.ItemType.MESSAGE, item_id)
        self.role = role
        self.content: list[project_models.ItemContent] = []

    def create_item_resource(self, is_done: bool) -> project_models.ItemResource:
        """Build a message :class:`ItemResource`.

        :param is_done: ``True`` sets status to ``"completed"``; ``False`` sets ``"in_progress"``.
        :type is_done: bool
        :return: The constructed message item resource.
        :rtype: project_models.ItemResource
        """
        content = {
            "id": self.item_id,
            "type": self.item_type,
            "status": "in_progress" if not is_done else "completed",
            "content": self.content,
            "role": self.role,
        }
        return project_models.ItemResource(content)

    def add_aggregate_content(self, item: dict | project_models.ItemContent) -> None:
        """Append a content part to the message's content list.

        :param item: A raw dict (auto-converted to :class:`ItemContent`) or an :class:`ItemContent` instance.
        :type item: dict | project_models.ItemContent
        """
        if isinstance(item, dict):
            item = project_models.ItemContent(item)
        if isinstance(item, project_models.ItemContent):
            self.content.append(item)

    def get_aggregated_content(self) -> project_models.ItemResource:
        """Return the completed message item resource.

        :return: Completed :class:`ItemResource`.
        :rtype: project_models.ItemResource
        """
        return self.create_item_resource(is_done=True)
