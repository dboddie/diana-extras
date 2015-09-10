#!/usr/bin/env python

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

import json, pprint, sys
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

ISODate = Time("yyyy-MM-ddTHH:mm:ss.zzzZ")

class LLF_File:

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
        "timesteps": [
            {
                "range":    [int],
                "valid":    [ISODate],
                "forecast": {
                    "type": "FeatureCollection",
                    "features": [
                        {
                            "geometry": {
                                "type": "Polygon",
                                "coordinates": [
                                    [LonLat()]
                                    ]
                                },
                            "type": "Feature",
                            "properties": {
                                "timeStep": ISODate,
                                "refTime": ISODate,
                                "parameterGroup": unicode,
                                "valid": {
                                    "to": ISODate,
                                    "from": ISODate
                                    },
                                "parameters": { # Do not validate - depends on product type.
                                    }
                                },
                        }]
                    }
            }]
        }
    
    def __init__(self, file_name = None):

        if file_name:
            self.read(file_name)

    def read(self, file_name):
    
        d = json.JSONDecoder()
        try:
            data = open(file_name, "rb").read()
        except IOError:
            raise LLF_Error, "Failed to read file: %s" % file_name
        
        # Try to decode the data. This raises a ValueError if it fails.
        llf = d.decode(data)
        
        self.contents = schema.validate(llf, LLF_File.schema)


if __name__ == "__main__":

    if len(sys.argv) != 3:

        sys.stderr.write("Usage: %s <LLF GeoJSON file> <KML file for Diana>\n" % sys.argv[0])
        sys.exit(1)
    
    geojson_file, kml_file = sys.argv[1:3]

    llf = LLF_File(geojson_file)
    pprint.pprint(llf.contents)
