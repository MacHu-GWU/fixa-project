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

CHARSET_HEXSTR_LOWER = "0123456789abcdef"
CHARSET_HEXSTR_UPPER = CHARSET_HEXSTR_LOWER.upper()

# we don't use ambiguous character like O, o, l, i, and digits 0 and 1.
CHARSET_PASSWORD_LOWER = "abcdefghjkmnpqrstuvwxyz"
CHARSET_PASSWORD_UPPER = "ABCDEFHJKLMNPQRSTUVWXYZ"
CHARSET_PASSWORD_DIGITS = "23456789"
CHARSET_PASSWORD_CHAR = "!@#$%^&*"
CHARSET_PASSWORD = (
    CHARSET_PASSWORD_LOWER
    + CHARSET_PASSWORD_UPPER
    + CHARSET_PASSWORD_DIGITS
    + CHARSET_PASSWORD_CHAR
)
CHARSET_PASSWORD_NO_CHAR = (
    CHARSET_PASSWORD_LOWER
    + CHARSET_PASSWORD_UPPER
    + CHARSET_PASSWORD_DIGITS
)


def rand_str(length: int, allowed: str = CHARSET_ALPHA_DIGITS) -> str:
    """
    Generate fixed-length random string from your allowed character pool.

    :param length: total length of this string.
    :param allowed: allowed charset.

    Example::

        >>> rand_str(32)
        H6ExQPNLzb4Vp3YZtfpyzLNPFwdfnwz6
    """
    res = list()
    for _ in range(length):
        res.append(random.choice(allowed))
    return "".join(res)


def rand_hexstr(length: int, lower: bool = True) -> str:
    """
    Gererate fixed-length random hexstring, usually for md5.

    :param length: total length of this string.
    :param lower: use lower case or upper case.
    """
    if lower:
        return rand_str(length, allowed=CHARSET_HEXSTR_LOWER)
    else:
        return rand_str(length, allowed=CHARSET_HEXSTR_UPPER)


def rand_alphastr(length: int, lower: bool = True, upper: bool = True) -> str:
    """
    Generate fixed-length random alpha only string.
    """
    if lower is True and upper is True:
        return rand_str(length, allowed=string.ascii_letters)
    if lower is True and upper is False:
        return rand_str(length, allowed=string.ascii_lowercase)
    if lower is False and upper is True:
        return rand_str(length, allowed=string.ascii_uppercase)
    else:
        raise Exception


def rand_pwd(length: int = 12, special_char: bool = True) -> str:
    """Random Internet password.

    Example::

        >>> rand_pwd(12)
        TlhM$^jzculH
    """
    if length < 8:
        raise ValueError("minimal password length is 8!")

    first = random.choice(CHARSET_PASSWORD_LOWER + CHARSET_PASSWORD_UPPER)
    chars = [
        random.choice(CHARSET_PASSWORD_LOWER),
        random.choice(CHARSET_PASSWORD_UPPER),
        random.choice(CHARSET_PASSWORD_DIGITS),
    ]
    if special_char:
        chars.append(random.choice(CHARSET_PASSWORD_CHAR))
        k = length - 4
        for _ in range(k):
            chars.append(random.choice(CHARSET_PASSWORD))
    else:
        k = length - 5
        for _ in range(k):
            chars.append(random.choice(CHARSET_PASSWORD_NO_CHAR))
    random.shuffle(chars)
    return first + "".join(chars)
