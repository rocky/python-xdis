# Copyright (c) 2023-2024 by Rocky Bernstein
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
"""
Defines types from one set of Python versions that don't exist in
another set of Pythons
"""


# From
# https://stackoverflow.com/questions/196345/how-to-check-if-a-string-in-python-is-in-ascii
def is_ascii(s: str) -> bool:
    """Check if the characters in string s are in ASCII, U+0-U+7F."""
    return len(s) == len(s.encode())


class LongTypeForPython3(int):
    """
    Define a Python3 long integer type which exists in
    Python 2 but does not exist in Python 3.
    """

    def __init__(self, value):
        self.value = value

    def __repr__(self) -> str:
        """
        Replacement repr() and str() for Python3.
        This ensures we get the "L" suffix on long types.
        """
        return f"""{self.value}L"""


class UnicodeForPython3(str):
    """
    Define a Python3 unicode type which exists in
    Python 2 but does not exist in Python 3.
    """

    def __init__(self, value):
        self.value = value

    def __eq__(self, other) -> bool:
        return self.value == other or self.value.decode("utf-8") == other

    def __hash__(self) -> int:
        return id(self.value)

    def __repr__(self) -> str:
        r"""
        Replacement repr() for Python3.
        This ensures we get the "u" suffix on unicode types,
        and also \u when the string is not ASCII representable
        """
        try:
            utf8_value = self.value.decode("utf-8")
            # Do we need to handle utf-16 and utf-32?
        except UnicodeDecodeError:
            return f"""u'{str(self.value)[1:]}'"""

        if is_ascii(utf8_value):
            return f"""u'{utf8_value}'"""

        # Turn the unicode character into its Unicode code point,
        # but strip of the leading "0x".
        stripped_utf8 = utf8_value[len("0x") :]
        unicode_codepoint = "".join(
            (c if is_ascii(c) else hex(ord(c)) for c in stripped_utf8)
        )
        return rf"""u'\u{unicode_codepoint}'"""

    def __str__(self) -> str:
        try:
            utf8_value = self.value.decode("utf-8")
            # Do we need to handle utf-16 and utf-32?
        except UnicodeDecodeError:
            return f"""u'{str(self.value)[1:]}'"""

        return f"""{utf8_value}"""
