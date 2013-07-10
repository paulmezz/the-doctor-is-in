#!/usr/bin/env python
""" "who is in" via python
    Ralph Bean 05/29/2013
    License: GPLv2+

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
import yaml
import pprint
import os
import sys
import time

cmd = "sudo l2ping {btaddr} -c 3 > /dev/null 2>&1"

default_bluetooth_addresses_file = "etc/bluetooth.yaml"


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


def ping_all(args, doctors, bluetooth_addresses):
    print("* Pinging all")
    for username, btaddrs in bluetooth_addresses.items():
        for device, btaddr in btaddrs.items():
            key = "%s/%s" % (username, device)
            if args.verbose:
                print("  * Checking %r -> %r" % (key, btaddr), end='')
		sys.stdout.flush()
            result = os.system(cmd.format(btaddr=btaddr))
            newval = result is 0
            if args.verbose:
                print(" | %r (%r)" % (newval, result))
            set_value(doctors, username, device, newval)


def ping_all_and_cache(args, bluetooth_addresses):

    if args.verbose:
        print("Opening cache %r" % args.cache)

    try:
        with open(args.cache, 'r') as f:
            doctors = json.loads(f.read())
    except IOError:
        print("Couldn't read %r.  Starting afresh." % args.cache)
        doctors = {}

    ping_all(args, doctors, bluetooth_addresses)

    if args.verbose:
        print("DB is %r" % pprint.pformat(doctors))
        print("Closing cache")

    with open(args.cache, 'w') as f:
        f.write(json.dumps(doctors, indent=4))


def parse_args():
    """ $ who-is-in-scanner.py [OPTIONS]

    Background process that scans bluetooth for persons,
    and caches state to disk.

    Needs to be run as root or with passwordless sudo for l2ping.

    License: GPLv2+
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
    parser.add_argument(
        "-a", "--bluetooth-address-file", dest="bluetooth_addresses_file",
        default=default_bluetooth_addresses_file,
        help="Where to find the bluetooth addresses (in YAML format)",
    )

    return parser.parse_args()


def main():
    args = parse_args()

    with open(args.bluetooth_addresses_file, 'r') as f:
        bluetooth_addresses = yaml.load(f.read())

    while True:
        ping_all_and_cache(args, bluetooth_addresses)
        time.sleep(args.sleep_interval)


if __name__ == '__main__':
    main()
