#!/usr/bin/env python
# encoding: utf-8
"""
Created on May 16, 2019
org -- Organization CRUD utility

@author:     FengXi
"""
import logging

import basedn
import ldap_client
import random
import ldap

logger = logging.getLogger("organization")
_DEBUG = False


class Organization(object):
    def __init__(self, dn, name, description):
        """
        dn : organization entrydn.
        name : organization name.
        description: organization description.
        """
        self.dn = dn
        self.name = name
        self.description = description

    def __str__(self):
        return "dn=%s,name=%s,description=%s" % (self.dn, self.name, self.description)

    __repr__ = __str__


class CRUD(object):
    """CRUD operation on a Organization"""

    def __init__(self, ldapclient):
        self._client = ldapclient

    def create(self, org, tenant_name, members=None):
        """create an organization

        Args:
            org: an Organization instance
            tenant_name: tenant name
        """
        attrs = {}
        attrs['objectclass'] = ['top', 'groupOfUniqueNames']
        attrs["cn"] = org.name
        attrs['description'] = org.description

        # hack, some ldap server like openldap needs at leas a uniqueMember for groupOfUniqueNames, but opendj not
        if members is None:
            attrs['uniqueMember'] = ['uid=dummy-user,ou=people']
        else:
            attrs['uniqueMember'] = members

        self._client.add_entry(org.dn, attrs)

    def modify_unique_member(self, org_dn, user_dn):
        self._client.replace_one_attr(org_dn, 'uniqueMember', user_dn)

    def delete(self, org):
        """delete an Organization"""
        self._client.recursive_delete(org.dn)

    def sample(self, tenant_name, choices, member_choices):
        """sample Organization
        :return:one list of all orgs_dn
        """
        def _pick_members():
            l = len(member_choices)
            count = random.randint(1, min(l, 10))
            return random.sample(member_choices, count)

        for choice in choices:
            if choice:
                org = self.line2Org(tenant_name,choice)
                self.create(org, tenant_name, members=_pick_members())

        return
    

    def line2Org(self,tenant_name,line):
        name = line.split(',')[0].split('=')[1]
        dn = line + ',' + basedn.org_base(tenant_name)
        org = Organization(dn=dn, name=name, description=name)

        return org


if __name__ == "__main__":
    # _DEBUG = True
    if _DEBUG:
        pass
