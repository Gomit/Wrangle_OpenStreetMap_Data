# -*- coding: utf-8 -*-
"""
Created on Fri Feb 19 16:19:16 2016

@author: merongoitom
"""
from pprint import pprint
import re
import xml.etree.ElementTree as ET




def process_zipcode(string):
    result = []
    groups = [group.strip() for group in string.split(';')]
    for group in groups:
        if re.match(r'\d{1,5}-\d{1,5}', group):
            group_range = map(int, group.split('-'))
            if group_range[0] < group_range[1]:
                result += list(map(str, range(group_range[0], group_range[1]+1)))
            else:
                result += list(map(str, range(group_range[1], group_range[0]+1)))
        elif re.match(r'\d{1,5}', group):
            result.append(group)
    return result





def test_zipcode():
    string = "1117; 1113-1111"
    zipcodes = process_zipcode(string)
    print zipcodes
    #assert zipcodes == ['78727', '78727', '78728', '78729']

test_zipcode()


