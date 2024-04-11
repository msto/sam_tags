# sam_tags

[![CI](https://github.com/msto/sam_tags/actions/workflows/python_package.yml/badge.svg?branch=main)](https://github.com/msto/sam_tags/actions/workflows/python_package.yml?query=branch%3Amain)
[![Python Versions](https://img.shields.io/badge/python-3.11_|_3.12-blue)](https://github.com/msto/sam_tags)
[![MyPy Checked](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://docs.astral.sh/ruff/)

SAM tags

## Quickstart

The `sam_tags` decorator permits the specification of custom enumerations that adhere to the conventions described in the SAM specification.

```py
from enum import StrEnum
from sam_tags import sam_tag


@sam_tag
class CustomTag(StrEnum):
    """Custom SAM tags."""

    XF = "XF"
    """Some filter."""

    vl = "vl"
    """Some value."""
```

The predefined standard tags are available as a built-in class.

```py
from sam_tags import StandardTag

# read: pysam.AlignedSegment
read.get_tag(StandardTag.RX)
```

Docstrings on each predefined tag permit simple reference within an IDE. 

![](assets/screenshot.png)

Built-in classes are also available for sets of tags used in popular bioinformatics software.

```py
from sam_tags.community import BwaTag
from sam_tags.community import CellrangerTag
```
