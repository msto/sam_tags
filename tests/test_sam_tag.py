from enum import Enum
from enum import StrEnum

import pytest

from sam_tags import sam_tag


def test_sam_tag() -> None:
    """Test that we can declare a custom SAM tag."""

    @sam_tag
    class CustomTag(StrEnum):
        XG = "XG"


def test_sam_tag_raises_if_not_str() -> None:
    """
    Test that we raise a TypeError if the decorated class is not a `StrEnum` or
    `str` mixin.
    """

    with pytest.raises(
        TypeError,
        match="SAM tags should inherit from `StrEnum` or mix in `str`.",
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
        match="The `sam_tag` decorator may only be applied to `Enum` classes.",
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

    with pytest.raises(
        ValueError, match=f"SAM tags must be two-character alphanumeric strings: {tag}"
    ):

        @sam_tag
        class BadTag(StrEnum):
            XB = tag


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
