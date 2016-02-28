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
                   "Askim",         u"\xd6cker\xf6", "Olofstorp"] 
#expected = ["Agnesberg","Angered","Askim","Asperö","Billdal","Bohus","Brännö","Donsö","Gunnilse","Göteborg","Hisings backa","Hisings kärra","Hovås","Kungälv","Köpstadsö","Mölndal","Nödinge","Olofstorp","Styrsö","Säve","Torslanda","Vrångö","Västra frölunda","Öckerö"] 


expected = ["Terrace", "Plaza",    "Locust",    "Bypass", "Mall",    "Mall", 
            "Street",  "Avenue",   "Boulevard", "Drive",  "Court",   "Place",
            "Square",  "Lane",     "Road",      "Trail",  "Parkway", "Commons",
            "Way",     "Broadway", "Circle",    "South",  "East",    "North",
            "Point",   "Row",      "West" ] # List of the street types we expect to see in the US

highways = ['2', '8', '40', '73', '74', '83', '85', '86', '119', '285', '287'] # Includes 'highway' and 'state highway' and 'us highway'

county_roads = ['7', '41', '45', '72', '126', '186', '314'] # Includes county roads

exceptions = ['19',        '#107',   '#169',     '#220',   '400',
              '1606',      '6001',   '6523',     '8765',   'A',
              'Highway',   'MUP',    'Boulder',  'Canyon', 'Centennial',
              'Center',    'Lamar',  'Lincoln',  'Mine',   'Newland',
              'Ramp',      'Run',    'Tennyson', 'Tilden', 'Ute',
              'Wadsworth', 'Walnut', 'Woodfern', 'G' ] # Exceptions that need manual checking

suites = ['1E',  '5B',   '106',  '110',  '120', 
          '154', '200',  '200b', '200c', '230',
          '300', '#300', '400',  '700',  '#850',
          '900', '2200', 'D',    'E1',    ] # Includes both 'Suite', 'Ste', and 'Unit'. Let them be.

addr_mapping = {"88th"         : "88th Street",                                 #Changes to street endings
                "80208"        : "High Street",
                "80305"        : "South Lashley Lane",
                "Appia"        : "Via Appia Way",
                "Av"           : "Avenue",
                "Ave"          : "Avenue",
                "Ave."         : "Avenue",
                "Avenue)"      : "East Bromley Lane",
    			"ave."         : "Avenue",
    			"Arapahoe"     : "Arapahoe Avenue",
    			"Baselin"      : "Baseline Road",
                "Baseline"     : "Baseline Road",
    			"Blvd"         : "Boulevard",
                "Caria"        : "Caria Court",
                "Cherryvale"   : "Cherryvale Road",
    			"Cir"          : "Circle",
                "circle"       : "Circle",
    			"Colorado"     : 'West Alameda Parkway',
                "Colfax"       : "East Colfax Avenue",
                "Ct"           : "Court",
                "ct"           : "Court",
                "Dr"           : "Drive",
                "dr"           : "Drive",
                "Elm"          : "East Elm Street",
                "Etna"         : "Etna Court",
                "Grant"        : "Grant Place",
                "lane"         : "Lane",
                "Leetsdale"    : "Leetsdale Drive",
                "Ln"           : "Lane",
                "Main"         : "Main Street",
                "Mainstreet"   : "Main Street",
                "Osage"        : "Osage Drive",
                "Pennsylvania" : "Pennsylvania Avenue",
                "Pky"          : "Parkway",
                "Pkwy"         : "Parkway",
                "Pl"           : "Place",
                "Rd"           : "Road",
                "Rd."          : "Road",
                "rd"           : "Road",
                "Roadaddr"     : "Arapahoe Avenue",
                "S"            : "",
                "St"           : "Street",
                "St."          : "Street",
                "STreet"       : "Street",
                "Streer"       : "Street",
                "Strret"       : "Street",
                "st"           : "Street",
                "trail"        : "Trail",
                "Valmont"      : "Valmont Road",
                "Varra"        : "Varra Road"
                } # Map incorrect street types to desired

