# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------


def get_receipt_field_value(field):
    if field is None:
        return field

    value = field.value_array or field.value_date or field.value_integer or field.value_number \
            or field.value_object or field.value_phone_number or field.value_string or field.value_time

    if value is None:  # Could do this and return string value where value_number doesn't get returned
        return field.text
    return value


def get_raw_field(field, raw_result):
    # FIXME: refactor this function
    raw = []
    lines = []
    try:
        for item in field.elements:
            split = item.split("readResults/")[1]
            num1 = int(split[0])
            num2 = int(split.split("/words")[0][-1])
            line = raw_result[num1].lines[num2]
            if line not in lines:
                lines.append(line)
                extracted_line = ExtractedLine._from_generated(line)
                raw.append(extracted_line)
        return raw
    except TypeError:
        return None


class ExtractedReceipt(object):

    def __init__(self, **kwargs):
        self.merchant_address = kwargs.get("merchant_address", None)
        self.merchant_name = kwargs.get("merchant_name", None)
        self.merchant_phone_number = kwargs.get("merchant_phone_number", None)
        self.receipt_type = kwargs.get("receipt_type", None)
        self.receipt_items = kwargs.get("receipt_items", None)
        self.subtotal = kwargs.get("subtotal", None)
        self.tax = kwargs.get("tax", None)
        self.tip = kwargs.get("tip", None)
        self.total = kwargs.get("total", None)
        self.transaction_date = kwargs.get("transaction_date", None)
        self.transaction_time = kwargs.get("transaction_time", None)
        self.fields = kwargs.get("fields", None)


class ReceiptFields(object):

    def __init__(self, **kwargs):
        self.merchant_address = kwargs.get("merchant_address", None)
        self.merchant_name = kwargs.get("merchant_name", None)
        self.merchant_phone_number = kwargs.get("merchant_phone_number", None)
        self.receipt_type = kwargs.get("receipt_type", None)
        self.receipt_items = kwargs.get("receipt_items", None)
        self.subtotal = kwargs.get("subtotal", None)
        self.tax = kwargs.get("tax", None)
        self.tip = kwargs.get("tip", None)
        self.total = kwargs.get("total", None)
        self.transaction_date = kwargs.get("transaction_date", None)
        self.transaction_time = kwargs.get("transaction_time", None)


class FieldValue(object):

    def __init__(self, **kwargs):
        self.value = kwargs.get("value", None)
        self.bounding_box = kwargs.get("bounding_box", None)
        self.confidence = kwargs.get("confidence", None)
        self.raw_field = kwargs.get("raw_field", None)

    @classmethod
    def _from_generated(cls, field, read_result, include_raw):
        if include_raw:
            return cls(
                value=get_receipt_field_value(field),
                bounding_box=field.bounding_box,
                confidence=field.confidence,
                raw_field=get_raw_field(field, read_result)
            )
        return cls(
            value=get_receipt_field_value(field),
            bounding_box=field.bounding_box,
            confidence=field.confidence,
            raw_field=None
        )


class ReceiptItem(object):
    def __init__(self, **kwargs):
        self.name = kwargs.get("name", None)
        self.quantity = kwargs.get("quantity", None)
        self.total_price = kwargs.get("total_price", None)

    @classmethod
    def _from_generated(cls, items):
        try:
            receipt_item = items.value_array
            return [cls(
                name=get_receipt_field_value(item.value_object["Name"]),
                quantity=get_receipt_field_value(item.value_object["Quantity"]),
                total_price=get_receipt_field_value(item.value_object["TotalPrice"])
            ) for item in receipt_item]
        except AttributeError:
            return None


class ReceiptItemField(object):
    def __init__(self, **kwargs):
        self.name = kwargs.get("name", None)
        self.quantity = kwargs.get("quantity", None)
        self.total_price = kwargs.get("total_price", None)

    @classmethod
    def _from_generated(cls, items, read_result, include_raw):
        try:
            receipt_item = items.value_array
            return [cls(
                name=FieldValue._from_generated(item.value_object["Name"], read_result, include_raw),
                quantity=FieldValue._from_generated(item.value_object["Quantity"], read_result, include_raw),
                total_price=FieldValue._from_generated(item.value_object["TotalPrice"], read_result, include_raw),
            ) for item in receipt_item]
        except AttributeError:
            return None


class ExtractedLine(object):
    def __init__(self, **kwargs):
        self.text = kwargs.get("text", None)
        self.bounding_box = kwargs.get("bounding_box", None)
        self.language = kwargs.get("language", None)
        self.words = kwargs.get("words", None)

    @classmethod
    def _from_generated(cls, line):
        return cls(
            text=line.text,
            bounding_box=line.bounding_box,
            language=line.language,
            words=[ExtractedWord._from_generated(word) for word in line.words]
        )


class ExtractedWord(object):
    def __init__(self, **kwargs):
        self.text = kwargs.get("text", None)
        self.bounding_box = kwargs.get("bounding_box", None)
        self.confidence = kwargs.get("confidence", None)

    @classmethod
    def _from_generated(cls, word):
        return cls(
            text=word.text,
            bounding_box=word.bounding_box,
            confidence=word.confidence
        )
