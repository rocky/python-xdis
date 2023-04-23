# Copyright (c) 2023 by Rocky Bernstein
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


class LongTypeForPython3(int):
    """
    Define a Python3 long integer type which exists in
    Python 2 but does not exist in Python 3.
    """

    def __init__(self, value):
        self.value = value

    def __repr__(self):
        """
        Replacement __str__ and str() for Python3.
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

    def __repr__(self):
        """
        Replacement __str__ and str() for Python3.
        This ensures we get the "u" suffix on unicode types.
        """
        try:
            value = self.value.decode("utf-8")
            # Do we need to handle utf-16 and utf-32?
        except UnicodeDecodeError:
            return f"""u'{str(self.value)[1:]}'"""
        else:
            return f"""u'{str(value)}'"""