mapping_city = { "Gothenburg"            : "Göteborg",                           #All cities within Gothenburg municipality are corrected according to their correct names
                 "436 58"                : u"Hov\xe5s",                          #The postal code for Hovås is changed to it's full name
                 u"Hisings K\xe4rra"     : u"Hisings k\xe4rra",                  #As UTF-8 don't convert åäö in lists on python 2.7, i have used the decoded names for å,ä and ö as can be found in the åäö_test.py file
                 u"V\xe4stra Fr\xf6lunda": u"V\xe4stra frölunda",
                 u"V\xe2stra Fr\xf6lunda": u"V\xe4stra fr\xf6lunda",
                 u"Hisings K\xe4rra"     : u"Hisings k\xe4rra"
            }# Map incorrect city names to desired
            


mapping_post_code = { "SE-42671": "42671",                                      
                     u"Hov\xe5s": "43650",                                               #Hovås is changed to it's correct postal code
                     "12"       : "41274",                                                       #The actual postal code
                     "417631"   : "41763"                                                    #Deleted the incorrect '1' at the end of postcode
                     }
## Update Functions #################################################

def update_postcode(name):                                                      # Define streety type and correct if necessary
    if name.isdigit() == False or len(name) != 5:                               #Check if the postcode is not digits and/or does not have the standard length of 5 numbers
        if name in mapping_post_code.keys():                                             #Check with the key:value pairs in the 'mapping_post_code' object on line 27
            name = mapping_post_code[name]                                              #If the key matches, replace it with the new value
            return name                                                         #then append it to array                                                      #Saw together the spaces
    return name 

def update_house_number(this_house_number):                                       #---
    result = []
    new_string = this_house_number.upper()
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
    
def update_city(this_city):                                                     #---Värdet från update_city stoppas in på rad 206
    # Change city string to lower and correct if necessary
    if this_city not in expected_cities:
        if this_city in mapping_city.keys():
            this_city = mapping_city[this_city]
            return this_city
    return this_city
## Element Shaping and Writing to JSON #################################################

