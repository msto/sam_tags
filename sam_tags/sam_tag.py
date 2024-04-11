import re
from enum import Enum
from enum import unique
from typing import TypeVar

EnumerationT = TypeVar("EnumerationT", bound=type[Enum])
"""
An Enumeration type.

Copied from `mypy`: https://github.com/python/mypy/blob/e2fc1f28935806ca04b18fab277217f583b51594/mypy/typeshed/stdlib/enum.pyi#L40
"""

TAG_REGEX = re.compile(r"^[A-Za-z][A-Za-z0-9]$")


def sam_tag(enumeration: EnumerationT) -> type[Enum]:
    """
    Declare a locally-defined group of SAM tags.

    This decorator enforces the following conventions on the decorated enum:

    1. SAM tags must be unique.
    2. SAM tags must not be a predefined standard tag.
    3. SAM tags must be two-character strings matching the regex
       `[A-Za-z][A-Za-z0-9]`, i.e. the first character must be an alphabetical
       character and the second must be an alphanumeric character.
    4. Locally-defined tags must adhere to SAM convention, namely that tags
       start with "X", "Y", or "Z", or are lowercase.
    5. The enumeration class must inherit from `StrEnum` or `str`.
    """

    # TODO: accumulate errors

    if not issubclass(enumeration, Enum):
        raise TypeError(
            "The `sam_tag` decorator may only be applied to `Enum` classes."
        )

    if not issubclass(enumeration, str):
        raise TypeError("SAM tags should inherit from `StrEnum` or mix in `str`.")

    for tag in enumeration:
        if not TAG_REGEX.match(tag.value):
            raise ValueError(
                f"SAM tags must be two-character alphanumeric strings: {tag}"
            )

    return unique(enumeration)
