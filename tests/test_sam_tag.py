from enum import Enum
from enum import StrEnum

import pytest

from sam_tags import StandardTag
from sam_tags import sam_tag


def test_sam_tag() -> None:
    """Test that we can declare a custom SAM tag."""

    @sam_tag
    class CustomTag(StrEnum):
        XG = "XG"


def test_sam_tag_with_callable_decorator() -> None:
    """Test that we can use the decorator with callable syntax."""

    @sam_tag()
    class CustomTag(StrEnum):
        XG = "XG"


def test_sam_tag_raises_if_not_str() -> None:
    """
    Test that we raise a TypeError if the decorated class is not a `StrEnum` or
    `str` mixin.
    """

    with pytest.raises(
        TypeError,
        match="BadTag: SAM tag classes should inherit from `StrEnum` or mix in `str`.",
    ):

        @sam_tag
        class BadTag(Enum):
            XG = "XG"


def test_sam_tag_raises_if_not_enum() -> None:
    """
    Test that we raise a TypeError if the decorated class is not an `Enum`.
    """

    with pytest.raises(
        TypeError,
        match="BadTag: The `sam_tag` decorator may only be applied to `Enum` subclasses.",
    ):
        # NB: mypy (accurately) flags that `sam_tag` requires an enumeration
        # type, but we want to test that this is also enforced at runtime for
        # contexts where the user is not running a type checker.
        @sam_tag
        class BadTag(str):  # type: ignore[type-var]
            XG = "XG"


@pytest.mark.parametrize(
    "tag",
    [
        "",  # empty string
        "a",  # 1 character
        "abc",  # 3 character
        "1a",  # starts with number
    ],
)
def test_sam_tag_raises_if_tags_are_not_two_characters(tag: str) -> None:
    """
    Test that we raise a ValueError if any of the enumeration's values are not
    two-character strings.
    """

    with pytest.raises(ValueError, match="BadTag: The following SAM tags are invalid") as excinfo:

        @sam_tag
        class BadTag(StrEnum):
            XB = tag

    msg = str(excinfo.value)
    assert msg.endswith(f"{tag}: SAM tags must be two-character alphanumeric strings.")


def test_sam_tag_raises_if_tags_are_not_unique() -> None:
    """
    Test that we raise a ValueError if any of the enumeration's values are not
    unique.
    """

    with pytest.raises(ValueError, match="duplicate values found"):

        @sam_tag
        class BadTag(StrEnum):
            XB = "xb"
            XC = "xb"


@pytest.mark.parametrize("standard_tag", [tag.value for tag in StandardTag])
def test_sam_tag_raises_if_tag_conflicts_with_standard(
    standard_tag: str,
) -> None:
    """
    Test that we raise a ValueError if any of the enumeration's values conflict
    with a predefined standard tag.
    """

    with pytest.raises(ValueError, match="BadTag: The following SAM tags are invalid:") as excinfo:

        @sam_tag
        class BadTag(StrEnum):
            XB = standard_tag

    msg = str(excinfo.value)
    assert msg.endswith(
        f"{standard_tag}: Locally-defined SAM tags may not conflict with a predefined standard "
        "tag."
    )


def test_sam_tag_raises_if_tag_is_not_valid_local() -> None:
    """
    Test that we raise a ValueError if any of the enumeration's values don't
    adhere to SAM conventions for locally-defined tags.
    """

    with pytest.raises(ValueError, match="BadTag: The following SAM tags are invalid:") as excinfo:

        @sam_tag
        class BadTag(StrEnum):
            XB = "AA"

    msg = str(excinfo.value)
    assert msg.endswith("AA: Locally-defined SAM tags must be lowercase or start with X, Y, or Z.")


def test_sam_tag_allows_invalid_local_when_not_strict() -> None:
    """
    Test that we permit tags which don't adhere to SAM conventions for
    locally-defined tags when `strict=False`.
    """

    try:

        @sam_tag(strict=False)
        class BadTag(StrEnum):
            XB = "AA"

    except ValueError:
        raise AssertionError(
            "Unconventional tags should be permitted when `strict=False`"
        ) from None