def shape_element(element):
    # Shaping the element to be pushed to JSON
    # Declare dict for new reshaped element
    node = {}                                                                   #+++Foundation code
    # Declare dict for metadata of this node
    created = {}                                                                #---Added code
    # Define the metadata fields we want to pull from this element
    created_fields = ['changeset', 'version', 'timestamp', 'user', 'uid']       #---Metadatan i 'created' från 'foundation' koden 
    # Define other high level items of interest (example = 'id', 'type', 'pos')
    high_level_items = ['id', 'visible', 'type']                                #---Också Metadatan i 'created' från 'foundation' koden
    # Define other elements of interest                                         #---Nedan: Också Metadatan i 'created' från 'foundation' koden, plus tydligen andra intressanta element
    elems_of_int = ['amenity', 'cuisine', 'name', 'phone', 'historic', 'peak', 'natural']
    # If this element is node or way, do stuff below
    if element.tag == "node" or element.tag == "way" :                          #+++
        value = set()                                                           #value:n som du satt in
        # First field we add to node is the type of node
        node['type'] = element.tag                                              #/// Används på flera platser
        # Store the element keys (for instance 'uid', 'changeset', 'timestamp', etc.)
        keys = element.attrib.keys()                                            #///
        # Second we add the created metadata of interest, high_level_keys, position and their values
        for item in keys:                                                       #--- Behåll detta kodblock!: Itterera genom keys:en och spara sedan i created.
            if item in created_fields:                                          #--- Detta är för att bygga upp objectet på rad 17 - 23 på udacity coden
                created[item] = element.attrib[item]                            #--- Denna koden skapar allt från 14-23
            if item in high_level_items:                                        #---
                node[item] = element.attrib[item]                               #---
            if 'lat' in keys:                                                   #///
                node['pos'] = [float(element.attrib['lat']), float(element.attrib['lon'])]   #/// detta skapar latitud och longitud på rad 24
        # Store created fields and values as element within the node
        node['created'] = created                                               #---Spara hela created i node, node representerar allt från rad 13 - 34 på udacity koden
        # If node contains address data, add address field
        for child in element:                                                   #---för varje <element>29.99</element>
        	if child.tag == 'tag':                                               #---om dess tag har element-namn "tag" som <tag k="addr:city" v="Chicago"/>
        		if child.attrib['k'].startswith('addr:'):                      #---sen om dess attribut är k och börjar med 'addr:' som i <tag k="addr:city" v="Chicago"/>
        			node['address'] = {}                                      #--- skapa då en 'address' key med value {} som i 'address' : {} som han vill i 25-29
        # Populate address key (if present) and all other attributes of interest
        for child in element:                                                   #--- Gör samma som ovan
            if child.tag == 'tag':                                              #--- Gör samma som ovan
                if child.attrib['k'].startswith('addr:') == 1 and child.attrib['k'].count(':') < 2:      # om det bara finns en addr: och inte finns två beteckningar som ex: <tag k="addr:street:name" v="Lexington"/>
                    field = child.attrib['k'][5:]                               #---Sätt få field till lika med alla bokstäver efter 5, dvs alla bokstäver efter addr: altså "housenumber" <tag k="addr:housenumber" v="1412"/>
                    if field == 'housenumber':                                   #---Om nu field är 'street'
                        value = update_postcode(child.attrib['v'])              #Ersätt med housenumber #---sätt value till dess attrib 'v' i detta fallet "West Lexington St." <tag k="addr:street" v="West Lexington St."/>
                    elif field == 'city':                                       #---Om fieldet är 'City'
                        value = update_city(child.attrib['v'])                  #---spara då dess v-värde i value <tag k="addr:city" v="Baldwin Rd."/>
                    elif field == 'postcode':                                   #---Gör desamma med postnummer
                        for house_number in update_house_number(child.attrib['v']):   #---Detta värde 'v' stoppas in i rad 143
                            value.add(house_number) 
                    else:                                                       #---
                        value = child.attrib['v']                               #--- annars sätt value til det v-värde som uppstår
                    node['address'].update({field : value})                     #--- i ditt address node object rad 25-29 på udacity, skapa ditt key:value par som ex *"housenumber": "5157"* hämtat från udacity på rad 26
                if child.attrib['k'] in elems_of_int:                           #---Skapa de sista 4 rubrikerna från Udacity objectet, rad 30-33: Om k-värdet finns i list:en elems_of_int, som i detta fallet 'name' <tag k="name" v="Matty Ks"/>
                    node[child.attrib['k']] = child.attrib['v']                 #---skapa då ett key:value par name:Matty Ks
        # Process the way nds
        if element.tag == "way":                                                #---för all way taggar </way>
            nds = []                                                            #---skapa ny list
            for child in element:                                               #---för varje child i denna ways <way> element. Ex. 70-86
                if child.tag == 'nd':                                           #---om elementets child är 'nd' som i <nd ref="2199822281"/>
                    nds.append(child.attrib['ref'])                             #---Appenda då dess 'ref' referensnummer värde <nd ref="2199822281"/>
            node['node_refs'] = nds                                             #---stoppa sedan in detta i node_refs
        return node                                                             #+++returna node
    else:                                                                       #+++
        return None                                                             #+++

def process_map(file_in, pretty = False):                                       #+++
    # Process to JSON. Used start, end objects to improve performance
    # Depending upon file size... this may take a few minutes
    file_out = "{0}.json".format(file_in)                                       #+++
    data = []                                                                   #+++
    with codecs.open(file_out, "w") as fo:                                      #+++
        context = ET.iterparse(file_in,events=('start','end'))                  #---parsa genom varje rad för sig
        context = iter(context)                                                 #---itterera genom context
        event, root = context.next()                                            #---
        for event, element in context:                                          #---
            if event == 'end':                                                  #---
                el = shape_element(element)                                     #+++
                if el:                                                          #+++
                    data.append(el)                                             #+++
                    if pretty:                                                  #+++
                        fo.write(json.dumps(el, indent=2)+"\n")                 #+++
                    else:                                                       #+++
                        fo.write(json.dumps(el) + "\n")                         #+++
            root.clear()                                                        #---
    return data                                                                 #+++

## Mongo Import Instructions (after JSON created) ###################################

# Start a mongod instance using ./mongod
# Open new terminal window and cd to mongo bin folder
# Move records from json to mongo with this command using mongo import
# ./mongoimport --db osm --collection osmb_807 --type json --file /Users/frankCorrigan/Udacity/OpenStreetMap-Analysis/OSM_Data_Project/denver-boulder_colorado.osm.json