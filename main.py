#!/usr/bin/python

import argparse
import sys

from addressToGHgeojsonObject import Address_to_gist_map
from parse_settings import parse_settings

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
google_maps_api_key, github_token = parse_settings()


################
# Initialization
################
write_to_file_flag = False
# gmaps = googlemaps.Client(key=google_maps_key)

if args.input_file:
    addresses = args.input_file.readlines()
if args.addresses:
    addresses = args.addresses
else:
    addresses = [address]

gh_gm = Address_to_gist_map(github_token, google_maps_api_key, addresses, False)
gh_gm.initalize()
gh_gm.gist_map_from_addresses()
