# pylint: disable=line-too-long,useless-suppression
# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------

"""
Tests for the to_llm_input helper function.

Covers:
  1. Import and public API surface
  2. Error handling (TypeError, empty/None results)
  3. Field resolution (_resolve_fields) for all field types
  4. Single document with page markers (span-based and PageBreak fallback)
  5. Single audio/video with time range
  6. Multi-segment audio/video separated by *****
  7. Document classification hierarchy (parent skipped, children rendered)
  8. Parameter combinations (include_fields, include_markdown, metadata)
  9. YAML front matter key ordering
  10. Edge cases (no fields, no markdown, None field values)
"""

import pytest

from azure.ai.contentunderstanding import to_llm_input
from azure.ai.contentunderstanding._helpers import _resolve_fields
from azure.ai.contentunderstanding.models import (
    AnalysisResult,
    AudioVisualContent,
    DocumentContent,
    DocumentContentSegment,
    DocumentPage,
    ContentSpan,
    StringField,
    IntegerField,
    NumberField,
    BooleanField,
    DateField,
    TimeField,
    ArrayField,
    ObjectField,
    JsonField,
)


# ---------------------------------------------------------------------------
# Fixtures / helpers
# ---------------------------------------------------------------------------

def _make_invoice_doc(**kwargs):
    """Create a simple invoice DocumentContent for reuse."""
    defaults = dict(
        kind="document",
        markdown="CONTOSO LTD.\n\n# INVOICE\n\nAmount: $165.00",
        fields={
            "VendorName": StringField(type="string", value_string="CONTOSO LTD."),
            "InvoiceDate": DateField(type="date", value_date="2019-11-15"),
            "Amount": NumberField(type="number", value_number=165),
        },
        start_page_number=1,
        end_page_number=1,
    )
    defaults.update(kwargs)
    return DocumentContent(**defaults)


def _make_result(contents, warnings=None):
    return AnalysisResult(contents=contents, warnings=warnings or [])


# ===========================================================================
# 1. Import and public API
# ===========================================================================

class TestPublicAPI:

    def test_importable_from_package(self):
        from azure.ai.contentunderstanding import to_llm_input as fn
        assert callable(fn)

    def test_in_package_all(self):
        import azure.ai.contentunderstanding as pkg
        assert "to_llm_input" in pkg.__all__


# ===========================================================================
# 2. Error handling
# ===========================================================================

class TestErrorHandling:

    def test_type_error_on_string(self):
        with pytest.raises(TypeError, match="Expected AnalysisResult"):
            to_llm_input("not a result")

    def test_type_error_on_none(self):
        with pytest.raises(TypeError, match="Expected AnalysisResult"):
            to_llm_input(None)

    def test_type_error_on_dict(self):
        with pytest.raises(TypeError, match="Expected AnalysisResult"):
            to_llm_input({"contents": []})

    def test_empty_contents_list(self):
        result = _make_result(contents=[])
        assert to_llm_input(result) == ""

    def test_none_contents(self):
        result = _make_result(contents=None)
        assert to_llm_input(result) == ""


# ===========================================================================
# 3. Field resolution
# ===========================================================================

