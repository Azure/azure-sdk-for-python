# coding=utf-8

from enum import Enum
from corehttp.utils import CaseInsensitiveEnumMeta


class BulletPointsEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """This tests really long bullet points in enum documentation to see how wrapping and formatting
    are handled. This should wrap around correctly and maintain proper indentation for each line.

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
    """

    SIMPLE = "Simple"
    """Simple bullet point. This line is intentionally long to test text wrapping in bullet points
    within enum documentation comments. It should properly indent the wrapped lines.
    
    * One: one. This line is intentionally long to test text wrapping in bullet points within enum
    documentation comments. It should properly indent the wrapped lines.
    * Two: two. This line is intentionally long to test text wrapping in bullet points within enum
    documentation comments. It should properly indent the wrapped lines."""
    BOLD = "Bold"
    """Bullet point with **bold text**. This line is intentionally long to test text wrapping in
    bullet points within enum documentation comments. It should properly indent the wrapped lines.
    
    * **One**: one. This line is intentionally long to test text wrapping in bullet points within
    enum documentation comments. It should properly indent the wrapped lines.
    * **Two**: two. This line is intentionally long to test text wrapping in bullet points within
    enum documentation comments. It should properly indent the wrapped lines."""
    ITALIC = "Italic"
    """Bullet point with *italic text*. This line is intentionally long to test text wrapping in
    bullet points within enum documentation comments. It should properly indent the wrapped lines.
    
    * *One*: one. This line is intentionally long to test text wrapping in bullet points within
    enum documentation comments. It should properly indent the wrapped lines.
    * *Two*: two. This line is intentionally long to test text wrapping in bullet points within
    enum documentation comments. It should properly indent the wrapped lines."""
