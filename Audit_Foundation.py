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


expected_cities = ["Agnesberg","Angered","Askim",u"Asper\xf6","Billdal","Bohus",u"Br\xe4nn\xf6",u"Dons\xf6","Gunnilse",u"G\xf6teborg","Hisings backa",u"Hisings k\xe4rra",u"Hov\xe5s",u"Kung\xe4lv",u"K\xf6pstads\xf6",u"M\xf6lndal",u"N\xf6dinge","Olofstorp",u"Styrs\xf6",u"S\xe4ve","Torslanda",u"Vr\xe5ng\xf6",u"V\xe4stra fr\xf6lunda",u"\xd6cker\xf6"] 
#expected = ["Agnesberg","Angered","Askim","Asperö","Billdal","Bohus","Brännö","Donsö","Gunnilse","Göteborg","Hisings backa","Hisings kärra","Hovås","Kungälv","Köpstadsö","Mölndal","Nödinge","Olofstorp","Styrsö","Säve","Torslanda","Vrångö","Västra frölunda","Öckerö"] 
# "Partille","Stenkullen",u"K\xe5llered","H\xe4rryda","Landvetter",u"H\xf6n\xf6","Lerum",u"M\xf6lnlycke",
expected = ["Agnesberg"] 

#Bad  = Öckerö, Landvetter, Mölnlycke, mölnlycke, Stenkullen, Härryda, Kållered, Lerum, lerum
#       Partille, Partile, Lindome, Hönö, Jonsered, Sävedalen, Öjersjö, öjersjö

#Good = Hisings kärra, Hovås, Hisings Backa, Västra Frölunda, Vâstra Frölunda, Gothenburg

# UPDATE THIS VARIABLE

mapping_city = { "Gothenburg": "Göteborg",                                           #Erased 'SE-'
            u"Hisings K\xe4rra": u"Hisings k\xe4rra",                                                                  #the postal code for Hovås should in any case be changed somehow
            "436 58":u"Hov\xe5s",                                                       #the actual postal code
            u"V\xe4stra Fr\xf6lunda":u"V\xe4stra frölunda",
            u"V\xe2stra Fr\xf6lunda":u"V\xe4stra fr\xf6lunda",
            u"Hisings K\xe4rra":u"Hisings k\xe4rra"
            }

mapping_post_code = { "SE-42671": "42671",                                      #Erased 'SE-42671'
            u"Hov\xe5s": "43650",                                               #Hovås is changed to its postal code
            "12":"41274",                                                       #the actual postal code
            "417631":"41763"                                                    #deleted the '1' at the end
            }

def audit_type(types, name):
    m = street_type_re.search(name)
    if m:
        audit = m.group()
        if audit not in expected:
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


def update_city_name(name, mapping):
    array = []
    if name in mapping.keys():
        name = mapping[name]
    array.append(name)
    return "".join(array)

    return name


"""
def test(audit,update):
    st_types = audit(OSMFILE)
    #pprint.pprint(dict(st_types))

    for st_type, ways in st_types.iteritems():
        for name in ways:
            better_name = update(name, mapping_city)
            print name, "=>", better_name
            

test(audit_city,update_city_name)   
"""       
            

#================================================================
 #Audit postcode
#================================================================

def audit_post_code(osmfile):
    osm_file = open(osmfile, "r")
    postcode_types = defaultdict(set)
    #========= Detta kan nog tas bort i samband med 'audit_type' funktionen på rad 49 och 'expected' listen ======
    for event, elem in ET.iterparse(osm_file, events=("start",)):

        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_post_code(tag):
                    audit_type(postcode_types, tag.attrib['v'])
    #=========  hit kan det tas bort, Gör dessa för house number ===============
    osm_file.close()
    return postcode_types


def is_post_code(elem):
    return (elem.attrib['k'] == "addr:postcode")


def update_post_code(name, mapping):
    array = []                                                                 
    words = name.replace(" ", "")                                               #split postcode based on empty space ' '
    if words.isdigit() == False or len(words) != 5:                             #check if the postcode is not digits and/or had the standard length of 5 numbers
        if words in mapping.keys():                                             #check with the key:value pairs in the 'mapping' object above matches
            words = mapping[words]                                              #if the key matches, replace it with the new value
        array.append(words)                                                     #then append it to array
    return "".join(array)                                                       #saw up the gaps
    return name 

"""
def test(audit,update):                                                         #this test gives the output presenting the changes made
    st_types = audit(OSMFILE)
    #pprint.pprint(dict(st_types))

    for st_type, ways in st_types.iteritems():
        for name in ways:
            words = name.replace(" ", "")
            if words.isdigit() == False or len(words) != 5:
                better_name = update(words, mapping_post_code)
                print words, "=>", better_name
test(audit_post_code,update_post_code)
"""
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

def update_house_number(name):                                                  #Changes
    array = []                                                  
    words = list(name)                                                          #make a list out of the house numbers
    for word in words:                                          
        if isinstance(word, str) and word.islower():                            #check if listitem is a string and if the string is lowercaps
            word = word.title()                                                 #if it is, turn it into uppercaps
        array.append(word)                                                      #append the updated date into the array
    return "".join(array)                                                       #saw up the gaps
    return name
    

"""
def test(audit,update):                                                         #this test gives the output presenting the changes made
    st_types = audit(OSMFILE)
    #pprint.pprint(dict(st_types))
    for st_type, ways in st_types.iteritems():
        for name in ways:
            words = list(name)                                                  #Make all housenumbers into a list

                                                                                #Check for housenumbers with only letters
        #    if all(i.isdigit() == False for i in words):                       #Check if all list items are letters
        #        print name                                                     #In case all list items are letters, print the housenumbers
        
                                                                                #Check the changes to housenumber
        for name in words:                                                      #Itterate through list items
            if isinstance(name, str) and name.islower():                        #check if listitem is a string and if the string is lowercaps
                better_name = update(words)                                     #In that case present the changes made in 'update_house_number'
                print "".join(words), "=>", better_name                         #Print the data side by side with the updated information
        
test(audit_house_number,update_house_number)
"""
#================================================================
 #Test
#================================================================

"""
def test(audit,update):                                                         #this test gives the output presenting the changes made
    st_types = audit(OSMFILE)
    pprint.pprint(dict(st_types))

    for st_type, ways in st_types.iteritems():
        for name in ways:
            better_name = update(name, mapping)
            print name, "=>", better_name
test(audit_house_number,update_house_number)
"""   
   
#word = 'Hello Wor(ld'
#print re.findall(r"[\w']+",name)