class TestResolveFields:

    def test_string_field(self):
        fields = {"Name": StringField(type="string", value_string="Alice")}
        assert _resolve_fields(fields) == {"Name": "Alice"}

    def test_integer_field(self):
        fields = {"Count": IntegerField(type="integer", value_integer=42)}
        assert _resolve_fields(fields) == {"Count": 42}

    def test_number_field(self):
        fields = {"Price": NumberField(type="number", value_number=9.99)}
        assert _resolve_fields(fields) == {"Price": 9.99}

    def test_boolean_field(self):
        fields = {"Active": BooleanField(type="boolean", value_boolean=True)}
        assert _resolve_fields(fields) == {"Active": True}

    def test_date_field(self):
        fields = {"Date": DateField(type="date", value_date="2019-11-15")}
        resolved = _resolve_fields(fields)
        # Date fields are converted to ISO string
        assert resolved["Date"] == "2019-11-15"

    def test_time_field(self):
        fields = {"Time": TimeField(type="time", value_time="14:30:00")}
        resolved = _resolve_fields(fields)
        assert resolved["Time"] == "14:30:00"

    def test_object_field(self):
        fields = {
            "TotalAmount": ObjectField(
                type="object",
                value_object={
                    "Amount": NumberField(type="number", value_number=165),
                    "CurrencyCode": StringField(type="string", value_string="USD"),
                },
            )
        }
        resolved = _resolve_fields(fields)
        assert resolved["TotalAmount"] == {"Amount": 165, "CurrencyCode": "USD"}

    def test_array_field(self):
        fields = {
            "Items": ArrayField(
                type="array",
                value_array=[
                    ObjectField(
                        type="object",
                        value_object={
                            "Name": StringField(type="string", value_string="Widget"),
                            "Qty": IntegerField(type="integer", value_integer=3),
                        },
                    ),
                    ObjectField(
                        type="object",
                        value_object={
                            "Name": StringField(type="string", value_string="Gadget"),
                            "Qty": IntegerField(type="integer", value_integer=1),
                        },
                    ),
                ],
            )
        }
        resolved = _resolve_fields(fields)
        assert resolved["Items"] == [
            {"Name": "Widget", "Qty": 3},
            {"Name": "Gadget", "Qty": 1},
        ]

    def test_json_field(self):
        fields = {"Data": JsonField(type="json", value_json={"key": "val"})}
        resolved = _resolve_fields(fields)
        assert resolved["Data"] == {"key": "val"}

    def test_none_value_omitted(self):
        fields = {
            "Present": StringField(type="string", value_string="yes"),
            "Missing": StringField(type="string", value_string=None),
        }
        resolved = _resolve_fields(fields)
        assert "Present" in resolved
        assert "Missing" not in resolved

    def test_nested_object_in_array(self):
        fields = {
            "Items": ArrayField(
                type="array",
                value_array=[
                    ObjectField(
                        type="object",
                        value_object={
                            "Sub": ObjectField(
                                type="object",
                                value_object={
                                    "Deep": StringField(type="string", value_string="val"),
                                },
                            ),
                        },
                    ),
                ],
            )
        }
        resolved = _resolve_fields(fields)
        assert resolved["Items"] == [{"Sub": {"Deep": "val"}}]

    def test_object_field_none_value_object(self):
        fields = {"Addr": ObjectField(type="object", value_object=None)}
        resolved = _resolve_fields(fields)
        assert "Addr" not in resolved

    def test_nested_object_within_object(self):
        """Object containing another object: BillingAddress → Street → {Name, Number}."""
        fields = {
            "BillingAddress": ObjectField(
                type="object",
                value_object={
                    "City": StringField(type="string", value_string="Redmond"),
                    "Street": ObjectField(
                        type="object",
                        value_object={
                            "Name": StringField(type="string", value_string="Main St"),
                            "Number": IntegerField(type="integer", value_integer=123),
                        },
                    ),
                },
            )
        }
        resolved = _resolve_fields(fields)
        assert resolved == {
            "BillingAddress": {
                "City": "Redmond",
                "Street": {
                    "Name": "Main St",
                    "Number": 123,
                },
            }
        }

    def test_empty_fields_dict(self):
        assert _resolve_fields({}) == {}


# ===========================================================================
# 4. Single document with page markers
# ===========================================================================

class TestSingleDocument:

    def test_basic_document(self):
        doc = _make_invoice_doc()
        output = to_llm_input(_make_result([doc]))
        assert "---" in output
        assert "contentType: document" in output
        assert "VendorName: CONTOSO LTD." in output
        assert "InvoiceDate: '2019-11-15'" in output
        assert "Amount: 165" in output
        assert "CONTOSO LTD." in output
        assert "# INVOICE" in output

    def test_page_markers_from_spans(self):
        doc = DocumentContent(
            kind="document",
            markdown="First page text.\n\nSecond page text.",
            start_page_number=1,
            end_page_number=2,
            pages=[
                DocumentPage(page_number=1, spans=[ContentSpan(offset=0, length=16)]),
                DocumentPage(page_number=2, spans=[ContentSpan(offset=18, length=17)]),
            ],
        )
        output = to_llm_input(_make_result([doc]))
        assert "<!-- page 1 -->" in output
        assert "<!-- page 2 -->" in output

    def test_page_markers_from_pagebreak_fallback(self):
        doc = DocumentContent(
            kind="document",
            markdown="Page 1 content.\n\n<!-- PageBreak -->\n\nPage 2 content.",
            start_page_number=1,
            end_page_number=2,
        )
        output = to_llm_input(_make_result([doc]))
        assert "<!-- page 1 -->" in output
        assert "<!-- page 2 -->" in output
        assert "<!-- PageBreak -->" not in output

    def test_page_markers_respect_start_page_number(self):
        """When analyzing a page range (e.g. pages 3-5), markers use the original page numbers."""
        doc = DocumentContent(
            kind="document",
            markdown="Content A.\n\n<!-- PageBreak -->\n\nContent B.",
            start_page_number=3,
            end_page_number=4,
        )
        output = to_llm_input(_make_result([doc]))
        assert "<!-- page 3 -->" in output
        assert "<!-- page 4 -->" in output

    def test_pages_single_page_format(self):
        doc = _make_invoice_doc(start_page_number=1, end_page_number=1)
        output = to_llm_input(_make_result([doc]))
        assert "pages: 1" in output

    def test_pages_range_format(self):
        doc = _make_invoice_doc(start_page_number=2, end_page_number=5)
        output = to_llm_input(_make_result([doc]))
        assert "pages: 2-5" in output


# ===========================================================================
# 5. Single audio/video
# ===========================================================================

