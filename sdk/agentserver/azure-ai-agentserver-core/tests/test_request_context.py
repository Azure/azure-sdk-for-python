# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Unit tests for the request-scoped platform context."""
from __future__ import annotations

import asyncio
from dataclasses import FrozenInstanceError
from urllib.parse import quote, unquote

import httpx
import pytest
from starlette.datastructures import Headers

from azure.ai.agentserver.core import (
    FoundryAgentRequestContext,
    FoundryOriginalSubject,
    get_request_context,
    reset_request_context,
    set_request_context,
)
from azure.ai.agentserver.core._platform_headers import FOUNDRY_CALL_ID, USER_ID

SUBJECT_HEADER = "x-ms-original-subject"
SUBJECT_VALUE = 'oid="original-oid", tid="original-tid", idtype="user"'
SUBJECT_HEADERS = {SUBJECT_HEADER: SUBJECT_VALUE}
BAGGAGE_HEADER = "x-ms-foundry-baggage"


def model_headers(value: str) -> dict[str, str]:
    return {SUBJECT_HEADER: value, BAGGAGE_HEADER: f"foundry.original_subject={quote(value, safe='')}"}


class TestOriginalSubject:
    def test_absent_subject_does_not_infer_from_state_or_call_id(self) -> None:
        context = FoundryAgentRequestContext(user_id="raw-state-user", call_id="opaque-call")
        assert context.original_subject is None
        assert context.model_attribution_headers() == {}
        assert FoundryOriginalSubject.from_headers(Headers({USER_ID: "raw-state-user"})) is None

    @pytest.mark.parametrize("idtype", ["user", "app", "unknown"])
    def test_model_headers_preserve_tuple_and_platform_headers_are_unchanged(self, idtype: str) -> None:
        expected = {SUBJECT_HEADER: f'oid="original-oid", tid="original-tid", idtype="{idtype}"'}
        context = FoundryAgentRequestContext(
            original_subject=FoundryOriginalSubject.from_headers(Headers(expected)),
            call_id="opaque-call",
            user_id="different-state-key",
        )
        assert context.model_attribution_headers() == {
            **model_headers(expected[SUBJECT_HEADER]),
            FOUNDRY_CALL_ID: "opaque-call",
        }
        assert context.platform_headers() == {FOUNDRY_CALL_ID: "opaque-call"}
        copied = context.model_attribution_headers()
        copied[SUBJECT_HEADER] = "changed"
        assert context.model_attribution_headers()[SUBJECT_HEADER] == expected[SUBJECT_HEADER]

    @pytest.mark.parametrize(
        "value,oid,tid,idtype",
        [
            ('tid="original-tid", idtype="user"', None, "original-tid", "user"),
            ('oid="original-oid", idtype="user"', "original-oid", None, "user"),
            ('oid="original-oid", tid="original-tid"', "original-oid", "original-tid", None),
            ('oid="", tid="original-tid", idtype="user"', "", "original-tid", "user"),
            ('oid="original-oid", tid=" ", idtype="user"', "original-oid", " ", "user"),
        ],
    )
    def test_partial_or_empty_subject_is_preserved_but_cannot_be_forwarded(
        self, value: str, oid: str | None, tid: str | None, idtype: str | None
    ) -> None:
        subject = FoundryOriginalSubject.from_headers({SUBJECT_HEADER: value})
        assert subject is not None
        assert (subject.oid, subject.tid, subject.idtype) == (oid, tid, idtype)
        with pytest.raises(ValueError, match="complete, HTTP-safe tuple"):
            FoundryAgentRequestContext(original_subject=subject).model_attribution_headers()

    @pytest.mark.parametrize("invalid", [None, "", " ", "oid\r\ninjected", "\t", "\x00", "\x7f", "\N{SNOWMAN}"])
    def test_constructed_unsafe_subject_cannot_be_forwarded(self, invalid: str | None) -> None:
        subject = FoundryOriginalSubject(oid=invalid, tid="tenant", idtype="user")
        with pytest.raises(ValueError, match="complete, HTTP-safe tuple"):
            FoundryAgentRequestContext(original_subject=subject).model_attribution_headers()

    @pytest.mark.parametrize(
        "value",
        [
            "",
            " ",
            "original-oid,original-tid,user",
            'oid="one", oid="two"',
            'oid="one", oid="one"',
            'oid="one", extra="value"',
            'oid="one";extra="value"',
            "oid=null",
            "oid=user",
            "oid=123",
            "oid=?1",
            'OID="one"',
            'oid = "one"',
            'oid="unterminated',
            'oid="one",',
            ',oid="one"',
            'oid="one",,tid="two"',
            'oid="one"tid="two"',
            r'oid="bad\escape"',
            'oid="bad\r\ninjected"',
            'oid="bad\tinjected"',
            'oid="bad\x00"',
            'oid="bad\x7f"',
            'oid="\N{SNOWMAN}"',
        ],
    )
    def test_malformed_or_ambiguous_dictionary_is_rejected(self, value: str) -> None:
        with pytest.raises(ValueError, match="Original-subject attribution"):
            FoundryOriginalSubject.from_headers({SUBJECT_HEADER: value})

    def test_duplicate_header_fields_are_rejected(self) -> None:
        headers = Headers(
            raw=[
                (SUBJECT_HEADER.encode(), b'oid="one"'),
                (SUBJECT_HEADER.encode(), b'tid="two", idtype="user"'),
            ]
        )
        with pytest.raises(ValueError, match="single header field"):
            FoundryOriginalSubject.from_headers(headers)

    def test_order_and_optional_whitespace_do_not_change_the_snapshot(self) -> None:
        subject = FoundryOriginalSubject.from_headers(
            {
                "X-MS-Original-Subject": (" \t" 'idtype="user" \t,tid="original-tid",\t oid="original-oid"\t '),
            }
        )
        assert subject == FoundryOriginalSubject(oid="original-oid", tid="original-tid", idtype="user")
        assert FoundryAgentRequestContext(original_subject=subject).model_attribution_headers() == model_headers(
            SUBJECT_VALUE
        )

    def test_structured_fields_escaping_round_trips_without_splitting_quoted_commas(self) -> None:
        value = r'oid="original\\oid\",branch", tid="original-tid", idtype="user"'
        subject = FoundryOriginalSubject.from_headers({SUBJECT_HEADER: value})
        assert subject == FoundryOriginalSubject(oid='original\\oid",branch', tid="original-tid", idtype="user")
        assert FoundryAgentRequestContext(original_subject=subject).model_attribution_headers() == model_headers(value)

    @pytest.mark.parametrize("present", [False, True])
    def test_merge_replaces_reserved_subjects_without_mutating_headers(self, present: bool) -> None:
        existing = {
            "Authorization": "test-key",
            "X-MS-Original-Subject": "stale",
            "x-ms-original-subject": "also-stale",
            "X-MS-Original-Subject-Oid": "stale",
            "X-AGENT-FOUNDRY-CALL-ID": "stale-call",
            "X-MS-Foundry-Baggage": (
                "app=example,Foundry.Original_Subject=stale,"
                "foundry.original_subject.oid=stale,FOUNDry.original_subject.tid=stale"
            ),
            "x-ms-foundry-baggage": (
                "trace=opaque%252Cvalue;flag,app=example,"
                "FOUNDRY.ORIGINAL_SUBJECT=other,foundry.original_subject.idtype=app"
            ),
        }
        snapshot = existing.copy()
        context = FoundryAgentRequestContext(
            original_subject=FoundryOriginalSubject(oid="current", tid="tenant", idtype="app") if present else None,
            call_id="current-call",
        )
        result = context.model_attribution_headers(existing)
        assert existing == snapshot
        assert result["Authorization"] == "test-key"
        members = result[BAGGAGE_HEADER].split(",")
        unrelated = members[1:] if present else members
        assert unrelated == ["app=example", "trace=opaque%252Cvalue;flag", "app=example"]
        keys = [member.split("=", 1)[0].lower() for member in members]
        assert keys.count("foundry.original_subject") == int(present)
        assert not any(key.startswith("foundry.original_subject.") for key in keys)
        assert all(name in {"Authorization", BAGGAGE_HEADER, SUBJECT_HEADER, FOUNDRY_CALL_ID} for name in result)
        if present:
            assert unquote(members[0].split("=", 1)[1]) == result[SUBJECT_HEADER]
            assert FoundryOriginalSubject.from_headers(result) == context.original_subject
            assert result[FOUNDRY_CALL_ID] == "current-call"
        else:
            assert result == {"Authorization": "test-key", BAGGAGE_HEADER: ",".join(members[:3])}
        result[BAGGAGE_HEADER] = "changed"
        assert context.model_attribution_headers(existing)[BAGGAGE_HEADER] != "changed"

    def test_reserved_only_headers_disappear_without_a_subject(self) -> None:
        assert (
            FoundryAgentRequestContext().model_attribution_headers(
                {
                    "X-MS-Original-Subject": SUBJECT_VALUE,
                    BAGGAGE_HEADER: "foundry.original_subject=stale,FOUNDry.original_subject.oid=stale",
                }
            )
            == {}
        )

    @pytest.mark.parametrize("present", [False, True])
    @pytest.mark.parametrize(
        "stale",
        [
            "Foundry.Original_Subject;stale=1",
            "foundry.original_subject;stale",
            "FOUNDry.original_subject.oid;stale=1",
            "foundry%2Eoriginal_subject;stale=1",  # cspell:disable-line
        ],
    )
    def test_reserved_members_with_properties_are_removed(self, present: bool, stale: str) -> None:
        subject = FoundryOriginalSubject(oid="current", tid="tenant", idtype="user") if present else None
        existing = {BAGGAGE_HEADER: f"foundry.project.id=project,{stale}"}
        result = FoundryAgentRequestContext(original_subject=subject).model_attribution_headers(existing)
        expected = "foundry.project.id=project"
        if subject is not None:
            expected = model_headers('oid="current", tid="tenant", idtype="user"')[BAGGAGE_HEADER] + "," + expected
        assert result[BAGGAGE_HEADER] == expected
        assert existing[BAGGAGE_HEADER] == f"foundry.project.id=project,{stale}"

    @pytest.mark.parametrize("present", [False, True])
    def test_unrelated_duplicate_baggage_is_preserved_without_reinterpreting_caller(self, present: bool) -> None:
        baggage = (
            "Foundry.Caller.Identity.Oid=caller-a,foundry.caller.identity.oid=caller-b,"
            "foundry.project.id=project-a,foundry.project.id=project-b,"
            "foundry.agent.name=opaque%252Cvalue;flag=true"
        )
        existing = {"Authorization": "test-key", BAGGAGE_HEADER: baggage}
        subject = FoundryOriginalSubject(oid="current", tid="tenant", idtype="user") if present else None
        result = FoundryAgentRequestContext(original_subject=subject).model_attribution_headers(existing)
        expected = baggage
        if subject is not None:
            expected = model_headers('oid="current", tid="tenant", idtype="user"')[BAGGAGE_HEADER] + "," + expected
        assert result[BAGGAGE_HEADER] == expected
        assert result["Authorization"] == existing["Authorization"]
        assert existing[BAGGAGE_HEADER] == baggage

    @pytest.mark.parametrize("length", [256, 257])
    @pytest.mark.parametrize("character", ["x", '"', "\\"])
    def test_serialized_subject_transport_bound(self, length: int, character: str) -> None:
        fixed_length = len('oid="", tid="tenant", idtype="user"')
        available = length - fixed_length
        escaped_length = 1 if character == "x" else 2
        oid = character * (available // escaped_length) + "x" * (available % escaped_length)
        context = FoundryAgentRequestContext(
            original_subject=FoundryOriginalSubject(oid=oid, tid="tenant", idtype="user")
        )
        if length > 256:
            with pytest.raises(ValueError, match="256"):
                context.model_attribution_headers()
        else:
            result = context.model_attribution_headers()
            assert len(result[SUBJECT_HEADER]) == length
            assert unquote(result[BAGGAGE_HEADER].split("=", 1)[1]) == result[SUBJECT_HEADER]

    @pytest.mark.parametrize("length", [1024, 1025])
    def test_merged_baggage_transport_bound_without_mutating_headers(self, length: int) -> None:
        context = FoundryAgentRequestContext(
            original_subject=FoundryOriginalSubject(oid="current", tid="tenant", idtype="user")
        )
        encoded = context.model_attribution_headers()[BAGGAGE_HEADER]
        prefix = ",".join(f"foundry.keep{index}=" + "x" * 200 for index in range(4)) + ",foundry.tail="
        baggage = prefix + "x" * (length - len(prefix) - 1 - len(encoded))
        existing_baggage = f"{baggage},foundry.original_subject=" + "x" * 2048
        existing = {BAGGAGE_HEADER: existing_baggage, "Authorization": "test-key"}
        if length > 1024:
            with pytest.raises(ValueError, match="1024"):
                context.model_attribution_headers(existing)
        else:
            result = context.model_attribution_headers(existing)
            assert len(result[BAGGAGE_HEADER]) == length
            assert result[BAGGAGE_HEADER] == f"{encoded},{baggage}"
        assert existing == {BAGGAGE_HEADER: existing_baggage, "Authorization": "test-key"}

    def test_subject_free_call_preserves_unrelated_baggage_outside_attribution_limits(self) -> None:
        baggage = "foundry.example=" + "x" * 2048
        existing = {BAGGAGE_HEADER: baggage + ",Foundry.Original_Subject;stale=1"}
        assert FoundryAgentRequestContext().model_attribution_headers(existing) == {BAGGAGE_HEADER: baggage}

    def test_subject_precedes_baggage_that_can_expand_during_transport_normalization(self) -> None:
        context = FoundryAgentRequestContext(
            original_subject=FoundryOriginalSubject(oid="current", tid="tenant", idtype="user")
        )
        baggage = "foundry.keep0=" + "!" * 200 + ",foundry.keep1=" + "!" * 120
        existing = {BAGGAGE_HEADER: baggage}
        encoded = context.model_attribution_headers()[BAGGAGE_HEADER]
        result = context.model_attribution_headers(existing)
        assert result[BAGGAGE_HEADER] == f"{encoded},{baggage}"
        assert len(result[BAGGAGE_HEADER]) < 1024
        assert existing == {BAGGAGE_HEADER: baggage}

    def test_baggage_encodes_full_quoted_tuple_exactly_once(self) -> None:
        subject = FoundryOriginalSubject(oid='a%2C\\",=b', tid="tenant", idtype="user")
        result = FoundryAgentRequestContext(original_subject=subject).model_attribution_headers()
        encoded = result[BAGGAGE_HEADER].split("=", 1)[1]
        assert "%252C" in encoded
        assert unquote(encoded) == result[SUBJECT_HEADER]
        assert FoundryOriginalSubject.from_headers({SUBJECT_HEADER: unquote(encoded)}) == subject
        assert len(result[BAGGAGE_HEADER].split(",")) == 1

    def test_typical_complete_tuple_fits_existing_carrier_limits(self) -> None:
        subject = FoundryOriginalSubject(
            oid="11111111-2222-3333-4444-555555555555",
            tid="aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
            idtype="user",
        )
        result = FoundryAgentRequestContext(original_subject=subject).model_attribution_headers()
        assert len(result[BAGGAGE_HEADER]) <= 1024
        assert len(unquote(result[BAGGAGE_HEADER].split("=", 1)[1])) <= 256

    def test_retired_headers_are_not_used_as_fallback_or_mixed_into_the_snapshot(self) -> None:
        retired = {
            "x-ms-original-subject-oid": "retired-oid",
            "x-ms-original-subject-tid": "retired-tid",
            "x-ms-original-subject-idtype": "app",
        }
        assert FoundryOriginalSubject.from_headers(retired) is None
        subject = FoundryOriginalSubject.from_headers({**retired, **SUBJECT_HEADERS})
        assert subject == FoundryOriginalSubject(oid="original-oid", tid="original-tid", idtype="user")

    def test_snapshot_is_immutable_and_does_not_print_identifiers(self) -> None:
        subject = FoundryOriginalSubject(oid="private-original-oid", tid="tenant", idtype="user")
        with pytest.raises(FrozenInstanceError):
            setattr(subject, "oid", "different")
        assert "private-original-oid" not in repr(subject)

    @pytest.mark.asyncio
    async def test_shared_client_parallel_users_and_retries_keep_per_call_headers(self) -> None:
        both_bound = asyncio.Event()
        bound = 0
        attempts: dict[str, int] = {}
        observed: list[httpx.Headers] = []

        def receive(request: httpx.Request) -> httpx.Response:
            observed.append(request.headers.copy())
            subject = FoundryOriginalSubject.from_headers(request.headers)
            assert subject is not None and subject.oid is not None
            oid = subject.oid
            attempts[oid] = attempts.get(oid, 0) + 1
            return httpx.Response(503 if attempts[oid] == 1 else 200)

        async with httpx.AsyncClient(
            transport=httpx.MockTransport(receive),
            headers={"Authorization": "Bearer model-agent-token"},
        ) as client:
            client.headers[BAGGAGE_HEADER] = "application=shared"

            async def invoke(user: str) -> None:
                nonlocal bound
                token = set_request_context(
                    FoundryAgentRequestContext(
                        original_subject=FoundryOriginalSubject(oid=user, tid=f"tenant-{user}", idtype="user"),
                        call_id=f"call-{user}",
                    )
                )
                try:
                    bound += 1
                    if bound == 2:
                        both_bound.set()
                    await both_bound.wait()
                    for _ in range(2):
                        response = await client.post(
                            "https://model.test/responses",
                            headers=get_request_context().model_attribution_headers(client.headers),
                            json={"input": "test"},
                        )
                    assert response.status_code == 200
                finally:
                    reset_request_context(token)
                assert get_request_context().original_subject is None

            await asyncio.gather(invoke("alice"), invoke("bob"))
            assert SUBJECT_HEADER not in client.headers
            assert client.headers[BAGGAGE_HEADER] == "application=shared"

        assert attempts == {"alice": 2, "bob": 2}
        for headers in observed:
            subject = FoundryOriginalSubject.from_headers(headers)
            assert subject is not None
            user = subject.oid
            assert subject.tid == f"tenant-{user}"
            assert headers[FOUNDRY_CALL_ID] == f"call-{user}"
            baggage = headers[BAGGAGE_HEADER].split(",")
            assert baggage[1] == "application=shared"
            assert unquote(baggage[0].split("=", 1)[1]) == headers[SUBJECT_HEADER]
            assert headers["authorization"] == "Bearer model-agent-token"
            assert USER_ID not in headers
        assert get_request_context().original_subject is None


class TestRequestContext:
    def test_default_is_empty(self) -> None:
        ctx = get_request_context()
        assert ctx.call_id is None
        assert ctx.user_id is None
        assert ctx.session_id is None

    def test_set_and_reset(self) -> None:
        token = set_request_context(FoundryAgentRequestContext(call_id="c1", user_id="u1", session_id="s1"))
        try:
            ctx = get_request_context()
            assert ctx.call_id == "c1"
            assert ctx.user_id == "u1"
            assert ctx.session_id == "s1"
        finally:
            reset_request_context(token)
        assert get_request_context().call_id is None

    def test_platform_headers_includes_call_id(self) -> None:
        ctx = FoundryAgentRequestContext(call_id="cid", user_id="uid")
        headers = ctx.platform_headers()
        # Only the call ID is forwarded to 1P services; user_id is not.
        assert headers == {FOUNDRY_CALL_ID: "cid"}
        assert USER_ID not in headers

    def test_platform_headers_omits_absent_values(self) -> None:
        assert FoundryAgentRequestContext().platform_headers() == {}
        # user_id alone never produces an outbound header.
        assert FoundryAgentRequestContext(user_id="uid").platform_headers() == {}
        assert FoundryAgentRequestContext(call_id="cid").platform_headers() == {FOUNDRY_CALL_ID: "cid"}

    def test_context_propagates_into_child_task(self) -> None:
        async def _run() -> FoundryAgentRequestContext:
            set_request_context(FoundryAgentRequestContext(call_id="task-cid", user_id="task-uid"))

            async def _child() -> FoundryAgentRequestContext:
                return get_request_context()

            # Child task created in this scope inherits the current context.
            return await asyncio.create_task(_child())

        ctx = asyncio.run(_run())
        assert ctx.call_id == "task-cid"
        assert ctx.user_id == "task-uid"
