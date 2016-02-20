#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -*- coding: iso-8859-1 -*-
# -*- coding: latin-1 -*-
"""
Created on Thu Feb 18 13:18:18 2016

@author: merongoitom
"""

"""
Your task in this exercise has two steps:

- audit the OSMFILE and change the variable 'mapping' to reflect the changes needed to fix 
    the unexpected street types to the appropriate ones in the expected list.
    You have to add mappings only for the actual problems you find in this OSMFILE,
    not a generalized solution, since that may and will depend on the particular area you are auditing.
- write the update_name function, to actually fix the street name.
    The function takes a string with street name as an argument and should return the fixed name
    We have provided a simple test so that you see what exactly is expected
"""
import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import pprint

OSMFILE = "data/gothenburg_sweden.osm"
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)


expected = ["", "Savedalen", "Boulevard", "Drive", "Court", "Place", "Square", "Lane", "Road", 
            "Trail", "Parkway", "Commons"]



#expected = ["Olofstorp", "Sävedalen", "Boulevard", "Drive", "Court", "Place", "Square", "Lane", "Road", 
#            "Trail", "Parkway", "Commons"]

# UPDATE THIS VARIABLE
mapping = {}


def audit_street_type(street_types, street_name):
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            street_types[street_type].add(street_name)


def is_street_name(elem):
    return (elem.attrib['k'] == "addr:housenumber")


def audit(osmfile):
    osm_file = open(osmfile, "r")

    street_types = defaultdict(set)
    for event, elem in ET.iterparse(osm_file, events=("start",)):

        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    audit_street_type(street_types, tag.attrib['v'])
    osm_file.close()
    return street_types


def update_name(name, mapping):
    array = []
    words = list(name)
    for word in words:
        word.title()
        if word in mapping.keys():
            word = mapping[word]
        elif isinstance(word, str):
            word = word.title()
        array.append(word)
    return "".join(array)

    return name


def audit_street_type(street_types, street_name):
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            street_types[street_type].add(street_name)

def test():
    st_types = audit(OSMFILE)
    pprint.pprint(dict(st_types))

    for st_type, ways in st_types.iteritems():
        for name in ways:
            better_name = update_name(name, mapping)
            print(name), "=>", better_name
            

test()

#word = 'Hello Wor(ld'
#print re.findall(r"[\w']+",name)