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
    allow_unconventional_local_names: bool = False,
    allow_standard_tag_collisions: bool = False,
) -> type[Enum] | Callable[..., type[Enum]]:
    """
    Declare a locally-defined group of SAM tags.

    This decorator always enforces the following conventions on the decorated enum:

    1. SAM tags must be two-character strings matching the regex `[A-Za-z][A-Za-z0-9]`, i.e. the
       first character must be an alphabetical character and the second must be an alphanumeric
       character.
    2. SAM tags must be unique.
    3. The enumeration class must inherit from `StrEnum` or `str`.

    Additionally, the following optional conventions are enforced by default, but may be disabled:

    1. Locally-defined tags must adhere to SAM convention, namely that tags start with "X", "Y", or
       "Z", or are lowercase.
    2. SAM tags must not be a predefined standard tag.

    Args:
        allow_unconventional_local_names: If True, custom SAM tags do not have to adhere to SAM
            conventions for the locally-defined tag namespace. (i.e. they may be uppercase and start
            with a letter besides "X", "Y", or "Z".)
        allow_standard_tag_collisions: If True, custom SAM tags may be the same as a predefined
            standard tag.
    """

    def validate_sam_tag_enum(enumeration: EnumerationT) -> type[Enum]:
        # Validate that the enumeration class is a `StrEnum` (or an `Enum` with `str` mixin).
        _validate_sam_tag_class_is_valid(enumeration)

        # Validate that all SAM tags are unique.
        _validate_sam_tags_are_unique(enumeration)

        # Validate that all SAM tags are valid per SAM spec.
        _validate_sam_tags(
            enumeration,
            allow_unconventional_local_names=allow_unconventional_local_names,
            allow_standard_tag_collisions=allow_standard_tag_collisions,
        )

        return enumeration

    # When the decorator is invoked with keyword arguments (or with
    # parentheses), there are no positional arguments. e.g.,
    # ```
    # @sam_tag(allow_unconventional_local_names=True)
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


def _validate_sam_tag_class_is_valid(enumeration: EnumerationT) -> None:
    """
    Require the SAM tag class to inherit from `StrEnum`.

    Raises:
        `TypeError` if the class does not inherit from `Enum` and `str`.
    """
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


def _validate_sam_tags_are_unique(enumeration: EnumerationT) -> None:
    """
    Validate that all SAM tags are unique.

    `enum.unique` does this, but its error reporting is limited. Namely, if more than two members
    are duplicates, the duplicated members are reported in pairs instead of as a single group. And,
    the duplicated *value* is not reported - only the names of the members with duplicated values.

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


def _validate_sam_tags(
    enumeration: EnumerationT,
    allow_unconventional_local_names: bool = True,
    allow_standard_tag_collisions: bool = False,
) -> None:
    """
    Validate that SAM tags meet convention.

    Raises:
        ValueError if any of the defined SAM tags are invalid. All SAM tags are validated and errors
        are accumulated, so a single exception is raised with all errors.
    """
    errs: list[str] = []
    for tag in enumeration:
        err_msg = _validate_sam_tag(
            tag,
            allow_unconventional_local_names=allow_unconventional_local_names,
            allow_standard_tag_collisions=allow_standard_tag_collisions,
        )
        if err_msg is not None:
            errs.append(err_msg)

    if len(errs) > 0:
        raise ValueError(
            f"{enumeration.__name__}: The following SAM tags are invalid:\n" + "\n".join(errs)
        )


def _validate_sam_tag(
    tag: Enum,
    allow_unconventional_local_names: bool = True,
    allow_standard_tag_collisions: bool = False,
) -> str | None:
    """
    Validate an individual SAM tag.

    Returns:
        An error message if the SAM tag was invalid.
        None otherwise.
    """
    if TAG_REGEX.match(tag.value) is None:
        return f"  {tag}: SAM tags must be two-character alphanumeric strings."

    if not allow_standard_tag_collisions and tag.value in [
        standard_tag.value for standard_tag in StandardTag
    ]:
        return f"  {tag}: Locally-defined SAM tags may not conflict with a predefined standard tag."

    if not allow_unconventional_local_names and not _is_valid_local_tag(tag.value):
        return f"  {tag}: Locally-defined SAM tags must be lowercase or start with X, Y, or Z."

    return None


def _is_valid_local_tag(tag: str) -> bool:
    """
    True if the tag is a valid locally-defined tag.
    """
    return tag.startswith("X") or tag.startswith("Y") or tag.startswith("Z") or tag.islower()
