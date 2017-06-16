#!/usr/bin/python

import os, sys
import settings
import argparse

from addressToGHgeojsonObject import Address_to_gist_map

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
# gmaps = googlemaps.Client(key=google_maps_key)

if args.input_file:
    addresses = args.input_file.readlines()
if args.addresses:
    addresses = args.addresses

gh_gm = Address_to_gist_map(github_token, google_maps_key, addresses, True)
gh_gm.initalize()
gh_gm.gist_map_from_addresses()
# coordinate_set = map(from_string_to_coordinates_and_poi, addresses)
# if debug:
    # print coordinate_set
# fc = fromCoordinatesToFeatureCollection(coordinate_set)
# if debug:
    # print fc


# gist = createGistDictFromGeojson("output.json", "patata", fc)
# if debug:
    # print gist

# response, gist_url = publishToGists(gist)
# print gist_url
# if debug:
    # print response
