#!/usr/bin/python

import os, sys

import json
import googlemaps, geojson
import requests

import settings
import argparse

parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('--addresses', metavar='addresses', nargs='+',
        help='an address to parse and show')
parser.add_argument('--input_file', dest='input_file', action='store',
        type=file, help='pass a file from which to read')
parser.add_argument('--output-file', dest='output_file', action='store',
                    help='pass a file to write to')

args = parser.parse_args()
# print args

debug = False


################
# Functions
################
def write_to_file(filename, contents):
    f = open("patata.geojson", "w")
    f.write(contents)
    f.close()

def from_string_to_coordinates_and_poi(address_string):
    address_tokens = address_string.split(';')
    poi_type = None
    if len(address_tokens) > 1:
        poi_type = address_tokens[1].strip()
        if debug:
            print "Address is: {}".format(address_tokens[0])
            print "POI type is: {}".format(address_tokens[1])
    addresses = gmaps.geocode(address_string)
    if len(addresses) == 0:
        print "address {} has not returned any results".format(address_string)
        return False

    if len(addresses) > 1:
        print "address {} is ambiguous".format(address_string)
    maps_dict = addresses[0]
    location = maps_dict['geometry']['location']
    lat, lng = location['lat'], location['lng']
    if debug:
        print "address {} has coordinates: {},{}".format(address_string, lat, lng)
    return lng, lat, poi_type

def get_icon_name_for_poi_type(poi_type):
    if poi_type == "bar":
        return "bar"
    print "Poi_type is not a bar, it's a: {}".format(poi_type)
    return 'triangle'

def fromCoordinatesToFeatureCollection(coordinatesSet, address_string = None):
    feature_collection = []
    for coordinate in coordinatesSet:
        lat = coordinate[0]
        lng = coordinate[1]
        poi_type = coordinate[2]
        if debug:
            print "poi_type is: {}".format(poi_type)
        properties = {}
        if poi_type:
            properties['marker-symbol'] = get_icon_name_for_poi_type(poi_type)
        my_point = geojson.Point((lat, lng))
        my_feature = geojson.Feature(geometry = my_point, properties=properties)
        feature_collection.append(my_feature)

    fc = geojson.FeatureCollection(feature_collection)
    return fc

def fromGeoJSONtoString(inputGeoJSON):
    dump = geojson.dumps(inputGeoJSON, sort_keys=True)
    return dump

### Writes string to file
def writeContentsToFile(contents, file_name):
    if write_to_file_flag:
        write_to_file(filename, dump)

def createGistDictFromGeojson(filename, description, geoJSON):
    content = fromGeoJSONtoString(geoJSON)
    public = True
    gist_data = {}
    gist_data['description'] = description
    gist_data['files'] = {}
    gist_data['files'][filename] = {}
    gist_data['files'][filename]['content'] = content
    gist_data['public'] = public
    return gist_data

# Tries to publish gist and returns response status and gist url (if successful) or blank
def publishToGists(gist_object):
    if github_token:
        headers =  {'Authorization': 'token {}'.format(github_token) }
        response = requests.post("https://api.github.com/gists", json=gist_object, headers=headers)
    else:
        response = requests.post("https://api.github.com/gists", json=gist_object)
    if not response.ok:
        print "something strange happened"
    obj = json.loads(response.text)
    if debug:
        print "{}".format(response.text)
    return (response.ok, obj['html_url'])

################
# Parse input
################

# Parse address
if len(sys.argv) == 1:
    print "usage: {} \"address\"".format(sys.argv[0])
    sys.exit(2)
if len(sys.argv) > 1:
    address_string = sys.argv[1]

################
# Parse settings
################

try:
    google_maps_key_settings = settings.GOOGLE_MAPS_API_KEY
except AttributeError:
    google_maps_key_settings = ""
    if debug:
        print "No key in settings file"

google_maps_key_env = os.getenv("GOOGLE_MAPS_API_KEY")
if  not len(google_maps_key_settings) and not google_maps_key_env :
    print "No maps_key, add an env key with GOOGLE_MAPS_API_KEY"
    print "or put one in the settings.py file"
    sys.exit(1)
else:
    google_maps_key = google_maps_key_env if google_maps_key_env else google_maps_key_settings


try:
    github_token_settings = settings.GITHUB_GIST_TOKEN
except AttributeError:
    github_token_settings = ""
    if debug:
        print "No github token in settings file"

github_token_env = os.getenv("GITHUB_GIST_TOKEN")
if  len(github_token_settings) and not github_token_env :
    print "No github token, add an env key with GITHUB_GIST_TOKEN"
    print "or put one in the settings.py file"
    print "The gist will be anonymouse"
else:
    github_token = github_token_env if github_token_env else github_token_settings


################
# Initialization
################
write_to_file_flag = False
gmaps = googlemaps.Client(key=google_maps_key)

if args.input_file:
    addresses = args.input_file.readlines()
if args.addresses:
    addresses = args.addresses

coordinate_set = map(from_string_to_coordinates_and_poi, addresses)
if debug:
    print coordinate_set
fc = fromCoordinatesToFeatureCollection(coordinate_set)
if debug:
    print fc


gist = createGistDictFromGeojson("output.json", "patata", fc)
if debug:
    print gist

response, gist_url = publishToGists(gist)
print gist_url
if debug:
    print response
