import re
from enum import Enum
from enum import unique
from typing import Callable
from typing import TypeVar

from sam_tags.standard_tag import StandardTag

EnumerationT = TypeVar("EnumerationT", bound=type[Enum])
"""
An Enumeration type.

Copied from `mypy`: https://github.com/python/mypy/blob/e2fc1f28935806ca04b18fab277217f583b51594/mypy/typeshed/stdlib/enum.pyi#L40
"""

TAG_REGEX = re.compile(r"^[A-Za-z][A-Za-z0-9]$")


def sam_tag(
    *args: EnumerationT,
    strict: bool = True,
    permit_standard_collisions: bool = False,
) -> type[Enum] | Callable[..., type[Enum]]:
    """
    Declare a locally-defined group of SAM tags.

    This decorator enforces the following conventions on the decorated enum:

    1. SAM tags must be two-character strings matching the regex
       `[A-Za-z][A-Za-z0-9]`, i.e. the first character must be an alphabetical
       character and the second must be an alphanumeric character.
    2. SAM tags must be unique.
    3. SAM tags must not be a predefined standard tag.
    4. The enumeration class must inherit from `StrEnum` or `str`.

    Additionally, the following conventions are enforced when `strict=True`:

    1. Locally-defined tags must adhere to SAM convention, namely that tags
       start with "X", "Y", or "Z", or are lowercase.
    """

    # TODO: accumulate errors

    def validate_sam_tag_enum(enumeration: EnumerationT) -> type[Enum]:
        if not issubclass(enumeration, Enum):
            raise TypeError("The `sam_tag` decorator may only be applied to `Enum` subclasses.")

        if not issubclass(enumeration, str):
            raise TypeError("SAM tags should inherit from `StrEnum` or mix in `str`.")

        errs: list[Exception] = []
        for tag in enumeration:
            try:
                _validate_sam_tag(tag, strict=strict)
            except ValueError as err:
                errs.append(err)

        if len(errs) > 0:
            raise ExceptionGroup("Invalid SAM tags", errs)

        return unique(enumeration)

    # When the decorator is invoked with keyword arguments (or with
    # parentheses), there are no positional arguments. e.g.,
    # ```
    # @sam_tag(strict=True)
    # class CustomTag(StrEnum):
    #     ...
    # ```
    if len(args) == 0:
        return validate_sam_tag_enum

    # When the decorator is invoked without keyword arguments (and without
    # parentheses), the enumeration class is passed implicitly as the only
    # positional argument. i.e.,
    # ```
    # @sam_tag
    # class CustomTag(StrEnum):
    #     ...
    # ```
    elif len(args) == 1:
        return validate_sam_tag_enum(args[0])

    # NB: I don't think it's possible to pass more than one positional argument
    # to a class decorator.
    else:
        raise AssertionError("unreachable")


def _validate_sam_tag(tag: Enum, strict: bool = False) -> None:
    """
    Validate an individual SAM tag.
    """

    if not TAG_REGEX.match(tag.value):
        raise ValueError(f"SAM tags must be two-character alphanumeric strings: {tag}")

    if tag.value in [standard_tag.value for standard_tag in StandardTag]:
        raise ValueError(
            f"Locally-defined SAM tags may not conflict with a predefined standard tag: {tag}"
        )

    if strict and not _is_valid_local_tag(tag.value):
        raise ValueError("Locally-defined SAM tags must be lowercase or start with " "X, Y, or Z.")


def _is_valid_local_tag(tag: str) -> bool:
    """
    True if the tag is a valid locally-defined tag.
    """

    return tag.startswith("X") or tag.startswith("Y") or tag.startswith("Z") or tag.islower()
