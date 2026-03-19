"""Python version compatibility shims.

The project targets >=3.12, but this module allows running
tests/tools on 3.10/3.11 where StrEnum is absent.
"""

import sys

if sys.version_info >= (3, 11):
    from enum import StrEnum
else:
    from enum import Enum

    class StrEnum(str, Enum):  # type: ignore[no-redef]
        pass
