#!/usr/bin/env python
# encoding: utf-8
"""
subject -- Subject CRUD utility

@author:     FengXi
"""

import basedn
import logging
import time
import random
import string
import uuid
import datetime
import ldap

logger = logging.getLogger("subject")


class Subject(object):
    def __init__(self, username):
        self.username = username

    def __str__(self):
        return self.username

    __repr__ = __str__


class People(Subject):
    def __init__(self, username, first_name, last_name, email="blabla@mailinator.com",
                 mobile="13488821234", tel="01082221234", pwd="1"):
        super(People, self).__init__(username)

        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.mobile = mobile
        self.tel = tel
        self.pwd = pwd

    def dn(self, tenant):
        return basedn.people_dn(self.username,tenant_name=tenant)

    def __str__(self):
        return "%s,%s,%s" % (self.username, self.first_name, self.last_name)

    __repr__ = __str__

class CRUD(object):
    """CRUD operation on a Subject"""

    def __init__(self, ldapclient):
        self._client = ldapclient

    def is_ascii(self, s):
        return all(ord(c) < 128 for c in s)

    def create(self, tenant, people):
        """create a people

        Args:
            peole: a People instance
        """
        dn = basedn.people_dn(people.username,tenant_name=tenant)

        attrs = {}
        attrs['objectclass'] = ['inetOrgPerson']
        attrs["uid"] = people.username

        attrs['sn'] = people.last_name
        attrs['givenName'] = people.first_name

        if self.is_ascii(people.first_name) or self.is_ascii(people.last_name):
            # english name
            attrs['cn'] = "%s %s" % (people.first_name, people.last_name)
        else:
            # chinese name
            attrs['cn'] = "%s%s" % (people.first_name, people.last_name)

        attrs['description'] = "%s profile." % attrs['cn']
        attrs['userPassword'] = people.pwd
        attrs['mail'] = [people.email]
        attrs['telephoneNumber'] = [people.tel]

        # use customized mobile number
        # attrs['mobileTelephoneNumber'] = [people.mobile]
        attrs['mobile'] = [people.mobile]

        self._client.add_entry(dn, attrs)

    def delete(self, username, tenant_name):
        """delete a Subject"""
        dn = basedn.people_dn(username, tenant_name)
        self._client.delete_entry(dn)

    def get_all(self, tenant_name):
        """get all People(s)"""
        base = basedn.people_base(tenant_name)
        r = self._client.search(base, filterstr='(objectClass=inetOrgPerson)', attrlist=["*"])

        peoples = []
        for _, entry in r:
            p = People(entry.get("uid")[0], entry.get("givenName")[0], entry.get("sn")[0],
                       entry.get("mail")[0], entry.get("mobile")[0], entry.get("telephoneNumber")[0],
                       entry.get("userPassword")[0])
            peoples.append(p)

        return peoples

    def exists(self, tenant_name, username):
        """check if a user name exists"""
        base = basedn.people_base(tenant_name)
        r = self._client.search(base, filterstr='(&(objectClass=inetorgperson)(uid=%s))' % basedn.escape(username),
                                attrlist=["1.1"])

        return len(r) > 0

    def clean(self, tenant_name):
        """delete all People"""

        all_people = self.get_all(tenant_name)
        for p in all_people:
            self.delete(p.username, tenant_name)

    def sample(self, tenant_name, firstname_choices=None, lastname_choices=None, username_choices=None, count=10,
               prefix=None):
        """sample subject"""
        # if len(username_choices) < count:
        #    padding_count = count - len(username_choices)
        #    for idx in range(0,padding_count):
        #        username_choices.append("padding-user-%s-%s" % (int(round(time.time())), idx))

        def _pick_one_username():
            candidate = random.choice(username_choices)
            while True:
                if not self.exists(tenant_name, candidate):
                    return candidate
                else:
                    candidate = "%s_%s_%s" % (candidate, int(round(time.time())), random.random())

        def _pick_one_firstname():
            return random.choice(firstname_choices)

        def _pick_one_lastname():
            return random.choice(lastname_choices)

        def _pick_one_tel():
            length = random.choice([8, 9, 10, 11, 12])

            return ''.join(random.choice(string.digits) for _ in range(length))

        dn_list = []
        for idx in range(0, count):
            # do not randomize username, simply append an index to a fixed prefix.
            if prefix:
                username = "%s.%s" % (prefix, idx)
                first_name = "%s_fn.%s" % (prefix, idx)
                last_name = "%s_ln.%s" % (prefix, idx)
            else:
                username = _pick_one_username()
                first_name = _pick_one_firstname()
                last_name = _pick_one_lastname()

            email = "%s@mailinator.com" % username
            mobile = _pick_one_tel()
            tel = _pick_one_tel()

            pwd = "1"

            # create people
            people = People(username=username, first_name=first_name, last_name=last_name, email=email,
                            mobile=mobile, tel=tel, pwd=pwd)
            self.create(tenant_name, people)

            dn = people.dn(tenant_name)
            dn_list.append(dn)

        return dn_list


if __name__ == "__main__":
    pass
