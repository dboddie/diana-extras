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
from xml.etree.ElementTree import Element, ElementTree, SubElement
import llf_schema

from PyQt4.QtCore import Qt

def read_file(file_name):

    d = json.JSONDecoder()
    data = open(file_name, "rb").read()
    
    # Try to decode the data. This raises a ValueError if it fails.
    llf = d.decode(data)
    
    return llf_schema.File().validate(llf)
    

if __name__ == "__main__":

    if not 2 <= len(sys.argv) <= 3:

        sys.stderr.write("Usage: %s <LLF GeoJSON file> [KML file for Diana]\n" % sys.argv[0])
        sys.exit(1)
    
    geojson_file = sys.argv[1]
    
    if len(sys.argv) == 3:
        kml_file = sys.argv[2]
    else:
        kml_file = None

    llf = read_file(geojson_file)

    kml = Element('kml')
    kml.set('xmlns', "http://www.opengis.net/kml/2.2")
    doc = SubElement(kml, 'Document')
    
    # Obtain information about each timestep in the file.
    for timestep in llf:
    
        for feature in timestep['forecast']:
        
            folder = SubElement(doc, 'Folder')
            name = SubElement(folder, 'name')
            name.text = ''
            valid = timestep['valid']
            
            timespan = SubElement(folder, 'TimeSpan')
            begin = SubElement(timespan, 'begin')
            begin.text = unicode(feature['properties']['valid']['from'].toString("yyyy-MM-ddThh:mm:ssZ"))
            end = SubElement(timespan, 'end')
            end.text = unicode(feature['properties']['valid']['to'].toString("yyyy-MM-ddThh:mm:ssZ"))
            
            polygons = feature['geometry']['coordinates']
            for coords in polygons:
            
                placemark = SubElement(folder, 'Placemark')
                SubElement(placemark, 'name').text = feature['properties']['parameterGroup']
                SubElement(placemark, 'description').text = ''
                
                extdata = SubElement(placemark, 'ExtendedData')
                data = SubElement(extdata, 'Data')
                data.set('name', u'met:objectType')
                SubElement(data, 'value').text = 'PolyLine'
                
                polygon = SubElement(placemark, 'Polygon')
                SubElement(polygon, 'tessellate').text = '1'
                
                boundary = SubElement(polygon, 'outerBoundaryIs')
                ring = SubElement(boundary, 'LinearRing')
                coordinates = SubElement(ring, 'coordinates')
                text = u''
                
                for coord in coords:
                    line = u"%f,%f,0\n" % (coord.x(), coord.y())
                    text += line
                
                coordinates.text = text
    
    if not kml_file:
        f = sys.stdout
    else:
        f = open(kml_file, 'wb')
    
    ElementTree(kml).write(f, 'utf-8', '<?xml version="1.0" encoding="UTF-8"?>')
