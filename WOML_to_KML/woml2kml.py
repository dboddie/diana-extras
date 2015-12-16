#!/usr/bin/env python

import sys

from lxml.etree import ElementTree

validTimeBegin = 'gml:validTime/gml:TimePeriod/gml:beginPosition'
validTimeEnd = 'gml:validTime/gml:TimePeriod/gml:endPosition'

if __name__ == "__main__":

    if len(sys.argv) != 3:
        sys.stderr.write("Usage: %s <WOML file> <KML file>\n" % sys.argv[0])
        sys.exit(1)
    
    tree = ElementTree(file=open(sys.argv[1]))
    root = tree.getroot()
    
    nsmap = root.nsmap
    begin = root.find(validTimeBegin, nsmap).text
    end = root.find(validTimeEnd, nsmap).text
    print begin, end
    print
    
    objects = root.findall('.//womlcore:member/womlswo:*', nsmap)
    timespans = {}
    
    for obj in objects:
    
        begin = obj.find(validTimeBegin, nsmap).text
        end = obj.find(validTimeEnd, nsmap).text
        print obj, begin, end
        
        
