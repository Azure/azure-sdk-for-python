# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import sys
import pytest
import datetime
from azure.ai.formrecognizer import _models

# All features return a tuple of the object and the repr of the obejct

# Adding in assert for each pytest fixture so it's easier to narrow down where the problem is

@pytest.fixture
def bounding_box():
    model = [
        _models.Point(1, 2),
        _models.Point(3, 4),
        _models.Point(5, 6),
        _models.Point(7, 8)
    ]
    model_repr = '[Point(x=1, y=2), Point(x=3, y=4), Point(x=5, y=6), Point(x=7, y=8)]'
    assert repr(model) == model_repr
    return model, model_repr

@pytest.fixture
def form_word(bounding_box):
    model = _models.FormWord(text="Word", bounding_box=bounding_box[0], confidence=0.5, page_number=1)
    model_repr = "FormWord(text=Word, bounding_box={}, confidence=0.5, page_number=1, kind=word)".format(bounding_box[1])[:1024]
    assert repr(model) == model_repr
    return model, model_repr


@pytest.fixture
def form_line(bounding_box, form_word):
    appearance = _models.TextAppearance(style_name="other", style_confidence=1.0)
    model = _models.FormLine(text="Word Word", bounding_box=bounding_box[0], words=[form_word[0], form_word[0]], page_number=1, appearance=appearance)
    model_repr = "FormLine(text=Word Word, bounding_box={}, words=[{}, {}], page_number=1, kind=line, appearance={})".format(bounding_box[1], form_word[1], form_word[1], appearance)[:1024]
    assert repr(model) == model_repr
    return model, model_repr

@pytest.fixture
def form_table_cell(bounding_box, form_word):
    model = _models.FormTableCell(
        text="Cell", row_index=3, column_index=4, row_span=2, column_span=3, bounding_box=bounding_box[0],
        confidence=0.7, is_header=True, is_footer=False, page_number=3, field_elements=[form_word[0]]
    )
    model_repr = "FormTableCell(text=Cell, row_index=3, column_index=4, row_span=2, column_span=3, bounding_box={}, confidence=0.7, " \
        "is_header=True, is_footer=False, page_number=3, field_elements=[{}])".format(bounding_box[1], form_word[1])[:1024]
    assert repr(model) == model_repr
    return model, model_repr

@pytest.fixture
def form_table(form_table_cell, bounding_box):
    model = _models.FormTable(page_number=1, cells=[form_table_cell[0], form_table_cell[0]], row_count=3, column_count=4, bounding_box=bounding_box[0])
    model_repr = "FormTable(page_number=1, cells=[{}, {}], row_count=3, column_count=4, bounding_box={})".format(form_table_cell[1], form_table_cell[1], bounding_box[1])[:1024]
    assert repr(model) == model_repr
    return model, model_repr

@pytest.fixture
def field_data(bounding_box, form_word, form_line):
    model = _models.FieldData(page_number=1, text="This is text.", bounding_box=bounding_box[0], field_elements=[form_word[0], form_line[0]])
    model_repr = "FieldData(page_number=1, text=This is text., bounding_box={}, field_elements=[{}, {}])".format(bounding_box[1], form_word[1], form_line[1])[:1024]
    assert repr(model) == model_repr
    return model, model_repr

@pytest.fixture
def form_field_two(field_data):
    model = _models.FormField(value_type="string", label_data=field_data[0], value_data=field_data[0], name="form_field_two", value="value", confidence=0)
    model_repr = "FormField(value_type=string, label_data={}, value_data={}, name=form_field_two, value='value', confidence=0)".format(field_data[1], field_data[1])[:1024]
    assert repr(model) == model_repr
    return model, model_repr

@pytest.fixture
def form_field_one(field_data, form_field_two):
    model = _models.FormField(value_type="string", label_data=field_data[0], value_data=field_data[0], name="form_field_one", value=form_field_two[0], confidence=1.0)
    model_repr = "FormField(value_type=string, label_data={}, value_data={}, name=form_field_one, value={}, confidence=1.0)".format(field_data[1], field_data[1], form_field_two[1])[:1024]
    assert repr(model) == model_repr
    return model, model_repr

@pytest.fixture
def page_range():
    model = _models.FormPageRange(first_page_number=1, last_page_number=100)
    model_repr = "FormPageRange(first_page_number=1, last_page_number=100)"
    assert repr(model) == model_repr
    return model, model_repr

