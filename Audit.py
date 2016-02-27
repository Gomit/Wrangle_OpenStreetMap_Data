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


expected_cities = ["Agnesberg","Angered","Askim",u"Asper\xf6","Billdal","Bohus",u"Br\xe4nn\xf6",u"Dons\xf6","Gunnilse",u"G\xf6teborg","Hisings backa",u"Hisings k\xe4rra",u"Hov\xe5s",u"Kung\xe4lv",u"K\xf6pstads\xf6",u"M\xf6lndal",u"N\xf6dinge","Olofstorp",u"Styrs\xf6",u"S\xe4ve","Torslanda",u"Vr\xe5ng\xf6",u"V\xe4stra fr\xf6lunda",u"\xd6cker\xf6"] 
#expected = ["Agnesberg","Angered","Askim","Asperö","Billdal","Bohus","Brännö","Donsö","Gunnilse","Göteborg","Hisings backa","Hisings kärra","Hovås","Kungälv","Köpstadsö","Mölndal","Nödinge","Olofstorp","Styrsö","Säve","Torslanda","Vrångö","Västra frölunda","Öckerö"] 

mapping_city = { "Gothenburg": "Göteborg",                                      #All cities within Gothenburg municipality are corrected according to their correct names
            u"Hisings K\xe4rra": u"Hisings k\xe4rra",                           #As UTF-8 don't convert åäö in lists on python 2.7, i have used the decoded names for å,ä and ö as can be found in the Swedish_letters_åäö_Test.py file
            "436 58":u"Hov\xe5s",                                               #The postal code for Hovås is changed to it's full name
            u"V\xe4stra Fr\xf6lunda":u"V\xe4stra frölunda",
            u"V\xe2stra Fr\xf6lunda":u"V\xe4stra fr\xf6lunda",
            u"Hisings K\xe4rra":u"Hisings k\xe4rra"
            }

mapping_post_code = { "SE-42671": "42671",                                      
            u"Hov\xe5s": "43650",                                               #Hovås is changed to it's correct postal code
            "12":"41274",                                                       #The actual postal code
            "417631":"41763"                                                    #Deleted the incorrect '1' at the end of postcode
            }

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


def update_city_name(name, mapping):
    array = []
    if name in mapping.keys():
        name = mapping[name]
    array.append(name)
    return "".join(array)

    return name


"""
def test(audit,update):                                                         ##Test-check
    st_types = audit(OSMFILE)                                                   #Description below
    #pprint.pprint(dict(st_types))

    for st_type, ways in st_types.iteritems():
        for name in ways:
            better_name = update(name, mapping_city)
            print name, "=>", better_name
            

test(audit_city,update_city_name)   
"""    
#Bad Cities  = Öckerö, Landvetter, Mölnlycke, mölnlycke, Stenkullen, Härryda, Kållered, Lerum, lerum
#       Partille, Partile, Lindome, Hönö, Jonsered, Sävedalen, Öjersjö, öjersjö

#Good Cities = Hisings kärra, Hovås, Hisings Backa, Västra Frölunda, Vâstra Frölunda, Gothenburg 

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


def update_post_code(name, mapping):
    array = []                                                                 
    words = name.replace(" ", "")                                               #Split postcode based on empty space ' '
    if words.isdigit() == False or len(words) != 5:                             #Check if the postcode is not digits and/or does not have the standard length of 5 numbers
        if words in mapping.keys():                                             #Check with the key:value pairs in the 'mapping_post_code' object on line 27
            words = mapping[words]                                              #If the key matches, replace it with the new value
        array.append(words)                                                     #then append it to array
    return "".join(array)                                                       #Saw together the spaces
    return name 


"""                                                                             ##Test-check
def test(audit,update):                                                         #This test gives the output presenting the changes made
    st_types = audit(OSMFILE)
    #pprint.pprint(dict(st_types))

    for st_type, ways in st_types.iteritems():
        for name in ways:
            words = name.replace(" ", "")
            if words.isdigit() == False or len(words) != 5:
                better_name = update(words, mapping_post_code)
                print words, "=>", better_name
                
            #if words < '40010' or words > '47500':                             #Check if postalcodes are within Gothenburg county
            #    print words                                                    #Else postcodes belongs to the cities in the 'bad cities' listed on line 89
                
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

def update_house_number(name):                                                  ##Make changes
    array = []                                                  
    words = list(name)                                                          #Make a list out of the house numbers
    for word in words:                                          
        if isinstance(word, str) and word.islower():                            #Check if list item is a string and if the string is lowercaps
            word = word.upper()                                                 #If True, turn it into uppercaps
        array.append(word)                                                      #Append the updated date into the array
    return "".join(array)                                                       #Saw together the spaces
    return name
    

                                                                             ##Test-check
def test(audit,update):                                                         #This test gives the output presenting the changes made
    st_types = audit(OSMFILE)
    #pprint.pprint(dict(st_types))
    for st_type, ways in st_types.iteritems():
        for name in ways:
            words = list(name)                                                  #Make all housenumbers into a list
            better_name = update(words)                 #ta bort                    
            print "".join(words), "=>", better_name     #Ta bort

                                                                                ##Check for housenumbers with only letters
        #    if all(i.isdigit() == False for i in words):                       #Check if all list items are letters
        #        print name                                                     #In case all list items are letters, print the housenumbers
        
        """ #avmarkera                                                                        ##Check the changes to housenumber
        for name in words:                                                      #Itterate through list items
            if isinstance(name, str) and name.islower():                        #Check if listitem is a string and if the string is lowercaps
                better_name = update(words)                                     #In that case present the changes made in 'update_house_number'
                print "".join(words), "=>", better_name                         #Print the data side by side with the updated information
        """ #avmarkera
test(audit_house_number,update_house_number)




