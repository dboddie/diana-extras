
# Copyright (C) 2015 MET Norway
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

"""A module providing validation functions that can be used to describe the
expected contents of data structures. This can be especially useful when
trying to describe the contents of dictionaries obtained from JSON files
when the full descriptive power of JSON-Schema is not needed.
"""

class ValidationError(Exception):
    """Indicates an error in validation."""
    pass

class Optional:
    """Describes an optional element in the description of a data structure."""
    
    def __init__(self, value):
        self.value = value

def validate(data, schema):
    """Validates the given data dictionary against the specified schema.
    
    Returns the populated dictionary if successful or raises a ValidationError
    exception if validation fails."""

    return validate_dict(data, schema, ())

def validate_dict(data, expected, path):
    """Validates the given data dictionary against the expected description on the
    specified path of the expected description in a larger schema.

    Returns the populated dictionary if successful or raises a ValidationError
    exception if not.
    """

    if type(data) != dict:
        raise ValidationError, "Expected a dictionary at %s" % path
    
    new_data = {}

    for key, expected_value in expected.items():

        try:
            value = data[key]
        except KeyError:
            if isinstance(expected_value, Optional):
                expected_value = expected_value.value
            else:
                raise ValidationError, "Missing '%s' entry in schema at %s" % (key, path)
        
        new_data[key] = validate_value(value, expected_value, path + (key,))

    return new_data

def validate_value(value, expected, path):
    """Validates the given value against an expected value at the specified path
    of the expected value in a larger schema. This general purpose function calls
    the appropriate validation function for the value's data type.
    
    Returns the value if it is valid or raises a ValidationError exception if
    not."""
    
    if type(expected) == dict:
        return validate_dict(value, expected, path)
    
    elif type(expected) == list:
        return validate_list(value, expected, path)
    
    elif type(expected) == unicode:
        if value != expected:
            raise ValidationError, "Expected '%s' at %s" % (expected, path)

    elif type(expected) == str:
        if value != expected:
            raise ValidationError, "Expected '%s' at %s" % (expected, path)

    elif expected == unicode:
        if type(value) != unicode:
            raise ValidationError, "Expected unicode at %s" % path
    
    elif expected == int:
        if type(value) != int:
            raise ValidationError, "Expected integer at %s" % path
    
    elif expected == float:
        if type(value) != float:
            raise ValidationError, "Expected float at %s" % path
    
    else:
        try:
            value = expected.validate(value)
        except ValueError:
            raise ValidationError, "Failed to validate value at %s" % path
    
    return value

def validate_list(value, expected, path):
    """Validates the given list value against an expected list at the specified
    path of the expected list in a larger schema.

    Returns the populated list if successful or raises a ValidationError exception
    if not."""

    if type(value) != list:
        raise ValidationError, "Expected a list at %s" % path
    
    # The expected value is a list with one item that specifies the required type.
    expected_item = expected[0]
    
    new_list = []

    for item in value:
        new_list.append(validate_value(item, expected_item, path))

    return new_list