@pytest.fixture
def form_page(form_table, form_line):
    model = _models.FormPage(page_number=1, text_angle=180, width=5, height=5.5, unit="pixel", tables=[form_table[0]], lines=[form_line[0]])
    model_repr = "FormPage(page_number=1, text_angle=180, width=5, height=5.5, unit=pixel, tables=[{}], lines=[{}])".format(
            form_table[1], form_line[1]
        )[:1024]
    assert repr(model) == model_repr
    return model, model_repr

@pytest.fixture
def custom_form_model_field():
    model = _models.CustomFormModelField(label="label", name="name", accuracy=0.99)
    model_repr = "CustomFormModelField(label=label, name=name, accuracy=0.99)"
    assert repr(model) == model_repr
    return model, model_repr

@pytest.fixture
def custom_form_sub_model(custom_form_model_field):
    model = _models.CustomFormSubmodel(accuracy=0.99, model_id=1, fields={"name": custom_form_model_field[0]}, form_type="Itemized")
    model_repr = "CustomFormSubmodel(accuracy=0.99, model_id=1, fields={{'name': {}}}, form_type=Itemized)".format(custom_form_model_field[1])[:1024]
    assert repr(model) == model_repr
    return model, model_repr

@pytest.fixture
def form_recognizer_error():
    model = _models.FormRecognizerError(code=404, message="Resource Not Found")
    model_repr = "FormRecognizerError(code=404, message=Resource Not Found)"
    assert repr(model) == model_repr
    return model, model_repr

@pytest.fixture
def training_document_info(form_recognizer_error):
    model = _models.TrainingDocumentInfo(name="name", status="partiallySucceeded", page_count=5, errors=[form_recognizer_error[0]], model_id=1)
    model_repr = "TrainingDocumentInfo(name=name, status=partiallySucceeded, page_count=5, errors=[{}], model_id=1)".format(form_recognizer_error[1])[:1024]
    assert repr(model) == model_repr
    return model, model_repr

@pytest.fixture
def custom_form_model_properties():
    model = _models.CustomFormModelProperties(is_composed_model=True)
    model_repr = "CustomFormModelProperties(is_composed_model=True)"
    assert repr(model) == model_repr
    return model, model_repr

@pytest.fixture
def document_span():
    model = _models.DocumentSpan(offset=2, length=5)
    model_repr = "DocumentSpan(offset=2, length=5)"
    assert repr(model) == model_repr
    return model, model_repr

@pytest.fixture
def bounding_region(bounding_box):
    model = _models.BoundingRegion(polygon=bounding_box[0], page_number=2)
    model_repr = "BoundingRegion(page_number=2, polygon={})".format(bounding_box[1])
    assert repr(model) == model_repr
    return model, model_repr

@pytest.fixture
def address_value():
    model = _models.AddressValue(
        house_number="123",
        po_box="4567",
        road="Contoso Ave",
        city="Redmond",
        state="WA",
        postal_code="98052",
        country_region="USA",
        street_address="123 Contoso Ave",
        unit="unit",
        city_district="city_district",
        state_district="state_district",
        suburb="suburb",
        house="house",
        level="level"
    )
    model_repr = "AddressValue(house_number={}, po_box={}, road={}, city={}, state={}, postal_code={}, country_region={}, street_address={}, " \
                 "unit={}, city_district={}, state_district={}, suburb={}, house={}, level={})".format(
        "123",
        "4567",
        "Contoso Ave",
        "Redmond",
        "WA",
        "98052",
        "USA",
        "123 Contoso Ave",
        "unit",
        "city_district",
        "state_district",
        "suburb",
        "house",
        "level"
    )
    assert repr(model) == model_repr
    return model, model_repr


@pytest.fixture
def address_document_field(bounding_region, document_span, address_value):
    model = _models.DocumentField(value_type="address", value=address_value[0], content="123 Contoso Ave, Redmond, WA 98052 P.O. 4567", bounding_regions=[bounding_region[0]], spans=[document_span[0]], confidence=0.98)
    model_repr = "DocumentField(value_type={}, value={}, content={}, bounding_regions=[{}], spans=[{}], confidence={})".format(
                "address",
                address_value[1],
                "123 Contoso Ave, Redmond, WA 98052 P.O. 4567",
                bounding_region[1],
                document_span[1],
                0.98,
            )
    assert repr(model) == model_repr
    return model, model_repr

