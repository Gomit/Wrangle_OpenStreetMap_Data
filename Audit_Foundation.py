# -*- coding: utf-8 -*-
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


expected = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Square", "Lane", "Road", 
            "Trail", "Parkway", "Commons"]

# UPDATE THIS VARIABLE
mapping = { "SE-426": "426",                #Erased 'SE-'
            #"Hovås": "436 50",             # 'å' is not part of the UTF-8 standard apparently, 
                                            #the postal code for Hovås should in any case be changed somehow
            "12":"412 74",                  #the actual postal code
            "417631":"417 63"               #deleted the '1' at the end
            }


def audit_street_type(street_types, street_name):
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            street_types[street_type].add(street_name)


def is_street_name(elem):
    return (elem.attrib['k'] == "addr:postcode")


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
    array = []                          #empty array
    words = name.split(' ')             #split postcode based on empty space ' '
    for word in words:                  #for each word
        if word in mapping.keys():      #check with the key:value pairs in the 'mapping' object above
            word = mapping[word]        #if the key matches, replace it with the new key
        array.append(word)              #then append it to array
    return " ".join(array)              #join the entire array
    
    return name


def test():                             #this test gives the output presenting the changes made
    st_types = audit(OSMFILE)
    pprint.pprint(dict(st_types))

    for st_type, ways in st_types.iteritems():
        for name in ways:
            better_name = update_name(name, mapping)
            print name, "=>", better_name
test()
            
#word = 'Hello Wor(ld'
#print re.findall(r"[\w']+",name)

