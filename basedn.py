#!/usr/bin/env python
# encoding: utf-8
"""
Created on Sep 1, 2016

@author: FengXi
"""

import ldap.dn as dn

RESERVED_TENANT = "example"

def escape(val):
    """safely escape ldap dn"""
    return dn.escape_dn_chars(val)

def tenant_base(tenant_name=RESERVED_TENANT):
    return "dc=%s,dc=com" % (escape(tenant_name))

def people_base(tenant_name):
    return "ou=People," + tenant_base(tenant_name)

def subject_base(tenant_name):
    return people_base(tenant_name)

def people_dn(username, tenant_name=RESERVED_TENANT):
    return "uid=%s," % (escape(username)) + people_base(tenant_name)


def org_base(tenant_name):
    return "ou=Organizations," + tenant_base(tenant_name)


def org_dn(org_name, rdn):
    return "cn=%s," % (escape(org_name)) + rdn


def v2_org_dn(tenant_name, *names):
    rdns = []

    for p in names:
        rdns.append("cn=%s" % (escape(p)))

    rdns.append(org_base(tenant_name))

    return ','.join(rdns)


if __name__ == "__main__":
    pass