@pytest.fixture
def document_field(bounding_region, document_span):
    model = _models.DocumentField(value_type="number", value=0.30, content="my content", bounding_regions=[bounding_region[0]], spans=[document_span[0]], confidence=0.98)
    model_repr = "DocumentField(value_type={}, value={}, content={}, bounding_regions=[{}], spans=[{}], confidence={})".format(
                "number",
                0.30,
                "my content",
                bounding_region[1],
                document_span[1],
                0.98,
            )
    assert repr(model) == model_repr
    return model, model_repr

@pytest.fixture
def analyzed_document(bounding_region, document_span, document_field, address_document_field):
    model = _models.AnalyzedDocument(doc_type="prebuilt:invoice", bounding_regions=[bounding_region[0]], spans=[document_span[0]], fields={"key": document_field[0], "address": address_document_field[0]}, confidence=0.98)
    model_repr = "AnalyzedDocument(doc_type=prebuilt:invoice, bounding_regions=[{}], spans=[{}], fields={{'key': {}, 'address': {}}}, confidence={})".format(
        bounding_region[1], document_span[1], document_field[1], address_document_field[1], 0.98)
    assert repr(model) == model_repr
    return model, model_repr

@pytest.fixture
def document_key_value_element(bounding_region, document_span):
    model = _models.DocumentKeyValueElement(content="my content", bounding_regions=[bounding_region[0]], spans=[document_span[0]])
    model_repr = "DocumentKeyValueElement(content={}, bounding_regions=[{}], spans=[{}])".format(
                "my content",
                bounding_region[1],
                document_span[1],
            )
    assert repr(model) == model_repr
    return model, model_repr

@pytest.fixture
def document_key_value_pair(document_key_value_element):
    model = _models.DocumentKeyValuePair(key=document_key_value_element[0], value=document_key_value_element[0], confidence=0.98, common_name="Charges")
    model_repr = "DocumentKeyValuePair(key={}, value={}, confidence={}, common_name={})".format(document_key_value_element[1], document_key_value_element[1], 0.98, "Charges")
    assert repr(model) == model_repr
    return model, model_repr

@pytest.fixture
def document_word(bounding_box, document_span):
    model = _models.DocumentWord(content="word", polygon=bounding_box[0], span=document_span[0], confidence=0.92)
    model_repr = "DocumentWord(content={}, polygon={}, span={}, confidence={})".format(
            "word",
            bounding_box[1],
            document_span[1],
            0.92,
        )
    assert repr(model) == model_repr
    return model, model_repr

@pytest.fixture
def document_line(bounding_box, document_span):
    model = _models.DocumentLine(content="line content", polygon=bounding_box[0], spans=[document_span[0]])
    model_repr = "DocumentLine(content={}, polygon={}, spans=[{}])".format(
            "line content",
            bounding_box[1],
            document_span[1],
        )
    assert repr(model) == model_repr
    return model, model_repr

@pytest.fixture
def document_paragraph(bounding_region, document_span):
    model = _models.DocumentParagraph(role="role", content="paragraph content", bounding_regions=[bounding_region[0]], spans=[document_span[0]])
    model_repr = "DocumentParagraph(role={}, content={}, bounding_regions=[{}], spans=[{}])".format(
            "role",
            "paragraph content",
            bounding_region[1],
            document_span[1],
        )
    assert repr(model) == model_repr
    return model, model_repr

@pytest.fixture
def document_language(document_span):
    model = _models.DocumentLanguage(locale="en", spans=[document_span[0]], confidence=0.99)
    model_repr = "DocumentLanguage(locale={}, spans=[{}], confidence={})".format(
            "en",
            document_span[1],
            0.99,
        )
    assert repr(model) == model_repr
    return model, model_repr

@pytest.fixture
def document_selection_mark(bounding_box, document_span):
    model = _models.DocumentSelectionMark(state="selected", polygon=bounding_box[0], span=document_span[0], confidence=0.89)
    model_repr = "DocumentSelectionMark(state={}, span={}, confidence={}, polygon={})".format(
            "selected",
            document_span[1],
            0.89,
            bounding_box[1],
        )
    assert repr(model) == model_repr
    return model, model_repr

