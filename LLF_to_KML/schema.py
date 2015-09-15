
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

class ValidationError(Exception):
    pass

class Optional:

    def __init__(self, value):
        self.value = value

def validate(data, schema):

    return validate_dict(data, schema, ())

def validate_dict(data, expected, path):

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

    if type(value) != list:
        raise ValidationError, "Expected a list at %s" % path
    
    # The expected value is a list with one item that specifies the required type.
    expected_item = expected[0]
    
    new_list = []

    for item in value:
        new_list.append(validate_value(item, expected_item, path))

    return new_list
