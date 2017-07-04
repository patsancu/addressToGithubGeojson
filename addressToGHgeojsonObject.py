#!/usr/bin/python

import json
import googlemaps, geojson
import requests

class Address_to_gist_map():
    def __init__(self, github_token, google_maps_key, addresses, debug=False):
        self.github_token = github_token
        self.google_maps_key = google_maps_key
        self.addresses = addresses
        self.debug = debug

    def initalize(self):
        self.gmaps = googlemaps.Client(key=self.google_maps_key)

    def _write_to_file(self, filename, contents):
        f = open(filename, "w")
        f.write(contents)
        f.close()

    def _get_coordinate_set_from_strings(self):
        coordinate_set = map(self._from_string_to_coordinates_and_poi, self.addresses)
        if self.debug:
            print coordinate_set
        self._fromCoordinatesToFeatureCollection(coordinate_set)
        if self.debug:
            print self.fc

    def _from_string_to_coordinates_and_poi(self, address_string):
        address_tokens = address_string.split(';')
        poi_type = None
        if len(address_tokens) > 1:
            poi_type = address_tokens[1].strip()
            if self.debug:
                print "Address is: {}".format(address_tokens[0])
                print "POI type is: {}".format(address_tokens[1])
        addresses = self.gmaps.geocode(address_string)
        if len(addresses) == 0:
            print "address {} has not returned any results".format(address_string)
            return False

        if len(addresses) > 1:
            print "address {} is ambiguous".format(address_string)
        maps_dict = addresses[0]
        location = maps_dict['geometry']['location']
        lat, lng = location['lat'], location['lng']
        if self.debug:
            print "address {} has coordinates: {},{}".format(address_string, lat, lng)
        return lng, lat, poi_type

    def _get_icon_name_for_poi_type(self, poi_type):
        if poi_type == "bar":
            return "bar"
        print "Poi_type is not a bar, it's a: {}".format(poi_type)
        return 'triangle'

    def _fromCoordinatesToFeatureCollection(self, coordinatesSet, address_string = None):
        feature_collection = []
        for coordinate in coordinatesSet:
            lat = coordinate[0]
            lng = coordinate[1]
            poi_type = coordinate[2]
            if self.debug:
                print "poi_type is: {}".format(poi_type)
            properties = {}
            if poi_type:
                properties['marker-symbol'] = self._get_icon_name_for_poi_type(poi_type)
            my_point = geojson.Point((lat, lng))
            my_feature = geojson.Feature(geometry = my_point, properties=properties)
            feature_collection.append(my_feature)

        self.fc = geojson.FeatureCollection(feature_collection)

    def _create_string_from_geojson(self):
        dump = geojson.dumps(self.fc, sort_keys=True)
        return dump

    ### Writes string to file
    def _writeContentsToFile(self, contents, file_name):
        if write_to_file_flag:
            write_to_file(filename, dump)

    def _createGistDictFromGeojson(self, filename, description):
        content = self._create_string_from_geojson()
        public = True
        gist_data = {}
        gist_data['description'] = description
        gist_data['files'] = {}
        gist_data['files'][filename] = {}
        gist_data['files'][filename]['content'] = content
        gist_data['public'] = public
        self.gist_data = gist_data

    # Tries to publish gist and returns response status and gist url (if successful) or blank
    def _publishToGists(self):
        if self.github_token:
            headers =  {'Authorization': 'token {}'.format(self.github_token) }
            response = requests.post("https://api.github.com/gists", json=self.gist_data, headers=headers)
        else:
            response = requests.post("https://api.github.com/gists", json=self.gist_data)
        if not response.ok:
            print "something strange happened"
        obj = json.loads(response.text)
        if self.debug:
            print "{}".format(response.text)
        return (response.ok, obj['html_url'])

    def gist_map_from_addresses(self, filename="some_map.geojson", description="some description"):
        self._get_coordinate_set_from_strings()
        self._createGistDictFromGeojson(filename, description)
        response, gist_url = self._publishToGists()
        print gist_url

