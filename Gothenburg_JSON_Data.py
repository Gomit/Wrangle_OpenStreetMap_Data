# -*- coding: utf-8 -*-
"""
Created on Thu Feb 25 18:01:51 2016

@author: merongoitom
"""

import xml.etree.cElementTree as ET 
import re
import codecs
import json

'''
This file takes an osm files, parses it, and
writes each element into a JSON file. Using the audit.py 
file, potential errors that need correction to fit data 
model have been identified. The flow of functions ...
process_map uses --> shape_element uses --> everything else
These pieces of code can be used for element searching and Shaping
sample = "<node changeset="830792" id="335986968" lat="39.3419172" lon="-104.746838" timestamp="2009-01-24T17:35:23Z" uid="91266" user="HurricaneCoast" version="2">
    <tag k="addr:city" v="Franktown" />
    <tag k="created_by" v="Potlatch 0.10f" />
    <tag k="addr:street" v="Street G" />
    <tag k="addr:postcode" v="80116" />
</node>"
sample = ET.fromstring(sample)
for _, element in ET.iterparse(boulder_osm):
    for child in element:
        if child.tag == 'tag':
            if child.attrib['k'] == 'addr:street':
                if child.attrib['v'].rsplit(None, 1)[-1] == '106':
                #if child.attrib['v'].startswith('County Rd'):
                    for child in element:
                        print child.attrib
'''

small_boulder = 'boulder_sample.osm'
big_boulder = 'denver-boulder_colorado.osm'

## Helper lists & dictionaries #################################################

expected_cities = ["Agnesberg",     "Angered",       "Askim",        u"Asper\xf6",      u"K\xf6pstads\xf6",
                   "Bohus",         u"Dons\xf6",     "Gunnilse",     u"G\xf6teborg",    u"Hisings k\xe4rra",
                   "Hisings backa", u"Hov\xe5s",     u"Kung\xe4lv",  u"Br\xe4nn\xf6",   u"V\xe4stra fr\xf6lunda",
                   "Billdal",       u"M\xf6lndal",   u"N\xf6dinge",  u"K\xf6pstads\xf6",
                   u"Styrs\xf6",    u"S\xe4ve",      "Torslanda",    u"Vr\xe5ng\xf6",
                   "Askim",         u"\xd6cker\xf6", "Olofstorp"] # List of the cities we expect in Gothenburg municipality
#Cities in correct spelling
#expected_cities = ["Agnesberg","Angered","Askim","Asperö","Billdal","Bohus","Brännö","Donsö","Gunnilse","Göteborg","Hisings backa","Hisings kärra","Hovås","Kungälv","Köpstadsö","Mölndal","Nödinge","Olofstorp","Styrsö","Säve","Torslanda","Vrångö","Västra frölunda","Öckerö"] 


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
                     }# Map incorrect postcodes to desired

## Update Functions #################################################

#Check for bad postcodes and correct if necessary
def update_postcode(name):
    #Erase spaces and correct with mapping_post_code if necessary
    code = name.replace(" ", "")
    if code.isdigit() == False or len(code) != 5:                               
        if code in mapping_post_code.keys():                                            
            code = mapping_post_code[code]                                      
            return code                                                         
    return code 

#Check for abbreviations and correct if necessary
def update_house_number(this_house_number):                                       
    result = []
    new_string = this_house_number.upper()
    #Split based on ';' and '-' and append full sequence provided all are digits
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

#Check for misspellings and cities not associated to Gothenburg
def update_city(this_city):                                                     
    #Check if city among expected_cities, else correct if necessary
    if this_city not in expected_cities:
        if this_city in mapping_city.keys():
            this_city = mapping_city[this_city]
            return this_city
    return this_city

## Element Shaping and Writing to JSON #################################################

def shape_element(element):
    # Create the dict to be pushed to JSON
    node = {}                                                                   
    # Create the dict for data to be pushed into the node
    created = {}                                                                
    # Define the metadata fields which will populate the dict
    created_fields = ['changeset', 'version', 'timestamp', 'user', 'uid']       
    # Define other high level items which will populate the dict
    high_level_items = ['id', 'visible', 'type']                                
    # Define other elements of interest                                         
    elems_of_int = ['amenity', 'cuisine', 'name', 'phone', 'historic', 'peak', 'natural']
    # If this element is node or way, start pupulating
    if element.tag == "node" or element.tag == "way" :  
        # Create the element which will populate postcodes                        
        value = set()                                                           
        # First field added to node is the tag type
        node['type'] = element.tag                                              
        # Store the element keys (for instance 'uid', 'changeset', 'timestamp', etc.)
        keys = element.attrib.keys()                                            
        # Second we add the created metadata of interest, high_level_keys, position and their values
        for item in keys:                                                       
            if item in created_fields:                                          
                created[item] = element.attrib[item]                            
            if item in high_level_items:                                        
                node[item] = element.attrib[item]                               
            if 'lat' in keys:                                                   
                node['pos'] = [float(element.attrib['lat']), float(element.attrib['lon'])]           
        # Store created fields and values as element within the node
        node['created'] = created                                               
        # If node contains address data, add address field
        for child in element:                                                   
        	if child.tag == 'tag':                                               
        		if child.attrib['k'].startswith('addr:'):                      
        			node['address'] = {}                                      
        # Populate address key (if present) and all other attributes of interest
        for child in element:                                                   
            if child.tag == 'tag':                                              
                if child.attrib['k'].startswith('addr:') == 1 and child.attrib['k'].count(':') < 2:  
                    field = child.attrib['k'][5:]                              
                    if field == 'street':                                
                        value = child.attrib['v']                   
                    elif field == 'housenumber':                                
                        value = update_postcode(child.attrib['v'])             
                    elif field == 'city':                                       
                        value = update_city(child.attrib['v'])                  
                    elif field == 'postcode':                                   
                        for house_number in update_house_number(child.attrib['v']):  
                            value.add(house_number) 
                    else:                                                       
                        value = child.attrib['v']                               
                    node['address'].update({field : value})                     
                if child.attrib['k'] in elems_of_int:                           
                    node[child.attrib['k']] = child.attrib['v']                 
        # Process the way nds
        if element.tag == "way":                                                
            nds = []                                                           
            for child in element:
                # parse second-level tags for ways and populate `node_refs`                                               
                if child.tag == 'nd':                                           
                    nds.append(child.attrib['ref'])                           
            node['node_refs'] = nds                                           
        return node                                                             
    else:                                                                       
        return None                                                             

def process_map(file_in, pretty = False):                                       
    # Process to JSON
    file_out = "{0}.json".format(file_in)                                       
    data = []                                                                   
    with codecs.open(file_out, "w") as fo:                                      
        context = ET.iterparse(file_in,events=('start','end'))                  
        context = iter(context)                                                 
        event, root = context.next()                                            
        for event, element in context:                                          
            if event == 'end':                                                  
                el = shape_element(element)                                     
                if el:                                                          
                    data.append(el)                                             
                    if pretty:                                                  
                        fo.write(json.dumps(el, indent=2)+"\n")                 
                    else:                                                       
                        fo.write(json.dumps(el) + "\n")                         
            root.clear()                                                        
    return data                                                                 

## Mongo Import Instructions (after JSON created) ###################################

# Start a mongod instance using ./mongod
# Open new terminal window and cd to mongo bin folder
# Move records from json to mongo with this command using mongo import
# ./mongoimport --db osm --collection osmb_807 --type json --file /Users/frankCorrigan/Udacity/OpenStreetMap-Analysis/OSM_Data_Project/denver-boulder_colorado.osm.json