@pytest.fixture
def document_annotation(bounding_box, document_span):
    model = _models.DocumentAnnotation(
                    kind="check",
                    polygon=bounding_box[0],
                    confidence=0.8
                )
    model_repr = "DocumentAnnotation(kind={}, polygon={}, confidence={})".format(
            "check",
            bounding_box[1],
            0.8,
        )
    assert repr(model) == model_repr
    return model, model_repr

@pytest.fixture
def document_barcode(bounding_box, document_span):
    model = _models.DocumentBarcode(
                    kind="QRCode",
                    value="15",
                    polygon=bounding_box[0],
                    span=document_span[0],
                    confidence=0.8
                )
    model_repr = "DocumentBarcode(kind={}, polygon={}, confidence={}, value={}, span={})".format(
            "QRCode",
            bounding_box[1],
            0.8,
            "15",
            document_span[1],
        )
    assert repr(model) == model_repr
    return model, model_repr

@pytest.fixture
def document_formula(bounding_box, document_span):
    model = _models.DocumentFormula(
                    kind="inline",
                    value="2+2=4",
                    polygon=bounding_box[0],
                    span=document_span[0],
                    confidence=0.8
                )
    model_repr = "DocumentFormula(kind={}, polygon={}, confidence={}, value={}, span={})".format(
            "inline",
            bounding_box[1],
            0.8,
            "2+2=4",
            document_span[1],
        )
    assert repr(model) == model_repr
    return model, model_repr

@pytest.fixture
def document_image(bounding_box, document_span):
    model = _models.DocumentImage(
                    page_number=1,
                    polygon=bounding_box[0],
                    span=document_span[0],
                    confidence=0.8
                )
    model_repr = "DocumentImage(page_number={}, polygon={}, confidence={}, span={})".format(
            1,
            bounding_box[1],
            0.8,
            document_span[1],
        )
    assert repr(model) == model_repr
    return model, model_repr

@pytest.fixture
def document_page(document_span, document_word, document_selection_mark, document_line, document_annotation, document_formula, document_image, document_barcode):
    model = _models.DocumentPage(
        page_number=1,
        angle=120.0,
        width=8.0,
        height=11.0,
        unit="inch",
        spans=[document_span[0]],
        words=[document_word[0]],
        selection_marks=[document_selection_mark[0]],
        lines=[document_line[0]],
        kind="document",
        annotations=[document_annotation[0]],
        formulas=[document_formula[0]],
        images=[document_image[0]],
        barcodes=[document_barcode[0]],
    )
    model_repr = "DocumentPage(page_number={}, angle={}, width={}, height={}, unit={}, lines=[{}], words=[{}], selection_marks=[{}], spans=[{}], " \
                 "kind={}, annotations=[{}], barcodes=[{}], formulas=[{}], images=[{}])".format(
                1,
                120.0,
                8.0,
                11.0,
                "inch",
                document_line[1],
                document_word[1],
                document_selection_mark[1],
                document_span[1],
                "document",
                document_annotation[1],
                document_barcode[1],
                document_formula[1],
                document_image[1],
            )
    assert repr(model) == model_repr
    return model, model_repr

@pytest.fixture
def document_style(document_span):
    model = _models.DocumentStyle(
        is_handwritten=True,
        spans=[document_span[0]],
        confidence=0.98,
        similar_font_family="Arial",
        font_style="italic",
        font_weight="bold",
        color="#FF0000",
        background_color="#FFFFFF"
    )
    model_repr = "DocumentStyle(is_handwritten={}, spans=[{}], confidence={}, similar_font_family={}, font_style={}, " \
                 "font_weight={}, color={}, background_color={})".format(
                    True,
                    document_span[1],
                    0.98,
                    "Arial",
                    "italic",
                    "bold",
                    "#FF0000",
                    "#FFFFFF"
                )
    assert repr(model) == model_repr
    return model, model_repr

@pytest.fixture
def document_table_cell(bounding_region, document_span):
    model = _models.DocumentTableCell(kind="rowHeader", row_index=1, column_index=2, row_span=2, column_span=3, content="header", bounding_regions=[bounding_region[0]], spans=[document_span[0]])
    model_repr = "DocumentTableCell(kind={}, row_index={}, column_index={}, row_span={}, column_span={}, content={}, bounding_regions=[{}], spans=[{}])".format(
                "rowHeader",
                1,
                2,
                2,
                3,
                "header",
                bounding_region[1],
                document_span[1],
            )
    assert repr(model) == model_repr
    return model, model_repr