class TestSingleAudioVisual:

    def test_basic_av(self):
        av = AudioVisualContent(
            kind="audioVisual",
            markdown="Speaker 1: Hello world.",
            fields={"Summary": StringField(type="string", value_string="A greeting.")},
            start_time_ms=0,
            end_time_ms=30000,
        )
        output = to_llm_input(_make_result([av]))
        assert "contentType: audioVisual" in output
        # Single AV: no timeRange per design doc
        assert "timeRange" not in output
        assert "Summary: A greeting." in output
        assert "Speaker 1: Hello world." in output

    def test_av_time_format_only_in_multi_segment(self):
        """Time format is MM:SS – MM:SS, but only appears for multi-segment AV."""
        seg1 = AudioVisualContent(
            kind="audioVisual",
            markdown="Segment 1.",
            start_time_ms=62573,
            end_time_ms=125000,
        )
        seg2 = AudioVisualContent(
            kind="audioVisual",
            markdown="Segment 2.",
            start_time_ms=125000,
            end_time_ms=200000,
        )
        output = to_llm_input(_make_result([seg1, seg2]))
        # 62573ms = 1:02, 125000ms = 2:05, 200000ms = 3:20
        assert "timeRange: 01:02 – 02:05" in output
        assert "timeRange: 02:05 – 03:20" in output


# ===========================================================================
# 6. Multi-segment audio/video
# ===========================================================================

class TestMultiSegmentAV:

    def test_segments_separated_by_separator(self):
        seg1 = AudioVisualContent(
            kind="audioVisual",
            markdown="Speaker 1: First segment.",
            fields={"Summary": StringField(type="string", value_string="Seg 1.")},
            start_time_ms=0,
            end_time_ms=15000,
        )
        seg2 = AudioVisualContent(
            kind="audioVisual",
            markdown="Speaker 2: Second segment.",
            fields={"Summary": StringField(type="string", value_string="Seg 2.")},
            start_time_ms=15500,
            end_time_ms=43000,
        )
        output = to_llm_input(_make_result([seg1, seg2]))
        assert "*****" in output
        # Both segments present
        assert "Speaker 1: First segment." in output
        assert "Speaker 2: Second segment." in output
        # Both have their own front matter
        assert output.count("contentType: audioVisual") == 2
        assert "timeRange: 00:00 \u2013 00:15" in output
        assert "timeRange: 00:15 \u2013 00:43" in output

    def test_metadata_repeated_per_segment(self):
        seg1 = AudioVisualContent(kind="audioVisual", markdown="A", start_time_ms=0, end_time_ms=10000)
        seg2 = AudioVisualContent(kind="audioVisual", markdown="B", start_time_ms=10000, end_time_ms=20000)
        output = to_llm_input(_make_result([seg1, seg2]), metadata={"source": "clip.mp4"})
        assert output.count("source: clip.mp4") == 2


# ===========================================================================
# 7. Document classification hierarchy
# ===========================================================================

