#!/usr/bin/env python
""" $ who-is-in-http-app.py

A front-facing http app to show who is where: the "master" page.

:Author:    Ralph Bean
:License:   GPLv2+
"""

import argparse
import flask
import json
import yaml
import random
import urllib
import hashlib

app = flask.Flask(__name__)
email_file = default_email_file = "emails.yaml"
children_file = default_children_file = "children.yaml"
children = None
known_emails = None


def load_data():
    """ Ping all the slave nodes and return the aggregate data """
    results = {}
    for name, base_url in children.items():
        try:
            results[name] = json.loads(urllib.urlopen(base_url).read())
        except Exception as e:
            print " ** PROBLEM loading data for %r: %r" % (name, e)

    return results


def get_gravatar(username):
    email = known_emails.get(username, username + "@rit.edu")
    magic_sauce = hashlib.md5(email).hexdigest()
    base_url = "https://gravatar.com/avatar/"
    return base_url + magic_sauce + "?s=128"


def get_user_data(username):
    gravatar = get_gravatar(username)
    data = load_data()
    results = {}
    knowledge = {}
    for location, subdict in data.items():
        if username in subdict:
            results[location] = subdict[username]
            for device, status in subdict[username].items():
                if status:
                    knowledge[device] = knowledge.get(device, []) + [location]

    return {
        'gravatar': gravatar,
        'knowledge': knowledge,
        'details': results,
    }


def get_all_usernames():
    data = load_data()
    results = set()
    for location, subdict in data.items():
        results = results.union(set(subdict.keys()))
    return list(results)


@app.route("/")
def front():
    all_usernames = get_all_usernames()
    random.shuffle(all_usernames)
    data = dict([
        (username, get_user_data(username))
        for username in all_usernames
    ])

    in_data = dict([(k, v) for k, v in data.items() if v['knowledge']])
    out_data = dict([(k, v) for k, v in data.items() if not v['knowledge']])

    return flask.render_template("frontpage.html",
                                 in_data=in_data,
                                 out_data=out_data)


def parse_args():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument(
        "-P", "--port", default=9123, type=int, dest="port",
        help="Port to run on",
    )
    parser.add_argument(
        "-H", "--host", default="localhost", dest="host",
        help="Host/interface to run as/bind to",
    )
    parser.add_argument(
        "-d", "--debug", action="store_true", default=False, dest="debug",
        help="Run service in debug mode?  WARNING - allows remote code exec.",
    )
    parser.add_argument(
        "-c", "--children-file", dest="children_file",
        default=default_children_file,
        help="Location on disk of a JSON file defining what children to query."
    )
    parser.add_argument(
        "-e", "--email-file", dest="email_file",
        default=default_email_file,
        help="Location on disk of a JSON file defining known emails.",
    )
    return parser.parse_args()

def initialize_from_config_files():
    global children, known_emails

    with open(children_file, 'r') as f:
        children = yaml.load(f.read())
    with open(email_file, 'r') as f:
        known_emails = yaml.load(f.read())

if __name__ == "__main__":
    args = parse_args()
    children_file = args.children_file
    email_file = args.email_file

    initialize_from_config_files()

    app.run(
        host=args.host,
        port=args.port,
        debug=args.debug,
    )