@pytest.fixture
def document_table(bounding_region, document_span, document_table_cell):
    model = _models.DocumentTable(row_count=3, column_count=4, cells=[document_table_cell[0]], bounding_regions=[bounding_region[0]], spans=[document_span[0]])
    model_repr = "DocumentTable(row_count={}, column_count={}, cells=[{}], bounding_regions=[{}], spans=[{}])".format(
                3,
                4,
                document_table_cell[1],
                bounding_region[1],
                document_span[1],
            )
    assert repr(model) == model_repr
    return model, model_repr

@pytest.fixture
def doc_type_info():
    model = _models.DocumentTypeDetails(
            description="my description",
            build_mode="neural",
            field_confidence={"CustomerName": 95},
            field_schema={"prebuilt-invoice": {"CustomerName": {"type": "string"}}}
    )
    model_repr = "DocumentTypeDetails(description={}, build_mode={}, field_schema={{'prebuilt-invoice': {}}}, field_confidence={{'CustomerName': {}}})".format(
                "my description",
                "neural",
                {"CustomerName": {"type": "string"}},
                95
            )
    assert repr(model) == model_repr
    return model, model_repr

@pytest.fixture
def document_model(doc_type_info):
    model = _models.DocumentModelDetails(
            api_version="2022-08-31",
            tags={"awesome": "tag"},
            description="my description",
            created_on=datetime.datetime(2021, 9, 16, 10, 10, 59, 342380),
            expires_on=datetime.datetime(2024, 9, 16, 10, 10, 59, 342380),
            model_id="prebuilt-invoice",
            doc_types={"prebuilt-invoice": doc_type_info[0]}
    )
    model_repr = "DocumentModelDetails(model_id={}, description={}, created_on={}, api_version={}, tags={}, doc_types={{'prebuilt-invoice': {}}}, expires_on={})".format(
                "prebuilt-invoice",
                "my description",
                datetime.datetime(2021, 9, 16, 10, 10, 59, 342380),
                "2022-08-31",
                {"awesome": "tag"},
                doc_type_info[1],
                datetime.datetime(2024, 9, 16, 10, 10, 59, 342380),
            )
    assert repr(model) == model_repr
    return model, model_repr


@pytest.fixture
def document_analysis_inner_error():
    model = _models.DocumentAnalysisInnerError(
            code="ResourceNotFound",
            message="Resource was not found",
            innererror=_models.DocumentAnalysisInnerError(
                code="ResourceNotFound",
                message="Resource was not found",
            )
    )
    model_repr = "DocumentAnalysisInnerError(code={}, message={}, innererror={})".format(
                "ResourceNotFound",
                "Resource was not found",
                _models.DocumentAnalysisInnerError(
                    code="ResourceNotFound",
                    message="Resource was not found",
                ))
    assert repr(model) == model_repr
    return model, model_repr


@pytest.fixture
def document_analysis_error(document_analysis_inner_error):
    model = _models.DocumentAnalysisError(
            code="ResourceNotFound",
            message="Resource was not found",
            target="resource",
            details=[
                _models.DocumentAnalysisError(
                    code="ResourceNotFound",
                    message="Resource was not found"
                )
            ],
            innererror=document_analysis_inner_error[0]
    )
    model_repr = "DocumentAnalysisError(code={}, message={}, target={}, details={}, innererror={})".format(
                "ResourceNotFound",
                "Resource was not found",
                "resource",
                [_models.DocumentAnalysisError(
                    code="ResourceNotFound",
                    message="Resource was not found"
                )],
                document_analysis_inner_error[1]
            )
    assert repr(model) == model_repr
    return model, model_repr


