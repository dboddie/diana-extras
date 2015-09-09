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

import json, sys
import schema

class LLF_Error(Exception):
    pass

class LLF_File:

    schema = {
        "header": {
            "status": unicode,
            "group":  unicode,
            "locale": unicode,
            "ref":    schema.Time("HH"),
            "start":  schema.Time("HH"),
            "date":   schema.Time("yyMMdd"),
            "end":    schema.Time("HH"),
            "type":   unicode,
            "areas":  [unicode]
            },
        "timesteps": [
            {
                "range":    [int],
                "valid":    [schema.Time("yyyy-MM-ddTHH:mm:ss.zzzZ")],
                "forecast": {
                    "type": "FeatureCollection",
                    "features": [
                        {
                            "geometry": {
                                "type": "Polygon",
                                "coordinates": [
                                    [schema.LonLat()]
                                    ]
                                },
                            "type": "Feature",
                            "properties": {
                                "timeStep": schema.Time("yyyy-MM-ddTHH:mm:ss.zzzZ"),
                                "refTime": schema.Time("yyyy-MM-ddTHH:mm:ss.zzzZ"),
                                "parameterGroup": unicode,
                                "valid": {
                                    "to": schema.Time("yyyy-MM-ddTHH:mm:ss.zzzZ"),
                                    "from": schema.Time("yyyy-MM-ddTHH:mm:ss.zzzZ")
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
        
        schema.validate(llf, LLF_File.schema)


if __name__ == "__main__":

    if len(sys.argv) != 3:

        sys.stderr.write("Usage: %s <LLF GeoJSON file> <KML file for Diana>\n" % sys.argv[0])
        sys.exit(1)
    
    geojson_file, kml_file = sys.argv[1:3]

    llf = LLF_File(geojson_file)
