#!/usr/bin/env python
""" $ who-is-in-http-service.py [OPTIONS]

A micro http app to query the doctor DB.  An instance of this
should be run on every monitored node alongside the scanner
script.

It can be queried by the master webapp, an IRC bot, a local script, whatever.

:Author:    Ralph Bean
:License:   GPLv2+

"""

import flask
import json
import argparse


app = flask.Flask(__name__)
cache = default_cache = "/tmp/doctors.db"


@app.route("/")
def hello():
    with open(cache, 'r') as f:
        d = json.loads(f.read())
    return flask.jsonify(d)


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
        "-c", "--onfile-cache", dest="cache", default=default_cache,
        help="Where to store the doctors cache on disk"
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    cache = args.cache
    app.run(
        host=args.host,
        port=args.port,
        debug=args.debug,
    )
