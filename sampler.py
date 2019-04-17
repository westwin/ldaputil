#!/usr/bin/env python
# encoding: utf-8
"""
sampler -- Sampler utility

@author:     FengXi
"""

import logging
import sys

import ldap_client
from argparse import ArgumentParser
from argparse import ArgumentDefaultsHelpFormatter
import json

logger = logging.getLogger("sampler")


def main(argv=None):
    """Command line options."""

    if argv is None:
        argv = sys.argv
    else:
        sys.argv.extend(argv)

    # add command line options/parser
    parser = ArgumentParser(description="Sample LDAP Data, including Org, People,Token etc.",
                            formatter_class=ArgumentDefaultsHelpFormatter)

    parser.add_argument("--host", help="@deperated, please use --uri.", default="localhost")
    parser.add_argument("-p", "--port", help="@deprecated, please use --uri.", type=int, default=1389)

    parser.add_argument("-D", "--bindDN", help="DN to use to bind to the server.", default="cn=admin,dc=example,dc=com")
    parser.add_argument("-w", "--bindPassword", help="Password to use to bind to the server.", default="admin")

    parser.add_argument("--subject", help="Sample subject #.", type=int, default=10000)
    parser.add_argument("--prefix", help="username prefix sequentially.")

    parser.add_argument("--chinese", help="Sampler Chinese names #.", action="store_true", default=False)

    # parse arguments
    args = parser.parse_args()
    ldap_server = ldap_client.Server(args.host, args.port, None)

    ldap_account = ldap_client.Account(args.bindDN, args.bindPassword)

    # ldap client instance
    client = ldap_client.Client(ldap_server)
    client.connect_bind(ldap_account)

    # sample English names
    firstname_dict_file = "sample/census-dist-all-first.txt"
    lastname_dict_file = "sample/census-dist-all-last.txt"

    # sample Chinese names
    if args.chinese:
        firstname_dict_file = "sample/census-dist-all-first-cn.txt"
        lastname_dict_file = "sample/census-dist-all-last-cn.txt"

    firstname_choices = [line.rstrip('\n').strip().title() for line in open(firstname_dict_file, 'r')]
    lastname_choices = [line.rstrip('\n').strip().title() for line in open(lastname_dict_file, 'r')]
    username_choices = [line.rstrip('\n').strip().lower() for line in open('sample/usernames.txt', 'r')]

    # sample people/token data.
    all_tenants = ("example",)
    import subject

    s_crud = subject.CRUD(client)  # subject crud client

    for t in all_tenants:
        # then create sample subject.
        s_crud.sample(t, firstname_choices=firstname_choices, lastname_choices=lastname_choices,
                                 username_choices=username_choices, count=args.subject,
                                 prefix=args.prefix)
    client.close()


if __name__ == "__main__":
    sys.exit(main())
