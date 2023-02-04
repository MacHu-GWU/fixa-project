# -*- coding: utf-8 -*-

"""
This module provides some easy function to generate random text from built-in 
templates.

- :func:`rand_str`: fixed-length string
- :func:`rand_hexstr`: fixed-length hex string
- :func:`rand_pwd`: random password
"""

import random
import string

CHARSET_ALPHA_DIGITS = string.ascii_letters + string.digits
CHARSET_PASSWORD = CHARSET_ALPHA_DIGITS + "!@#$%^&*()"
CHARSET_HEXSTR_LOWER = "0123456789abcdef"
CHARSET_HEXSTR_UPPER = CHARSET_HEXSTR_LOWER.upper()
DOMAIN_SURFIX = ["com", "net", "org", "edu"]


def rand_str(length, allowed=CHARSET_ALPHA_DIGITS):
    """Generate fixed-length random string from your allowed character pool.

    :param length: total length of this string.
    :param allowed: allowed charset.

    Example::

        >>> import string
        >>> rand_str(32)
        H6ExQPNLzb4Vp3YZtfpyzLNPFwdfnwz6
    """
    res = list()
    for _ in range(length):
        res.append(random.choice(allowed))
    return "".join(res)


def rand_hexstr(length, lower=True):
    """Gererate fixed-length random hexstring, usually for md5.

    :param length: total length of this string.
    :param lower: use lower case or upper case.
    """
    if lower:
        return rand_str(length, allowed=CHARSET_HEXSTR_LOWER)
    else:
        return rand_str(length, allowed=CHARSET_HEXSTR_UPPER)


def rand_alphastr(length, lower=True, upper=True):
    """Generate fixed-length random alpha only string."""
    if lower is True and upper is True:
        return rand_str(length, allowed=string.ascii_letters)
    if lower is True and upper is False:
        return rand_str(length, allowed=string.ascii_lowercase)
    if lower is False and upper is True:
        return rand_str(length, allowed=string.ascii_uppercase)
    else:
        raise Exception


def rand_pwd(length):
    """Random Internet password.

    Example::

        >>> rand_pwd(12)
        TlhM$^jzculH
    """
    return rand_str(length, CHARSET_PASSWORD)
