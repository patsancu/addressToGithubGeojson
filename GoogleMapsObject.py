import os, sys
import os, googlemaps, settings
import geojson
import requests

import settings

api_key_settings = settings.GOOGLE_MAPS_API_KEY
api_key_env = os.getenv("GOOGLE_MAPS_API_KEY")
if  not(api_key_settings and len(api_key_settings)) and not api_key_env :
    print "No maps_key, add an env key with GOOGLE_MAPS_API_KEY"
    print "or put one in the settings.py file"
else:
    api_key = api_key_env if api_key_env else api_key_settings
    print "Key is: " + api_key

address_string = "avenida pablo iglesias, 19, madrid"
gmaps = googlemaps.Client(key=api_key)
addresses = gmaps.geocode(address_string)


if len(addresses) == 0:
    print "address {} has not returned any results".format(address_string)
elif len(addresses) > 1:
    print "address {} is ambigous".format(address_string)
else:
    maps_dict = addresses[0]
    location = maps_dict['geometry']['location'] 
    lat, lng = location['lat'], location['lng']
    print "address {} has coordinates: {},{}".format(address_string, lat, lng)

import geojson
my_point = geojson.Point((lng, lat))
my_feature = geojson.Feature(geometry=my_point, properties={"address": address_string})
fc = geojson.FeatureCollection([my_feature])
dump = geojson.dumps(fc, sort_keys=True)
f = open("patata.geojson", "w")
f.write(dump)
f.close()

debug = True
if debug:
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


    print dictData
    response = requests.post("https://api.github.com/gists", json=dictData)
    if not response.ok:
        print "something strange happened"
    print "{}".format(response.text)