class TestClassificationHierarchy:

    def _make_classification_result(self):
        """All segments routed — both have top-level children with fields."""
        parent = DocumentContent(
            kind="document",
            path="input1",
            markdown="Invoice text.\n\nBank text.",
            start_page_number=1,
            end_page_number=3,
            segments=[
                DocumentContentSegment(
                    segment_id="segment1", category="Invoice",
                    span=ContentSpan(offset=0, length=13),
                    start_page_number=1, end_page_number=1,
                ),
                DocumentContentSegment(
                    segment_id="segment2", category="BankStatement",
                    span=ContentSpan(offset=15, length=10),
                    start_page_number=2, end_page_number=3,
                ),
            ],
        )
        child1 = DocumentContent(
            kind="document",
            path="input1/segment1",
            category="Invoice",
            markdown="Invoice text.",
            fields={"Vendor": StringField(type="string", value_string="CONTOSO")},
            start_page_number=1,
            end_page_number=1,
        )
        child2 = DocumentContent(
            kind="document",
            path="input1/segment2",
            category="BankStatement",
            markdown="Bank text.",
            fields={"Bank": StringField(type="string", value_string="Contoso Bank")},
            start_page_number=2,
            end_page_number=3,
        )
        return _make_result([parent, child1, child2])

    def test_parent_skipped(self):
        output = to_llm_input(self._make_classification_result())
        # Parent has "Invoice text.\n\nBank text." — this combined string should not appear
        assert "Invoice text.\n\nBank text." not in output

    def test_children_rendered(self):
        output = to_llm_input(self._make_classification_result())
        assert "category: Invoice" in output
        assert "category: BankStatement" in output
        assert "Vendor: CONTOSO" in output
        assert "Bank: Contoso Bank" in output

    def test_children_separated_by_separator(self):
        output = to_llm_input(self._make_classification_result())
        assert "*****" in output

    def test_children_have_pages(self):
        output = to_llm_input(self._make_classification_result())
        assert "pages: 1" in output
        assert "pages: 2-3" in output

    def test_no_routing_expands_all_segments(self):
        """No top-level children — all segments expanded from parent."""
        parent = DocumentContent(
            kind="document",
            path="input1",
            markdown="Invoice text.\n\nBank text.",
            start_page_number=1,
            end_page_number=3,
            segments=[
                DocumentContentSegment(
                    segment_id="segment1", category="Invoice",
                    span=ContentSpan(offset=0, length=13),
                    start_page_number=1, end_page_number=1,
                ),
                DocumentContentSegment(
                    segment_id="segment2", category="BankStatement",
                    span=ContentSpan(offset=15, length=10),
                    start_page_number=2, end_page_number=3,
                ),
            ],
        )
        result = _make_result([parent])
        output = to_llm_input(result)
        assert "category: Invoice" in output
        assert "category: BankStatement" in output
        assert "Invoice text." in output
        assert "Bank text." in output
        assert "*****" in output

    def test_partial_routing_mixes_expanded_and_routed(self):
        """Only Invoice is routed; BankStatement expanded from parent."""
        parent = DocumentContent(
            kind="document",
            path="input1",
            markdown="Invoice text.\n\nBank text.",
            start_page_number=1,
            end_page_number=3,
            segments=[
                DocumentContentSegment(
                    segment_id="segment1", category="Invoice",
                    span=ContentSpan(offset=0, length=13),
                    start_page_number=1, end_page_number=1,
                ),
                DocumentContentSegment(
                    segment_id="segment2", category="BankStatement",
                    span=ContentSpan(offset=15, length=10),
                    start_page_number=2, end_page_number=3,
                ),
            ],
        )
        routed_invoice = DocumentContent(
            kind="document",
            path="input1/segment1",
            category="Invoice",
            markdown="Invoice text.",
            fields={"Vendor": StringField(type="string", value_string="CONTOSO")},
            start_page_number=1,
            end_page_number=1,
        )
        result = _make_result([parent, routed_invoice])
        output = to_llm_input(result)
        blocks = output.split("*****")
        assert len(blocks) == 2
        # Invoice block has fields (from routed content)
        assert "Vendor: CONTOSO" in output
        # BankStatement block expanded from parent (no fields)
        assert "category: BankStatement" in output
        assert "Bank text." in output

    def test_output_sorted_by_page_number(self):
        """Routed content at end of contents list still appears first if page 1."""
        parent = DocumentContent(
            kind="document",
            path="input1",
            markdown="Page1.\n\nPage2.\n\nPage3.",
            start_page_number=1,
            end_page_number=3,
            segments=[
                DocumentContentSegment(
                    segment_id="segment1", category="TypeA",
                    span=ContentSpan(offset=0, length=6),
                    start_page_number=1, end_page_number=1,
                ),
                DocumentContentSegment(
                    segment_id="segment2", category="TypeB",
                    span=ContentSpan(offset=8, length=6),
                    start_page_number=2, end_page_number=2,
                ),
                DocumentContentSegment(
                    segment_id="segment3", category="TypeC",
                    span=ContentSpan(offset=16, length=6),
                    start_page_number=3, end_page_number=3,
                ),
            ],
        )
        # Routed TypeA comes last in contents list
        routed = DocumentContent(
            kind="document",
            path="input1/segment1",
            category="TypeA",
            markdown="Page1.",
            fields={"Key": StringField(type="string", value_string="val")},
            start_page_number=1,
            end_page_number=1,
        )
        result = _make_result([parent, routed])
        output = to_llm_input(result)
        blocks = output.split("*****")
        assert len(blocks) == 3
        # First block should be TypeA (page 1), not TypeB (page 2)
        assert "category: TypeA" in blocks[0]
        assert "category: TypeB" in blocks[1]
        assert "category: TypeC" in blocks[2]

    def test_path_based_deduplication_not_category_based(self):
        """Two segments with same category but different segment IDs — only the routed one is deduplicated."""
        parent = DocumentContent(
            kind="document",
            path="input1",
            markdown="Inv1.\n\nInv2.",
            start_page_number=1,
            end_page_number=2,
            segments=[
                DocumentContentSegment(
                    segment_id="segment1", category="Invoice",
                    span=ContentSpan(offset=0, length=5),
                    start_page_number=1, end_page_number=1,
                ),
                DocumentContentSegment(
                    segment_id="segment2", category="Invoice",
                    span=ContentSpan(offset=7, length=5),
                    start_page_number=2, end_page_number=2,
                ),
            ],
        )
        # Only segment1 is routed
        routed = DocumentContent(
            kind="document",
            path="input1/segment1",
            category="Invoice",
            markdown="Inv1.",
            fields={"Vendor": StringField(type="string", value_string="A")},
            start_page_number=1,
            end_page_number=1,
        )
        result = _make_result([parent, routed])
        output = to_llm_input(result)
        blocks = output.split("*****")
        # Should have 2 blocks: routed segment1 (with fields) + expanded segment2 (no fields)
        assert len(blocks) == 2
        assert "Vendor: A" in blocks[0]
        # Second block is expanded from parent — no fields
        assert "Inv2." in blocks[1]
        assert "fields:" not in blocks[1]


# ===========================================================================
# 8. Parameter combinations
# ===========================================================================

