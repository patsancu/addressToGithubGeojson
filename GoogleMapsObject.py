#!/usr/bin/python

import os, sys

import json
import googlemaps, geojson
import requests

import settings

debug = False
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

addresses = gmaps.geocode(address_string)

def write_to_file(filename, contents):
    f = open("patata.geojson", "w")
    f.write(contents)
    f.close()

if len(addresses) == 0:
    print "address {} has not returned any results".format(address_string)
elif len(addresses) > 1:
    print "address {} is ambigous".format(address_string)
else:
    maps_dict = addresses[0]
    location = maps_dict['geometry']['location']
    lat, lng = location['lat'], location['lng']
    if debug:
        print "address {} has coordinates: {},{}".format(address_string, lat, lng)
    my_point = geojson.Point((lng, lat))
    my_feature = geojson.Feature(geometry=my_point, properties={"address": address_string})
    fc = geojson.FeatureCollection([my_feature])
    dump = geojson.dumps(fc, sort_keys=True)
    if write_to_file_flag:
        write_to_file("patata.geojson", dump)


description = "rtfm"
filename = "patata.geojson"
content = dump
public = True
dictData = {}
dictData['description'] = description
dictData['files'] = {}
dictData['files'][filename] = {}
dictData['files'][filename]['content'] = content
dictData['public'] = public

if debug:
    print dictData
if github_token:
    headers =  {'Authorization': 'token {}'.format(github_token) }
    response = requests.post("https://api.github.com/gists", json=dictData, headers=headers)
else:
    response = requests.post("https://api.github.com/gists", json=dictData)

if not response.ok:
    print "something strange happened"

obj = json.loads(response.text)
print obj['html_url']
if debug:
    print "{}".format(response.text)
