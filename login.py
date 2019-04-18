#!/usr/bin/env python
# encoding: utf-8
"""
login -- login utility

@author:     FengXi
"""

import logging
import sys

import ldap_client
from argparse import ArgumentParser
from argparse import ArgumentDefaultsHelpFormatter

logger = logging.getLogger("login")


def main(argv=None):
    """Command line options."""

    if argv is None:
        argv = sys.argv
    else:
        sys.argv.extend(argv)

    # add command line options/parser
    parser = ArgumentParser(description="ldap login.", formatter_class=ArgumentDefaultsHelpFormatter)

    parser.add_argument("--uri", help="LDAP URI. For example: ldaps://localhost:1636", default="ldap://localhost:1389")
    parser.add_argument("-D", "--bindDN", help="DN to use to bind to the server.")
    parser.add_argument("-w", "--bindPassword", help="Password to use to bind to the server.")

    # parse arguments
    args = parser.parse_args()

    ldap_server = ldap_client.Server(None, None, args.uri)
    ldap_account = ldap_client.Account(args.bindDN, args.bindPassword)

    # ldap client instance
    client = ldap_client.Client(ldap_server)
    client.connect_bind(ldap_account)

    client.close()


if __name__ == "__main__":
    sys.exit(main())
