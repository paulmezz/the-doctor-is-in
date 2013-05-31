#!/usr/bin/env python
""" A front-facing http app to show who is where.

:Author:    Ralph Bean
:License:   GPLv2+

"""

import flask
import json
import random
import urllib
import hashlib


app = flask.Flask(__name__)

# TODO -- someday move this to a config file or CLI switches
port = 9000
host = 'localhost'
# This is a dict of locations of the micro http services
children = {
    "here": "http://localhost:9123",
}
# XXX - Be careful with this.  It allows remote code execution
debug = True

known_emails = {
    'threebean': 'rbean@redhat.com',
    'paulmezz': 'paul@themezz.com',
}


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
    print results, "is all usernames"
    return list(results)


def get_location_data(location):
    raise NotImplementedError("wat")


@app.route("/user/<username>/")
def by_user(username):
    results = get_user_data(username)
    return flask.render_template("username.html", results=results)


@app.route("/location/<location>/")
def by_location(location):
    data = get_location_data(location)
    return flask.render_template("location.html", results=data[location])


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


if __name__ == "__main__":
    app.run(
        host=host,
        port=port,
        debug=debug,
    )
