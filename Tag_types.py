# -*- coding: utf-8 -*-
"""
Created on Tue Feb  9 16:54:56 2016

@author: merongoitom
"""

import xml.etree.cElementTree as ET
import pprint
import re
"""
Your task is to explore the data a bit more.
Before you process the data and add it into MongoDB, you should check the "k"
value for each "<tag>" and see if they can be valid keys in MongoDB, as well as
see if there are any other potential problems.

We have provided you with 3 regular expressions to check for certain patterns
in the tags. As we saw in the quiz earlier, we would like to change the data
model and expand the "addr:street" type of keys to a dictionary like this:
{"address": {"street": "Some value"}}
So, we have to see if we have such tags, and if we have any tags with
problematic characters.

"""


lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

#This code checks the k='value' for problamatic values,
#if its a ':' in the text, then its a 'lower_colon' value
#if theres caps letters then they are 'other'
#if theres only small letter then theyr 'lower'
#and 'problemchars' are all wierd letters such as '.#)"/€=%'

def key_type(element, keys):
    if element.tag == "tag":
        # YOUR CODE HERE
        k_value = element.attrib['k']
        
        if lower.search(k_value) is not None:
            keys['lower'] +=1
        elif lower_colon.search(k_value) is not None:
            keys['lower_colon'] +=1
        elif problemchars.search(k_value) is not None:
            keys['problemchars'] +=1
        else:
            keys['other'] +=1
        pass
        
    return keys



def process_map(filename):
    keys = {"lower": 0, "lower_colon": 0, "problemchars": 0, "other": 0}
    for _, element in ET.iterparse(filename):
        keys = key_type(element, keys)

    return keys




keys = process_map('data/gothenburg_sweden.osm')
pprint.pprint(keys)
