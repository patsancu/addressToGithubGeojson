#!/usr/bin/python

import settings
import os
import argparse

debug = False

def _parse_google_maps_api_key():
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
    return google_maps_key


def _parse_github_api_key():
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
    return github_token

def parse_settings():
    google_maps_api_key = _parse_google_maps_api_key()
    github_token = _parse_github_api_key()
    return google_maps_api_key, github_token