class TestRepr():
    # Not inheriting form FormRecognizerTest because that doesn't allow me to define pytest fixtures in the same file
    # Not worth moving pytest fixture definitions to conftest since all I would use is assertEqual and I can just use assert
    def test_recognized_form(self, form_field_one, page_range, form_page):
        model = _models.RecognizedForm(form_type="receipt", form_type_confidence=1.0, model_id=1, fields={"one": form_field_one[0]}, page_range=page_range[0], pages=[form_page[0]])
        model_repr = "RecognizedForm(form_type=receipt, fields={{'one': {}}}, page_range={}, pages=[{}], form_type_confidence=1.0, model_id=1)".format(
            form_field_one[1], page_range[1], form_page[1]
        )[:1024]
        assert repr(model) == model_repr

    def test_custom_form_model(self, custom_form_sub_model, custom_form_model_properties, form_recognizer_error, training_document_info):
        model = _models.CustomFormModel(
            model_id=1,
            status="creating",
            training_started_on=datetime.datetime(1, 1, 1),
            training_completed_on=datetime.datetime(1, 1, 1),
            submodels=[custom_form_sub_model[0], custom_form_sub_model[0]],
            errors=[form_recognizer_error[0]],
            training_documents=[training_document_info[0], training_document_info[0]],
            properties=custom_form_model_properties[0],
            model_name="my model"
        )

        model_repr = "CustomFormModel(model_id=1, status=creating, training_started_on=0001-01-01 00:00:00, " \
            "training_completed_on=0001-01-01 00:00:00, submodels=[{}, {}], errors=[{}], training_documents=[{}, {}], " \
            "model_name=my model, properties={})".format(
                custom_form_sub_model[1], custom_form_sub_model[1], form_recognizer_error[1], training_document_info[1], training_document_info[1],
                custom_form_model_properties[1]
            )[:1024]

        assert repr(model) == model_repr

    def test_custom_form_model_info(self, custom_form_model_properties):
        model = _models.CustomFormModelInfo(
            model_id=1, status="ready", training_started_on=datetime.datetime(1, 1, 1), training_completed_on=datetime.datetime(1, 1, 1),
            properties=custom_form_model_properties[0], model_name="my model"
        )
        model_repr = "CustomFormModelInfo(model_id=1, status=ready, training_started_on=0001-01-01 00:00:00, training_completed_on=0001-01-01 00:00:00, properties={}, model_name=my model)".format(custom_form_model_properties[1])[:1024]
        assert repr(model) == model_repr

    def test_account_properties(self):
        model = _models.AccountProperties(custom_model_count=100, custom_model_limit=1000)
        model_repr = "AccountProperties(custom_model_count=100, custom_model_limit=1000)"
        assert repr(model) == model_repr

    def test_analyze_result(self, document_page, document_table, document_key_value_pair, document_style, analyzed_document, document_language, document_paragraph):
        model = _models.AnalyzeResult(api_version="2022-08-31", model_id="mymodel", content="document content", languages=[document_language[0]], pages=[document_page[0]], tables=[document_table[0]], key_value_pairs=[document_key_value_pair[0]], styles=[document_style[0]], documents=[analyzed_document[0]], paragraphs=[document_paragraph[0]])
        model_repr = "AnalyzeResult(api_version={}, model_id={}, content={}, languages=[{}], pages=[{}], paragraphs=[{}], tables=[{}], key_value_pairs=[{}], styles=[{}], documents=[{}])".format(
                "2022-08-31",
                "mymodel",
                "document content",
                document_language[1],
                document_page[1],
                document_paragraph[1],
                document_table[1],
                document_key_value_pair[1],
                document_style[1],
                analyzed_document[1],
            )
        assert repr(model) == model_repr

    def test_model_operation(self, document_analysis_error, document_model):
        model = _models.OperationDetails(
                api_version="2022-08-31",
                tags={"awesome": "tag"},
                operation_id="id",
                status="succeeded",
                percent_completed=99,
                created_on=datetime.datetime(2021, 9, 16, 10, 10, 59, 342380),
                last_updated_on=datetime.datetime(2021, 9, 16, 10, 10, 59, 342380),
                kind="documentModelCopyTo",
                resource_location="westus2",
                error=document_analysis_error[0],
                result=document_model[0],
            )
        model_repr = "OperationDetails(operation_id={}, status={}, percent_completed={}, created_on={}, last_updated_on={}, kind={}, resource_location={}, result={}, error={}, api_version={}, tags={})".format(
                    "id",
                    "succeeded",
                    99,
                    datetime.datetime(2021, 9, 16, 10, 10, 59, 342380),
                    datetime.datetime(2021, 9, 16, 10, 10, 59, 342380),
                    "documentModelCopyTo",
                    "westus2",
                    document_model[1],
                    document_analysis_error[1],
                    "2022-08-31",
                    {"awesome": "tag"},
                )
        assert repr(model) == model_repr

    def test_model_operation_info(self):
        model = _models.OperationSummary(
                operation_id="id",
                status="succeeded",
                percent_completed=100,
                created_on=datetime.datetime(2021, 9, 16, 10, 10, 59, 342380),
                last_updated_on=datetime.datetime(2021, 9, 16, 10, 30, 15, 342380),
                kind="documentModelCompose",
                resource_location="westus",
                api_version="2022-08-31",
                tags={"test": "value"},
            )
        model_repr = "OperationSummary(operation_id={}, status={}, percent_completed={}, created_on={}, last_updated_on={}, kind={}, resource_location={}, api_version={}, tags={})".format(
                    "id",
                    "succeeded",
                    100,
                    datetime.datetime(2021, 9, 16, 10, 10, 59, 342380),
                    datetime.datetime(2021, 9, 16, 10, 30, 15, 342380),
                    "documentModelCompose",
                    "westus",
                    "2022-08-31",
                    {"test": "value"},
                )
        assert repr(model) == model_repr

    def test_document_model(self, doc_type_info):
        model = _models.DocumentModelDetails(
            description="my description",
            created_on=datetime.datetime(2021, 9, 16, 10, 10, 59, 342380),
            expires_on=datetime.datetime(2024, 9, 16, 10, 10, 59, 342380),
            model_id="prebuilt-invoice",
            api_version="2022-08-31",
            tags={"test": "value"},
            doc_types={
                "prebuilt-invoice": doc_type_info[0],
            }
        )
        model_repr = "DocumentModelDetails(model_id={}, description={}, created_on={}, api_version={}, tags={}, doc_types={{'prebuilt-invoice': {}}}, expires_on={})".format(
            "prebuilt-invoice",
            "my description",
            datetime.datetime(2021, 9, 16, 10, 10, 59, 342380),
            "2022-08-31",
            {"test": "value"},
            doc_type_info[1],
            datetime.datetime(2024, 9, 16, 10, 10, 59, 342380),
        )
        assert repr(model) == model_repr

    def test_document_model_info(self):
        model = _models.DocumentModelSummary(
            description="my description",
            created_on=datetime.datetime(2021, 9, 16, 10, 10, 59, 342380),
            expires_on=datetime.datetime(2024, 9, 16, 10, 10, 59, 342380),
            model_id="prebuilt-invoice",
            api_version="2022-08-31",
            tags={"test": "value"},
        )
        model_repr = "DocumentModelSummary(model_id={}, description={}, created_on={}, api_version={}, tags={}, expires_on={})".format(
            "prebuilt-invoice",
            "my description",
            datetime.datetime(2021, 9, 16, 10, 10, 59, 342380),
            "2022-08-31",
            {"test": "value"},
            datetime.datetime(2024, 9, 16, 10, 10, 59, 342380),
        )
        assert repr(model) == model_repr

    def test_resource_details(self):
        model = _models.ResourceDetails(
            custom_document_models=_models.CustomDocumentModelsDetails(
                limit=5000, count=10
            ),
            custom_neural_document_model_builds=_models.QuotaDetails(
                used=0,
                quota=20,
                quota_resets_on=datetime.datetime(2024, 9, 16, 10, 10, 59, 342380)
            )
        )
        model_repr = "ResourceDetails(custom_document_models={}, custom_neural_document_model_builds={})".format(
            "CustomDocumentModelsDetails(count=10, limit=5000)",
            "QuotaDetails(used=0, quota=20, quota_resets_on=2024-09-16 10:10:59.342380)"
        )
        assert repr(model) == model_repr

    def test_currency_value(self):
        model = _models.CurrencyValue(
            amount=10.5,
            symbol="$",
            code="USD"
        )
        model_repr = "CurrencyValue(amount={}, symbol={}, code={})".format(
            10.5,
            "$",
            "USD"
        )
        assert repr(model) == model_repr

    def test_currency_value_str(self):
        model = _models.CurrencyValue(
            amount=10.5,
            symbol="$",
            code="USD"
        )
        assert str(model) == "$10.5"

        model = _models.CurrencyValue(
            amount=10.5,
        )
        assert str(model) == "10.5"
