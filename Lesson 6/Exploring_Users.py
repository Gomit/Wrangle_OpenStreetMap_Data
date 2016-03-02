# -*- coding: utf-8 -*-
"""
Created on Wed Mar  2 15:50:56 2016

@author: merongoitom
"""

#!/usr/bin/env python
# -*- coding: utf-8 -*-
import xml.etree.cElementTree as ET
import pprint
import re
"""
Your task is to explore the data a bit more.
The first task is a fun one - find out how many unique users
have contributed to the map in this particular area!

The function process_map should return a set of unique user IDs ("uid")
"""

def get_user(element):
    return


def process_map(filename):
    users = set()
    for not_node, element in ET.iterparse(filename):
        if element.tag == "node" or element.tag == "way" or element.tag == "relation":
            users.add(element.attrib['user'])

    print len(users)
    return users


def test():

    users = process_map('example.osm')
    pprint.pprint(users)
    assert len(users) == 6



if __name__ == "__main__":
    test()