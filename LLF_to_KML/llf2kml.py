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
import llf_schema

def read_file(file_name):

    d = json.JSONDecoder()
    data = open(file_name, "rb").read()
    
    # Try to decode the data. This raises a ValueError if it fails.
    llf = d.decode(data)
    
    return llf_schema.File().validate(llf)
    

if __name__ == "__main__":

    if len(sys.argv) != 3:

        sys.stderr.write("Usage: %s <LLF GeoJSON file> <KML file for Diana>\n" % sys.argv[0])
        sys.exit(1)
    
    geojson_file, kml_file = sys.argv[1:3]

    llf = read_file(geojson_file)
    
    for timestep in llf:
        print timestep['valid']
        for feature in timestep['forecast']:
            print feature
