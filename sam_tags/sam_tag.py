import re
from collections import Counter
from collections import defaultdict
from enum import Enum
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

    def validate_sam_tag_enum(enumeration: EnumerationT) -> type[Enum]:
        if not issubclass(enumeration, Enum):
            raise TypeError(
                f"{enumeration.__name__}: The `sam_tag` decorator may only be applied to `Enum` "
                "subclasses."
            )

        if not issubclass(enumeration, str):
            raise TypeError(
                f"{enumeration.__name__}: SAM tag classes should inherit from `StrEnum` or mix in "
                "`str`."
            )

        _validate_unique_sam_tags(enumeration)

        errs: list[str] = []
        for tag in enumeration:
            err_msg = _validate_sam_tag(tag, strict=strict)
            if err_msg is not None:
                errs.append(err_msg)

        if len(errs) > 0:
            raise ValueError(
                f"{enumeration.__name__}: The following SAM tags are invalid:\n" + "\n".join(errs)
            )

        return enumeration

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


def _validate_unique_sam_tags(enumeration: EnumerationT) -> None:
    """
    Validate that all SAM tags are unique.

    `enum.unique` does this, but its error reporting is limited. Namely, if more than two members
    are duplicates, the duplicated members are reported in pairs instead of as a single group. And, the duplicated *value* is not reported - only the names of the members with duplicated values.

    Raises:
        ValueError: if any of the defined SAM tag values are duplicated.
    """

    values_to_names: dict[str, list[str]] = defaultdict(list)
    value_counts: Counter[str] = Counter()

    for tag_name, tag in enumeration.__members__.items():
        values_to_names[tag.value].append(tag_name)
        value_counts[tag.value] += 1

    duplicates: list[str] = []
    for tag_value, tag_count in value_counts.items():
        if tag_count > 1:
            msg = "  " + ", ".join(sorted(values_to_names[tag_value])) + f": '{tag_value}'"
            duplicates.append(msg)

    if len(duplicates) > 0:
        raise ValueError(
            f"{enumeration.__name__}: The following SAM tags have duplicate values:\n"
            + "\n".join(duplicates)
        )


def _validate_sam_tag(tag: Enum, strict: bool = False) -> str | None:
    """
    Validate an individual SAM tag.

    Returns:
        An error message if the SAM tag was invalid.
        None otherwise.
    """
    if TAG_REGEX.match(tag.value) is None:
        return f"  {tag}: SAM tags must be two-character alphanumeric strings."

    if tag.value in [standard_tag.value for standard_tag in StandardTag]:
        return f"  {tag}: Locally-defined SAM tags may not conflict with a predefined standard tag."

    if strict and not _is_valid_local_tag(tag.value):
        return f"  {tag}: Locally-defined SAM tags must be lowercase or start with X, Y, or Z."

    return None


def _is_valid_local_tag(tag: str) -> bool:
    """
    True if the tag is a valid locally-defined tag.
    """
    return tag.startswith("X") or tag.startswith("Y") or tag.startswith("Z") or tag.islower()
