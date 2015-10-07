
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

"""Describes data types used in the structure of LLF GeoJSON files.

This module uses functions in the schema module to validate the contents of
dictionaries obtained from GeoJSON files.
"""

import schema

class LLF_Error(Exception):
    pass

from PyQt4.QtCore import QDateTime, QPointF

class Time:

    def __init__(self, format):
        self.format = format

    def validate(self, value):
    
        dateTime = QDateTime.fromString(value, self.format)
        if dateTime.isValid():
            return dateTime
        else:
            raise ValueError

class ShortDate(Time):

    def __init__(self):
        Time.__init__(self, "yyMMdd")

    def validate(self, value):

        dateTime = Time.validate(self, value)
        return dateTime.addYears(100)

class Hour(Time):

    def __init__(self):
        Time.__init__(self, "HH")

    def validate(self, value):

        return Time.validate(self, value).time().hour()

class LonLat:

    def validate(self, value):
    
        if len(value) != 2:
            raise ValueError
        elif not -180.0 <= value[0] <= 180.0:
            raise ValueError
        elif not -90.0 <= value[1] <= 90.0:
            raise ValueError
        else:
            return QPointF(value[0], value[1])

class IntRange:

    def __init__(self, minimum, maximum):
        self.minimum = minimum
        self.maximum = maximum
    
    def validate(self, value):
    
        if not self.minimum <= value <= self.maximum:
            raise ValueError
        else:
            return value

class OneOf:

    def __init__(self, choices):
        self.choices = choices
    
    def validate(self, value):
    
        if value in self.choices:
            return value
        else:
            raise ValueError

class AnyEntries:

    def __init__(self, expected_dict):
        self.expected_dict = expected_dict
    
    def validate(self, value_dict):
    
        for key, value in value_dict.items():
            schema.validate(value, self.expected_dict)
        
        return value_dict

ISODate = Time("yyyy-MM-ddTHH:mm:ss.zzzZ")

class SchemaElement:

    def __init__(self, schema):
        self.schema = schema

class Properties(SchemaElement):

    parameterGroups = {
        "vis-cld": {
            "presentweather": {
                "local": [unicode],
                "general": [unicode]
                },
            "cloudbase": {
                "local": {
                    "to": IntRange(0, 9999),
                    "from": IntRange(0, 9999)
                    },
                "general": {
                    "to": IntRange(0, 9999),
                    "from": IntRange(0, 9999)
                    }
                },
            "visibility": {
                "local": {
                    "to": IntRange(0, 9999),
                    "from": IntRange(0, 9999)
                    },
                "general": {
                    "to": IntRange(0, 9999),
                    "from": IntRange(0, 9999)
                    }
                }
            },
        "ctop": {
            "cloudtop": {
                "from": IntRange(0, 99),
                "to": IntRange(0, 9999),
                },
            "turbulence": {
                "from": OneOf(["FBL", "MOD", "SEV"]),
                "to": OneOf(["FBL", "MOD", "SEV"]),
                }
            },
        "zero": {
            "freezinglvl": {
                "from": IntRange(0, 125),
                "to": IntRange(0, 125),
                },
            "neglayer": {
                "from": IntRange(0, 125),
                "to": IntRange(0, 125),
                }
            },
        "ice": {
            "icinglvl": {
                "from": IntRange(0, 99),
                "to": IntRange(0, 9999),
                },
            "intensity": {
                "from": OneOf(["FBL", "MOD", "SEV"]),
                "to": OneOf(["FBL", "MOD", "SEV"]),
                }
            },
        "hwnd-tmp": {
            "highwind": AnyEntries({
                "FL100": {
                    "windspeed": IntRange(0, 99),
                    "winddirection": IntRange(0, 360)
                    },
                "FL050": {
                    "windspeed": IntRange(0, 99),
                    "winddirection": IntRange(0, 360)
                    },
                "2000ft": {
                    "windspeed": IntRange(0, 99),
                    "winddirection": IntRange(0, 360)
                    }
                }),
            "temperature": AnyEntries({
                "FL100": {
                    "temp": IntRange(-40, 50)
                    },
                "FL050": {
                    "temp": IntRange(-40, 50)
                    },
                "2000ft": {
                    "temp": IntRange(-40, 50)
                    }
                })
            },
        "wnd": {
            "windspeed": {
                "from": IntRange(0, 99),
                "to": IntRange(0, 99),
                },
            "winddirection": IntRange(0, 360)
            },
        "gust": {
            "from": IntRange(0, 99),
            "to": IntRange(0, 99),
            },
        "turb": {
            "turbulence": {
                "from": IntRange(0, 125),
                "to": IntRange(0, 125),
                },
            "intensity": {
                "from": OneOf(["FBL", "MOD", "SEV"]),
                "to": OneOf(["FBL", "MOD", "SEV"]),
                }
            },
        "qnh": {
            "pressure": IntRange(0, 1000)
            }
        }
    
    def validate(self, value):
    
        completed = schema.validate(value, self.schema)
        
        paraSchema = Properties.parameterGroups[value["parameterGroup"]]
        completed["parameters"] = schema.validate(value["parameters"], paraSchema)
        
        return LLF_Properties(completed)

class Feature(SchemaElement):

    def validate(self, value):
        return LLF_Feature(schema.validate(value, self.schema))

class Forecast(SchemaElement):

    def validate(self, value):
        return LLF_Forecast(schema.validate(value, self.schema))

class File:

    """Represents an LLF GeoJSON file, describing the expected structure and
    contents of this kind of file.

    To validate JSON data against this description, first decode it to a
    dictionary then call the validate method on an instance of this class,
    passing the dictionary as an argument.
    """

    schema = {
        "header": {
            "status": unicode,
            "group":  unicode,
            "locale": unicode,
            "ref":    Hour(),
            "start":  Hour(),
            "date":   ShortDate(),
            "end":    Hour(),
            "type":   unicode,
            "areas":  [unicode]
            },
        
        "timesteps": [ {
            "range":    [int],
            "valid":    [ISODate],
            "forecast": Forecast( {
                "type": "FeatureCollection",
                "features": [ Feature( {
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [ [LonLat()] ]
                        },
                    "type": "Feature",
                    "properties": Properties( {
                        "timeStep": ISODate,
                        "refTime": ISODate,
                        "parameterGroup": unicode,
                        "valid": {
                            "to": ISODate,
                            "from": ISODate
                            }
                        } )
                    } ) ]
                } )
            } ]
        }

    def validate(self, value):
    
        """Validates the Python dictionary, value, against the expected structure
        and contents of an LLF GeoJSON file, returning an LLF_File instance if
        successful or raising an exception if not.
        """

        # Note that the schema object here refers to the module, not the
        # attribute of this class.
        return LLF_File(schema.validate(value, File.schema))

# Containers for validated data

class LLF_Element:

    def __init__(self, contents):

        self.contents = contents

    def keys(self):

        return self.contents.keys()

    def __getitem__(self, key):

        return self.contents[key]

class LLF_Container(LLF_Element):

    def __getitem__(self, index):
    
        if type(index) == int:
            return self.contents[self.container_attr][index]
        else:
            return LLF_Element.__getitem__(self, index)
    
    def __len__(self):

        return len(self.contents[self.container_attr])

class LLF_Properties(LLF_Element):

    pass

class LLF_Feature(LLF_Element):

    pass

class LLF_Forecast(LLF_Container):

    container_attr = "features"

class LLF_File(LLF_Container):

    """Represents a valid LLF GeoJSON file whose contents can be accessed
    via the contents attribute or using dictionary-like methods."""

    container_attr = "timesteps"
