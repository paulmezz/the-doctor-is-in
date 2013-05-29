#!/usr/bin/env python
""" A micro http app to query the doctor DB.

:Author:    Ralph Bean
:License:   GPLv2+

"""

import flask
import shelve


app = flask.Flask(__name__)

# TODO -- someday move this to a config file or CLI switches
port = 9123
host = 'localhost'
cache = '/tmp/doctors.db'
# XXX - Be careful with this.  It allows remote code execution
debug = False


@app.route("/")
def hello():
    d = shelve.open(cache)
    try:
        return flask.jsonify(d)
    finally:
        d.close()


if __name__ == "__main__":
    app.run(
        host=host,
        port=port,
        debug=debug,
    )