class TestParameterCombinations:

    def test_include_fields_false(self):
        doc = _make_invoice_doc()
        output = to_llm_input(_make_result([doc]), include_fields=False)
        assert "fields:" not in output
        assert "VendorName" not in output
        assert "CONTOSO LTD." in output  # markdown body still present
        assert "contentType: document" in output

    def test_include_markdown_false(self):
        doc = _make_invoice_doc()
        output = to_llm_input(_make_result([doc]), include_markdown=False)
        assert "# INVOICE" not in output
        assert "VendorName: CONTOSO LTD." in output
        assert "contentType: document" in output

    def test_both_false_gives_frontmatter_only(self):
        doc = _make_invoice_doc()
        output = to_llm_input(_make_result([doc]), include_fields=False, include_markdown=False)
        assert "contentType: document" in output
        assert "fields:" not in output
        assert "INVOICE" not in output

    def test_metadata_in_output(self):
        doc = _make_invoice_doc()
        output = to_llm_input(
            _make_result([doc]),
            metadata={"source": "invoice.pdf", "batch_id": "B-123"},
        )
        assert "source: invoice.pdf" in output
        assert "batch_id: B-123" in output

    def test_metadata_position_after_content_type(self):
        doc = _make_invoice_doc()
        output = to_llm_input(
            _make_result([doc]),
            metadata={"source": "test.pdf"},
        )
        lines = output.split("\n")
        ct_idx = next(i for i, l in enumerate(lines) if "contentType:" in l)
        src_idx = next(i for i, l in enumerate(lines) if "source:" in l)
        fields_idx = next(i for i, l in enumerate(lines) if l.strip() == "fields:")
        assert ct_idx < src_idx < fields_idx

    @pytest.mark.parametrize(
        "reserved_key",
        ["contentType", "timeRange", "category", "pages", "fields", "rai_warnings"],
    )
    def test_reserved_metadata_key_raises(self, reserved_key):
        doc = _make_invoice_doc()

        with pytest.raises(ValueError, match="reserved front matter key"):
            to_llm_input(_make_result([doc]), metadata={reserved_key: "custom"})

    def test_non_classification_documents_preserve_input_order(self):
        doc_page_2 = DocumentContent(
            kind="document",
            markdown="Second input document.",
            start_page_number=2,
            end_page_number=2,
        )
        doc_page_1 = DocumentContent(
            kind="document",
            markdown="First input document.",
            start_page_number=1,
            end_page_number=1,
        )

        output = to_llm_input(_make_result([doc_page_2, doc_page_1]))

        assert output.index("Second input document.") < output.index("First input document.")


# ===========================================================================
# 9. YAML front matter structure
# ===========================================================================

class TestFrontMatter:

    def test_delimiters_present(self):
        doc = _make_invoice_doc()
        output = to_llm_input(_make_result([doc]))
        assert output.startswith("---\n")
        assert "\n---\n" in output

    def test_content_type_always_present(self):
        doc = DocumentContent(kind="document", markdown="text")
        output = to_llm_input(_make_result([doc]))
        assert "contentType: document" in output

    def test_key_order(self):
        """Verify front matter key order: contentType → metadata → timeRange → category → pages → fields."""
        doc = DocumentContent(
            kind="document",
            category="Invoice",
            markdown="text",
            fields={"X": StringField(type="string", value_string="val")},
            start_page_number=1,
            end_page_number=1,
        )
        output = to_llm_input(
            _make_result([doc]),
            metadata={"source": "f.pdf"},
        )
        lines = output.split("\n")
        positions = {}
        for i, line in enumerate(lines):
            for key in ["contentType:", "source:", "category:", "pages:", "fields:"]:
                if line.startswith(key) or line.strip().startswith(key):
                    positions[key] = i
                    break

        assert positions["contentType:"] < positions["source:"]
        assert positions["source:"] < positions["category:"]
        assert positions["category:"] < positions["pages:"]
        assert positions["pages:"] < positions["fields:"]

    def test_date_values_quoted(self):
        doc = DocumentContent(
            kind="document",
            fields={"D": DateField(type="date", value_date="2024-01-01")},
        )
        output = to_llm_input(_make_result([doc]))
        assert "'2024-01-01'" in output

    def test_integer_number_no_decimal(self):
        doc = DocumentContent(
            kind="document",
            fields={"N": NumberField(type="number", value_number=42)},
        )
        output = to_llm_input(_make_result([doc]))
        assert "N: 42" in output
        assert "N: 42.0" not in output

    def test_fractional_number_keeps_decimal(self):
        doc = DocumentContent(
            kind="document",
            fields={"Price": NumberField(type="number", value_number=9.99)},
        )
        output = to_llm_input(_make_result([doc]))
        assert "Price: 9.99" in output


# ===========================================================================
# 10. Edge cases
# ===========================================================================

