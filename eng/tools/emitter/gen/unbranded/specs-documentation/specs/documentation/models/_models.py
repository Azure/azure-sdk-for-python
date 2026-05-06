# coding=utf-8
# pylint: disable=useless-super-delegation

from typing import Any, Mapping, TYPE_CHECKING, Union, overload

from .._utils.model_base import Model as _Model, rest_field

if TYPE_CHECKING:
    from .. import models as _models


class BulletPointsModel(_Model):
    """This tests:

    * Simple bullet point. This bullet point is going to be very long to test how text wrapping is
    handled in bullet points within documentation comments. It should properly indent the wrapped
    lines.
    * Another bullet point with **bold text**. This bullet point is also intentionally long to see
    how the formatting is preserved when the text wraps onto multiple lines in the generated
    documentation.
    * Third bullet point with *italic text*. Similar to the previous points, this one is extended
    to ensure that the wrapping and formatting are correctly applied in the output.
    * Complex bullet point with **bold** and *italic* combined. This bullet point combines both
    bold and italic formatting and is long enough to test the wrapping behavior in such cases.
    * **Bold bullet point**: A bullet point that is entirely bolded. This point is also made
    lengthy to observe how the bold formatting is maintained across wrapped lines.
    * *Italic bullet point*: A bullet point that is entirely italicized. This final point is
    extended to verify that italic formatting is correctly applied even when the text spans
    multiple lines.

    :ivar prop: This property uses an enum with bullet point documentation. The enum documentation
     includes various formatting styles to test rendering. The styles are:

     * Simple bullet point. This bullet point is going to be very long to test how text
       wrapping is handled in bullet points within documentation comments. It should properly indent
       the wrapped lines.
     * Bullet point with **bold text**. This bullet point is also intentionally long to see how
       the formatting is preserved when the text wraps onto multiple
     * Bullet point with *italic text*. Similar to the previous points, this one is extended to
       ensure that the wrapping and formatting are correctly applied in the output.
     * Complex bullet point with **bold** and *italic* combined. This bullet point combines
       both bold and italic formatting and is long enough to test the wrapping behavior in such cases.
     * **Bold bullet point**
     * *Italic bullet point*. Required. Known values are: "Simple", "Bold", and "Italic".
    :vartype prop: str or ~specs.documentation.models.BulletPointsEnum
    """

    prop: Union[str, "_models.BulletPointsEnum"] = rest_field(
        visibility=["read", "create", "update", "delete", "query"]
    )
    """This property uses an enum with bullet point documentation. The enum documentation includes
      various formatting styles to test rendering. The styles are:
 
      * Simple bullet point. This bullet point is going to be very long to test how text
        wrapping is handled in bullet points within documentation comments. It should properly indent
        the wrapped lines.
      * Bullet point with **bold text**. This bullet point is also intentionally long to see how
        the formatting is preserved when the text wraps onto multiple
      * Bullet point with *italic text*. Similar to the previous points, this one is extended to
        ensure that the wrapping and formatting are correctly applied in the output.
      * Complex bullet point with **bold** and *italic* combined. This bullet point combines
        both bold and italic formatting and is long enough to test the wrapping behavior in such cases.
      * **Bold bullet point**
      * *Italic bullet point*. Required. Known values are: \"Simple\", \"Bold\", and \"Italic\"."""

    @overload
    def __init__(
        self,
        *,
        prop: Union[str, "_models.BulletPointsEnum"],
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None:
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
