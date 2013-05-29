#!/usr/bin/env python
""" "who is in" via python
    Ralph Bean 05/29/2013

based on

    rev 0.1
    who is in via bash
    Emilio Del Plato 5/14/2013

example ping to bt device::

    $ l2ping 5C:6B:32:49:36:B6 -c 3

"""

from __future__ import print_function

import argparse
import json
import pprint
import os
import sys
import time

cmd = "sudo l2ping {btaddr} -c 3 > /dev/null 2>&1"

bluetooth_addresses = dict(
    karen=dict(
        phone='5C:6B:32:49:36:B6',
    ),
    emilio=dict(
        phone='04:E4:51:10:10:B0',
        pebble='00:18:33:E4:F2:F0',
    ),
    threebean=dict(
        phone='4C:BC:A5:1A:9F:57',
    ),
    paulmezz=dict(
        phone='80:96:B1:54:84:B5',
    ),
    chuck=dict(
        phone='CC:08:E0:16:A2:7C',
    ),
)


def set_value(doctors, key, subkey, newval):
    if key in doctors and \
       subkey in doctors[key] and \
       doctors[key][subkey] is newval:
        # Then, nothing changed.
        pass
    else:
        doctors[key] = doctors.get(key, {})
        doctors[key][subkey] = newval
        # TODO -- emit a message to the world here


def ping_all(args, doctors):
    print("* Pinging all")
    for username, btaddrs in bluetooth_addresses.items():
        for device, btaddr in btaddrs.items():
            key = "%s/%s" % (username, device)
            if args.verbose:
                print("  * Checking %r -> %r" % (key, btaddr))
            result = os.system(cmd.format(btaddr=btaddr))
            newval = result is 0
            set_value(doctors, username, device, newval)


def ping_all_and_cache(args):

    if args.verbose:
        print("Opening cache %r" % args.cache)

    try:
        with open(args.cache, 'r') as f:
            doctors = json.loads(f.read())
    except IOError:
        print("Couldn't read %r.  Starting afresh." % args.cache)
        doctors = {}

    ping_all(args, doctors)

    if args.verbose:
        print("DB is %r" % pprint.pformat(doctors))
        print("Closing cache")

    with open(args.cache, 'w') as f:
        f.write(json.dumps(doctors, indent=4))


def parse_args():
    """ who-is-in-scanner.py [OPTIONS]

    Background process that scans bluetooth for persons,
    and caches state to disk.

    Needs to be run as root or with passwordless sudo for l2ping.
    """
    parser = argparse.ArgumentParser(usage=parse_args.__doc__)
    parser.add_argument(
        "-i", "--sleep-interval", dest="sleep_interval", default=10,
        help="Number of seconds to sleep between scans",
    )
    parser.add_argument(
        "-v", "--verbose", dest="verbose", default=False,
        action="store_true",
        help="Produce more output to stdout",
    )
    parser.add_argument(
        "-c", "--onfile-cache", dest="cache", default="/tmp/doctors.db",
        help="Where to store the doctors cache on disk"
    )

    return parser.parse_args()


def main():
    args = parse_args()
    while True:
        ping_all_and_cache(args)
        time.sleep(args.sleep_interval)


if __name__ == '__main__':
    main()