class TestEdgeCases:

    def test_no_fields_content(self):
        doc = DocumentContent(kind="document", markdown="Just text.", start_page_number=1, end_page_number=1)
        output = to_llm_input(_make_result([doc]))
        assert "fields:" not in output
        assert "Just text." in output

    def test_no_markdown_content(self):
        doc = DocumentContent(
            kind="document",
            fields={"Name": StringField(type="string", value_string="Test")},
            start_page_number=1,
            end_page_number=1,
        )
        output = to_llm_input(_make_result([doc]))
        assert "Name: Test" in output
        # Should end with --- (no markdown body)
        assert output.rstrip().endswith("---")

    def test_empty_fields_dict(self):
        doc = DocumentContent(kind="document", markdown="text", fields={})
        output = to_llm_input(_make_result([doc]))
        assert "fields:" not in output

    def test_no_separator_for_single_content(self):
        doc = _make_invoice_doc()
        output = to_llm_input(_make_result([doc]))
        assert "*****" not in output

    def test_boolean_field_in_yaml(self):
        doc = DocumentContent(
            kind="document",
            fields={"Flag": BooleanField(type="boolean", value_boolean=True)},
        )
        output = to_llm_input(_make_result([doc]))
        assert "Flag: true" in output

    def test_array_of_strings_in_yaml(self):
        doc = DocumentContent(
            kind="document",
            fields={
                "Topics": ArrayField(
                    type="array",
                    value_array=[
                        StringField(type="string", value_string="Finance"),
                        StringField(type="string", value_string="Legal"),
                    ],
                ),
            },
        )
        output = to_llm_input(_make_result([doc]))
        assert "- Finance" in output
        assert "- Legal" in output

    def test_special_yaml_characters_quoted(self):
        doc = DocumentContent(
            kind="document",
            fields={
                "Note": StringField(type="string", value_string="yes"),
                "Colon": StringField(type="string", value_string="key: value"),
            },
        )
        output = to_llm_input(_make_result([doc]))
        # "yes" is a YAML boolean keyword, should be quoted
        assert "'yes'" in output
        # "key: value" contains colon-space, should be quoted
        assert "'key: value'" in output

    def test_result_level_warnings_included(self):
        from azure.core.exceptions import ODataV4Format
        doc = _make_invoice_doc()
        warning = ODataV4Format({"code": "ContentWarning", "message": "Potentially sensitive content."})
        result = AnalysisResult(contents=[doc], warnings=[warning])
        output = to_llm_input(result)
        assert "rai_warnings:" in output
        assert "ContentWarning" in output
        assert "Potentially sensitive content." in output

    def test_warnings_present_regardless_of_include_flags(self):
        from azure.core.exceptions import ODataV4Format
        doc = _make_invoice_doc()
        warning = ODataV4Format({"code": "W1", "message": "msg"})
        result = AnalysisResult(contents=[doc], warnings=[warning])
        output = to_llm_input(result, include_fields=False, include_markdown=False)
        assert "rai_warnings:" in output

    def test_empty_string_field_value_quoted(self):
        doc = DocumentContent(
            kind="document",
            fields={"Note": StringField(type="string", value_string="")},
        )
        output = to_llm_input(_make_result([doc]))
        assert "Note: ''" in output


# ===========================================================================
# 11. Real CU output patterns (from sample_cu_output files)
# ===========================================================================

