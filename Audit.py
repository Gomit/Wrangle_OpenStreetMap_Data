# -*- coding: utf-8 -*-
"""
Created on Thu Feb 18 13:18:18 2016

@author: merongoitom
"""
import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import pprint

OSMFILE = "data/gothenburg_sweden.osm"
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)


expected_cities = ["Agnesberg",     "Angered",       "Askim",        u"Asper\xf6",      u"K\xf6pstads\xf6",
                   "Bohus",         u"Dons\xf6",     "Gunnilse",     u"G\xf6teborg",    u"Hisings k\xe4rra",
                   "Hisings backa", u"Hov\xe5s",     u"Kung\xe4lv",  u"Br\xe4nn\xf6",   u"V\xe4stra fr\xf6lunda",
                   "Billdal",       u"M\xf6lndal",   u"N\xf6dinge",  u"K\xf6pstads\xf6",
                   u"Styrs\xf6",    u"S\xe4ve",      "Torslanda",    u"Vr\xe5ng\xf6",
                   "Askim",         u"\xd6cker\xf6", "Olofstorp"]
#expected = ["Agnesberg","Angered","Askim","Asperö","Billdal","Bohus","Brännö","Donsö","Gunnilse","Göteborg","Hisings backa","Hisings kärra","Hovås","Kungälv","Köpstadsö","Mölndal","Nödinge","Olofstorp","Styrsö","Säve","Torslanda","Vrångö","Västra frölunda","Öckerö"] 


mapping_city = { "Gothenburg"            : "Göteborg",                           
                 "436 58"                : u"Hov\xe5s",                          
                 u"Hisings K\xe4rra"     : u"Hisings k\xe4rra",                  
                 u"V\xe4stra Fr\xf6lunda": u"V\xe4stra frölunda",
                 u"V\xe2stra Fr\xf6lunda": u"V\xe4stra fr\xf6lunda",
                 u"Hisings K\xe4rra"     : u"Hisings k\xe4rra"
            }# Map incorrect city names to desired


mapping_post_code = { "SE-42671": "42671",
                     u"Hov\xe5s": "43650",
                     "12"       : "41274", 
                     "417631"   : "41763"  
                     }# Map incorrect postcode to desired

def audit_type(types, name):
    m = street_type_re.search(name)
    if m:
        audit = m.group()
        types[audit].add(name)

def audit_city_type(types, name):
    m = street_type_re.search(name)
    if m:
        city_audit = m.group()
        if city_audit not in expected_cities:
            types[city_audit].add(name)
#================================================================
 #Audit cities
#================================================================

def audit_city(osmfile):
    osm_file = open(osmfile, "r")
    city_types = defaultdict(set)
    for event, elem in ET.iterparse(osm_file, events=("start",)):

        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_city_name(tag):
                    audit_city_type(city_types, tag.attrib['v'])
    osm_file.close()
    return city_types


def is_city_name(elem):
    return (elem.attrib['k'] == "addr:city")


def update_city_name(name):
    if name in mapping_city.keys():
        name = mapping_city[name]
        return name
    return name


# Uncomment the block below to see changes made
""" 
def test(audit,update):                                                         
    st_types = audit(OSMFILE)                                                   
    #pprint.pprint(dict(st_types))

    for st_type, ways in st_types.iteritems():
        for name in ways:
            better_name = update(name)
            print name, "=>", better_name

test(audit_city,update_city_name)   


#NOTE: Some cities do not lie within Gothenburg municipality, see list below
#Bad Cities =  Öckerö, Landvetter, Mölnlycke, mölnlycke, Stenkullen, Härryda, Kållered, Lerum, lerum
#              Partille, Partile, Lindome, Hönö, Jonsered, Sävedalen, Öjersjö, öjersjö

#Good Cities = Hisings kärra, Hovås, Hisings Backa, Västra Frölunda, Vâstra Frölunda, Gothenburg     
"""

#================================================================
 #Audit postcode
#================================================================

def audit_post_code(osmfile):
    osm_file = open(osmfile, "r")
    postcode_types = defaultdict(set)
    for event, elem in ET.iterparse(osm_file, events=("start",)):
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_post_code(tag):
                    audit_type(postcode_types, tag.attrib['v'])
    
    osm_file.close()
    return postcode_types


def is_post_code(elem):
    return (elem.attrib['k'] == "addr:postcode")


def update_post_code(name):                                                               
    words = name.replace(" ", "")                                               
    if words.isdigit() == False or len(words) != 5:                             
        if words in mapping_post_code.keys():                                             
            words = mapping_post_code[words]                                    
            return words
    count = 0
    result = ''
    for a in words:
        count +=1
        if count == 3:
            result+=a+' '
        else:
            result +=a
    return result                                                      


# Uncomment the block below to see changes made
                                                                            
def test(audit,update):                                                       
    st_types = audit(OSMFILE)
    #pprint.pprint(dict(st_types))

    for st_type, ways in st_types.iteritems():
        for name in ways:
            words = name.replace(" ", "")
            #better_name = update(words)
            #print words, "=>", better_name
            
            if words.isdigit() == False or len(words) != 5:
                better_name = update(words)
                print words, "=>", better_name
                
            #if words < '40010' or words > '47500':                             
            #    print words                                                    
                
test(audit_post_code,update_post_code)

#================================================================
 #Audit house numbers
#================================================================

def audit_house_number(osmfile):
    osm_file = open(osmfile, "r")

    house_number_types = defaultdict(set)
    for event, elem in ET.iterparse(osm_file, events=("start",)):

        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_house_number(tag):
                    audit_type(house_number_types, tag.attrib['v'])
    osm_file.close()
    return house_number_types

def is_house_number(elem):
    return (elem.attrib['k'] == "addr:housenumber")

def update_house_number(name):                                                  
    result = []
    new_string = name.upper()
    groups = [group.replace(" ", "") for group in new_string.split(';')]
    for group in groups:
        if re.match(r'\d{1,5}-\d{1,5}', group):
            if all(i.isdigit() == True for i in group.replace("-", "")): 
                group_range = map(int, group.split('-'))
                if group_range[0] < group_range[1]:
                    result += list(map(str, range(group_range[0], group_range[1]+1)))
                else:
                    result += list(map(str, range(group_range[1], group_range[0]+1)))
        elif re.match(r'\d{1,5}', group):
            result.append(group)
        else:
            result.append(group)
    return result
    
# Uncomment the block below to see changes made
"""                                                                            
def test(audit,update):                                                        
    st_types = audit(OSMFILE)
    #pprint.pprint(dict(st_types))
    for st_type, ways in st_types.iteritems():
        for name in ways:
            better_name = update(name)                                    
            print "".join(name), "=>", better_name              
   
test(audit_house_number,update_house_number)
"""



