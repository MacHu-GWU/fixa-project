# -*- coding: utf-8 -*-

"""
Reference:

- https://docs.python.org/3/library/sys.html#sys.platform
"""

import sys

IS_WINDOWS = False
IS_MACOS = False
IS_LINUX = False

_platform = sys.platform
if _platform in ["win32", "cygwin"]:
    IS_WINDOWS = True
elif _platform == "darwin":
    IS_MACOS = True
elif _platform == "linux":
    IS_LINUX = True
else:
    pass