class TestRealCUPatterns:
    """Tests modeled after actual CU service responses in sample_cu_output/."""

    def test_invoice_nested_object_and_array_fields(self):
        """Matches invoice.pdf.json: object fields (TotalAmount) and array of objects (LineItems)."""
        doc = DocumentContent(
            kind="document",
            markdown="CONTOSO LTD.\n\n# INVOICE\nContoso Headquarters\n123 456th St\nNew York, NY 10001",
            fields={
                "VendorName": StringField(type="string", value_string="CONTOSO LTD."),
                "InvoiceDate": DateField(type="date", value_date="2019-11-15"),
                "TotalAmount": ObjectField(
                    type="object",
                    value_object={
                        "Amount": NumberField(type="number", value_number=165),
                        "CurrencyCode": StringField(type="string", value_string="USD"),
                    },
                ),
                "LineItems": ArrayField(
                    type="array",
                    value_array=[
                        ObjectField(type="object", value_object={
                            "Description": StringField(type="string", value_string="Consulting Services"),
                            "Quantity": NumberField(type="number", value_number=2),
                            "TotalAmount": ObjectField(type="object", value_object={
                                "Amount": NumberField(type="number", value_number=80),
                                "CurrencyCode": StringField(type="string", value_string="USD"),
                            }),
                        }),
                        ObjectField(type="object", value_object={
                            "Description": StringField(type="string", value_string="Document Fee"),
                            "Quantity": NumberField(type="number", value_number=3),
                            "TotalAmount": ObjectField(type="object", value_object={
                                "Amount": NumberField(type="number", value_number=85),
                                "CurrencyCode": StringField(type="string", value_string="USD"),
                            }),
                        }),
                    ],
                ),
            },
            start_page_number=1,
            end_page_number=1,
            pages=[DocumentPage(page_number=1, spans=[ContentSpan(offset=0, length=76)])],
        )
        output = to_llm_input(_make_result([doc]), metadata={"source": "invoice.pdf"})
        assert "VendorName: CONTOSO LTD." in output
        assert "InvoiceDate: '2019-11-15'" in output
        # Nested object
        assert "Amount: 165" in output
        assert "CurrencyCode: USD" in output
        # Array of objects with nested objects
        assert "- Description: Consulting Services" in output
        assert "- Description: Document Fee" in output

    def test_call_center_audio_with_complex_fields(self):
        """Matches post_call_analysis_en_us.mp3.json: arrays of strings and objects."""
        av = AudioVisualContent(
            kind="audioVisual",
            markdown="# Audio: 00:00.000 => 01:02.573\n\nTranscript\n```\nAgent 1: Good afternoon...\nCustomer 1: I need help.\n```",
            fields={
                "Summary": StringField(type="string", value_string="Customer called about a transfer."),
                "Topics": ArrayField(type="array", value_array=[
                    StringField(type="string", value_string="Money transfer"),
                    StringField(type="string", value_string="Certificate of deposit"),
                    StringField(type="string", value_string="Customer service"),
                ]),
                "People": ArrayField(type="array", value_array=[
                    ObjectField(type="object", value_object={
                        "Name": StringField(type="string", value_string="Mary Smith"),
                        "Role": StringField(type="string", value_string="Customer"),
                    }),
                    ObjectField(type="object", value_object={
                        "Name": StringField(type="string", value_string="Agent"),
                        "Role": StringField(type="string", value_string="Agent"),
                    }),
                ]),
                "Sentiment": StringField(type="string", value_string="Positive"),
                "Companies": ArrayField(type="array", value_array=[
                    StringField(type="string", value_string="Contoso"),
                ]),
            },
            start_time_ms=0,
            end_time_ms=62573,
        )
        output = to_llm_input(_make_result([av]), metadata={"source": "call.wav"})
        assert "contentType: audioVisual" in output
        # Single AV: no timeRange per design doc
        assert "timeRange" not in output
        assert "Summary: Customer called about a transfer." in output
        # Array of strings
        assert "- Money transfer" in output
        assert "- Certificate of deposit" in output
        # Array of objects
        assert "Name: Mary Smith" in output
        assert "Role: Customer" in output
        assert "Sentiment: Positive" in output
        assert "- Contoso" in output

    def test_video_three_segments(self):
        """Matches flight_simulator_search.mp4.json: 3 audioVisual segments, no path."""
        segments = [
            AudioVisualContent(
                kind="audioVisual",
                markdown="Speaker 1: When it comes to the neural TTS...",
                fields={"Summary": StringField(type="string", value_string="About TTS technology.")},
                start_time_ms=733,
                end_time_ms=15467,
            ),
            AudioVisualContent(
                kind="audioVisual",
                markdown="[key frames only, no transcript]",
                fields={"Summary": StringField(type="string", value_string="Visual transition.")},
                start_time_ms=15467,
                end_time_ms=23100,
            ),
            AudioVisualContent(
                kind="audioVisual",
                markdown="Speaker 3: What we liked about cognitive services...",
                fields={"Summary": StringField(type="string", value_string="About Azure services.")},
                start_time_ms=23100,
                end_time_ms=43233,
            ),
        ]
        output = to_llm_input(_make_result(segments), metadata={"source": "video.mp4"})
        # 3 segments, 2 separators
        assert output.count("*****") == 2
        assert output.count("contentType: audioVisual") == 3
        assert output.count("source: video.mp4") == 3
        assert "timeRange: 00:00 \u2013 00:15" in output
        assert "timeRange: 00:15 \u2013 00:23" in output
        assert "timeRange: 00:23 \u2013 00:43" in output

    def test_multipage_doc_strips_pagebreak_with_spans(self):
        """Matches mixed_financial_invoices.pdf.json: spans-based markers replace PageBreak."""
        markdown = "Page 1 content.\n\n<!-- PageBreak -->\n\nPage 2 content.\n\n<!-- PageBreak -->\n\nPage 3 content."
        # Real CU data: spans are contiguous, PageBreak text falls within the preceding page's span
        doc = DocumentContent(
            kind="document",
            markdown=markdown,
            start_page_number=1,
            end_page_number=3,
            pages=[
                DocumentPage(page_number=1, spans=[ContentSpan(offset=0, length=37)]),
                DocumentPage(page_number=2, spans=[ContentSpan(offset=37, length=37)]),
                DocumentPage(page_number=3, spans=[ContentSpan(offset=74, length=15)]),
            ],
        )
        output = to_llm_input(_make_result([doc]))
        assert "<!-- PageBreak -->" not in output
        assert "<!-- page 1 -->" in output
        assert "<!-- page 2 -->" in output
        assert "<!-- page 3 -->" in output
        assert "Page 1 content." in output
        assert "Page 2 content." in output
        assert "Page 3 content." in output

    def test_image_with_empty_page_spans_falls_back(self):
        """Matches image_analyzer_sample_search.jpg.json: pages present but spans empty."""
        doc = DocumentContent(
            kind="document",
            markdown="![image](pages/1)\n",
            fields={"Summary": StringField(type="string", value_string="A resume photo.")},
            start_page_number=1,
            end_page_number=1,
            pages=[DocumentPage(page_number=1, spans=[])],
        )
        output = to_llm_input(_make_result([doc]))
        # Should fall back to PageBreak method, which adds page 1 marker
        assert "<!-- page 1 -->" in output
        assert "![image](pages/1)" in output

    def test_document_search_png_single_page_with_spans(self):
        """Matches document_search.png.json: single page document with span covering full markdown."""
        markdown = "# IAN HANSSON\n\n## PROFILE\n\nLorem ipsum dolor sit amet."
        doc = DocumentContent(
            kind="document",
            markdown=markdown,
            fields={"Summary": StringField(type="string", value_string="A resume document.")},
            start_page_number=1,
            end_page_number=1,
            pages=[DocumentPage(page_number=1, spans=[ContentSpan(offset=0, length=len(markdown))])],
        )
        output = to_llm_input(_make_result([doc]))
        assert "<!-- page 1 -->" in output
        assert "IAN HANSSON" in output
        assert "Summary: A resume document." in output

    def test_prebuilt_read_no_fields(self):
        """Matches mixed_financial_invoices.pdf.json with prebuilt-read: no fields extracted."""
        doc = DocumentContent(
            kind="document",
            markdown="Page 1 text.\n\n<!-- PageBreak -->\n\nPage 2 text.",
            start_page_number=1,
            end_page_number=2,
            pages=[
                DocumentPage(page_number=1, spans=[ContentSpan(offset=0, length=32)]),
                DocumentPage(page_number=2, spans=[ContentSpan(offset=32, length=14)]),
            ],
        )
        output = to_llm_input(_make_result([doc]))
        assert "contentType: document" in output
        assert "fields:" not in output
        assert "<!-- page 1 -->" in output
        assert "<!-- page 2 -->" in output

    def test_metadata_keys_with_yaml_special_chars(self):
        """Metadata keys with YAML-special characters must be quoted to produce valid YAML."""
        doc = DocumentContent(kind="document", markdown="Hello")
        output = to_llm_input(
            _make_result([doc]),
            metadata={
                "with: colon": "val1",
                "with# hash": "val2",
                "- dash_start": "val3",
                "normal_key": "val4",
            },
        )
        assert "'with: colon': val1" in output
        assert "'with# hash': val2" in output
        assert "'- dash_start': val3" in output
        assert "normal_key: val4" in output

    def test_audio_search_single_segment(self):
        """Matches audio_analysis.mp3.json: single audioVisual, no path, with transcriptPhrases."""
        av = AudioVisualContent(
            kind="audioVisual",
            markdown="# Audio: 00:00.000 => 01:02.573\n\nTranscript\nSpeaker 1: Good afternoon...",
            fields={"Summary": StringField(type="string", value_string="A greeting call.")},
            start_time_ms=0,
            end_time_ms=62573,
        )
        output = to_llm_input(_make_result([av]))
        assert "contentType: audioVisual" in output
        # Single AV: no timeRange per design doc
        assert "timeRange" not in output
        assert "Summary: A greeting call." in output
        # No separator for single segment
        assert "*****" not in output

    def test_nested_dict_in_array_indentation(self):
        """Nested objects inside array items must indent children deeper than the parent key."""
        doc = DocumentContent(
            kind="document",
            fields={
                "Items": ArrayField(
                    type="array",
                    value_array=[
                        ObjectField(type="object", value_object={
                            "Name": StringField(type="string", value_string="Widget"),
                            "Cost": ObjectField(type="object", value_object={
                                "Amount": NumberField(type="number", value_number=50),
                                "Currency": StringField(type="string", value_string="USD"),
                            }),
                        }),
                    ],
                ),
            },
        )
        output = to_llm_input(_make_result([doc]))
        lines = output.split("\n")
        # Find the Cost key and its children
        for i, line in enumerate(lines):
            if "Cost:" in line:
                cost_indent = len(line) - len(line.lstrip())
                amount_line = lines[i + 1]
                amount_indent = len(amount_line) - len(amount_line.lstrip())
                assert amount_indent > cost_indent, (
                    f"Child 'Amount' indent ({amount_indent}) must be greater than "
                    f"parent 'Cost' indent ({cost_indent}): {repr(amount_line)}"
                )
                break
        else:
            raise AssertionError("Cost: not found in output")

    def test_nested_list_in_array_indentation(self):
        """Nested lists inside array items must indent children deeper than the parent key."""
        doc = DocumentContent(
            kind="document",
            fields={
                "Items": ArrayField(
                    type="array",
                    value_array=[
                        ObjectField(type="object", value_object={
                            "Name": StringField(type="string", value_string="Widget"),
                            "Tags": ArrayField(type="array", value_array=[
                                StringField(type="string", value_string="red"),
                                StringField(type="string", value_string="blue"),
                            ]),
                        }),
                    ],
                ),
            },
        )
        output = to_llm_input(_make_result([doc]))
        lines = output.split("\n")
        # Find the Tags key and its children
        for i, line in enumerate(lines):
            if "Tags:" in line:
                tags_indent = len(line) - len(line.lstrip())
                child_line = lines[i + 1]
                child_indent = len(child_line) - len(child_line.lstrip())
                assert child_indent > tags_indent, (
                    f"Child '- red' indent ({child_indent}) must be greater than "
                    f"parent 'Tags' indent ({tags_indent}): {repr(child_line)}"
                )
                break
        else:
            raise AssertionError("Tags: not found in output")
