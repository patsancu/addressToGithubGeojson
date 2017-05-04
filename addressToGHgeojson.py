#!/usr/bin/python

import os, sys

import json
import googlemaps, geojson
import requests

import settings

debug = False


################
# Functions
################
def write_to_file(filename, contents):
    f = open("patata.geojson", "w")
    f.write(contents)
    f.close()

def fromStringToCoordinates(address_string):
    addresses = gmaps.geocode(address_string)
    if len(addresses) == 0:
        print "address {} has not returned any results".format(address_string)
        return False

    if len(addresses) > 1:
        print "address {} is ambigous".format(address_string)
    maps_dict = addresses[0]
    location = maps_dict['geometry']['location']
    lat, lng = location['lat'], location['lng']
    if debug:
        print "address {} has coordinates: {},{}".format(address_string, lat, lng)
    return lng, lat


def fromCoordinatesToFeatureCollection(coordinates, address_string = None):
    lat = coordinates[0]
    lng = coordinates[1]
    my_point = geojson.Point((lat, lng))
    properties= {}
    if address_string:
        properties["address"] = address_string
    my_feature = geojson.Feature(geometry=my_point, properties=properties)
    fc = geojson.FeatureCollection([my_feature])
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
    print obj['html_url']
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



coordinates = fromStringToCoordinates(address_string)
print coordinates

fc = fromCoordinatesToFeatureCollection(coordinates)
print fc

gist = createGistDictFromGeojson("prueba.json", "patata", fc)
print gist

response = publishToGists(gist)
print response
