#!/usr/bin/env python
from __future__ import print_function

import argparse
import shelve
import pprint


def parse_args():
    """ who-is-in-dump-db.py [OPTIONS]

    Dumps out the contents of the berkley db to debug.
    """
    parser = argparse.ArgumentParser(usage=parse_args.__doc__)
    parser.add_argument(
        "-c", "--onfile-cache", dest="cache", default="/tmp/doctors.db",
        help="Where to store the doctors cache on disk"
    )

    return parser.parse_args()


def main():
    args = parse_args()
    doctors = shelve.open(args.cache)
    pprint.pprint(doctors)
    doctors.close()


if __name__ == '__main__':
    main()
