#!/usr/bin/env python
# encoding: utf-8
"""
ldap_client -- LDAP client with very basic LDAP operations.

@author:     FengXi
"""

import logging
import ldap 
import ldap.modlist as modlist
import basedn
import sys

logger = logging.getLogger('ldap_client')


def convert_datetime_to_generalized_time(dt):
    """Convert datetime object to generalized time format."""
    dt = dt.timetuple()
    gtime = str(dt.tm_year) + ''.join(
        '0' * (2 - len(str(item))) + str(item) for item in (dt.tm_mon, dt.tm_mday, dt.tm_hour, dt.tm_min, dt.tm_sec))
    return gtime + 'Z'


class Account(object):
    """An user account on LDAP server."""

    def __init__(self, dn, password):
        self.dn = dn
        self.password = password

    def __str__(self):
        return "dn=%s, password=%s" % (self.dn, "******")

    __repr__ = __str__


class Server(object):
    """An LDAP server."""

    def __init__(self, ip, port, uri):
        self.ip = ip
        self.port = port

        self.uri = uri

        if self.uri:
            pass
        else:
            self.uri = "ldap://%s:%s" % (self.ip, self.port)

    def __str__(self):
        if self.uri:
            return self.uri
        else:
            return "ldap://%s:%s" % (self.ip, self.port)


# default server
DEFAULT_SERVER = Server("localhost", 1389, "ldap://localhost:1389")

# default binding user and password, openldap
DEFAULT_ACCOUNT = Account("cn=admin,dc=example,dc=com", "admin")


class Client(object):
    """LDAP client"""

    def __init__(self, server=DEFAULT_SERVER):
        self.server = server
        self._conn = None

    def __str__(self):
        return str(self.server)

    __repr__ = __str__

    def connect(self, trace_level=2, trace_file=sys.stdout):
        """Connect to a LDAP server.

        """
        logger.info("connect to %s" % self.server)
        # blind trust all certs for test purpose.
        ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)

        conn = ldap.initialize(uri=self.server.uri, trace_level=trace_level, trace_file=trace_file)

        self._conn = conn

    def bind(self, account=DEFAULT_ACCOUNT):
        """bind the LDAP connection to a user"""
        if self._conn:
            self._conn.simple_bind_s(who=account.dn, cred=account.password)

    def connect_bind(self, account=DEFAULT_ACCOUNT, trace_level=2, trace_file=sys.stdout):
        """Connect to a LDAP server and auto bind in sync.

        server: the server instance of LDAP server.

        account: the Account instance of binded user.

        """

        self.connect(trace_level=trace_level, trace_file=trace_file)

        # auto bind
        self.bind(account)

    def close(self):
        """close and unbind a LDAP connection"""
        if self._conn:
            logger.info("close connection.")
            self._conn.unbind_s()

    def add_entry(self, dn, attrs):
        """add an ldap entry

        Args:
            dn: The dn of our new entry/object
            attrs: A dict to help build the "body" of the object

        Example:
        dn="cn=replica,dc=example,dc=com"

        attrs = {}
        attrs['objectclass'] = ['top','organizationalRole','simpleSecurityObject']
        attrs['cn'] = 'replica'
        attrs['userPassword'] = 'aDifferentSecret'
        attrs['description'] = 'User object for replication using slurpd'

        """
        # Convert our dict to nice syntax for the add-function using modlist-module
        if attrs and dn:
            ldif = modlist.addModlist(attrs)
            # Do the actual synchronous add-operation to the ldapserver
            logger.info("add entry %s." % ldif)
            self._conn.add_s(dn, ldif)

    def add_entry_ext(self, dn, attrs, serverctrls=None, clientctrls=None):
        """add an ldap entry

        Args:
            dn: The dn of our new entry/object
            attrs: A dict to help build the "body" of the object

        Example:
        dn="cn=replica,dc=example,dc=com"

        attrs = {}
        attrs['objectclass'] = ['top','organizationalRole','simpleSecurityObject']
        attrs['cn'] = 'replica'
        attrs['userPassword'] = 'aDifferentSecret'
        attrs['description'] = 'User object for replication using slurpd'

        """
        # Convert our dict to nice syntax for the add-function using modlist-module
        if attrs and dn:
            ldif = modlist.addModlist(attrs)
            # Do the actual synchronous add-operation to the ldapserver
            logger.info("add entry %s." % ldif)
            ldap.CONTROL_POST_READ
            return self._conn.add_ext_s(dn, ldif, serverctrls=serverctrls, clientctrls=clientctrls)

    def delete_entry(self, dn):
        """delete an ldap entry by its dn

        Args:
            dn: ldap entry dn

        """
        if dn:
            logger.info("delete entry: %s", dn)
            self._conn.delete_s(dn)

    def recursive_delete(self, base_dn):
        search = self._conn.search_s(base_dn, ldap.SCOPE_ONELEVEL)

        for dn, _ in search:
            self.recursive_delete(dn)

        self.delete_entry(base_dn)

    def search(self, base, scope=ldap.SCOPE_ONELEVEL, filterstr='(objectClass=*)', attrlist=None):
        try:
            return self._conn.search_s(base, scope, filterstr, attrlist)
        except Exception:
            logger.debug("error during search.")
            return None

    def search_user_entryuuid(self, tenant_name, username):
        """search an user's entryuuid"""
        dn = basedn.people_dn(username, tenant_name)
        return self.search_entry_uuid(dn)

    def search_entry_uuid(self, dn):
        """search an entry's entryuuid"""
        r = self.search(base=dn, scope=ldap.SCOPE_BASE, attrlist=["entryUUID"])
        if r is not None and len(r) == 1:
            _, uuids = r[0]
            return uuids.get('entryUUID')[0]

        return None

    def exists_entry(self, dn, filterstr='(objectclass=*)'):
        """check if an entry exists"""
        try:
            r = self.search(dn, scope=ldap.SCOPE_BASE, filterstr=filterstr,
                            attrlist=["1.1"])
            return r is not None and len(r) > 0
        except ldap.NO_SUCH_OBJECT:
            logger.debug("entry '%s' does not exists.", dn)
            return False

        return False

    def exists_user(self, tenant_name, username):
        """check if a user exists"""
        base = basedn.people_dn(username, tenant_name)
        return self.exists_entry(base)

    def add_one_attr(self, dn, attr_name, attr_val):
        mod = (ldap.MOD_ADD, attr_name, attr_val)
        modlist = (mod,)

        self._conn.modify_s(dn, modlist)

    def replace_entry(self, dn, attrs):
        """replace an existing entry"""
        mods = []
        for name, val in attrs.iteritems():
            mod = (ldap.MOD_REPLACE, name, val)
            mods.append(mod)
        if modlist:
            self._conn.modify_s(dn, mods)
        pass

    def replace_one_attr(self, dn, attr_name, attr_val):
        mod = (ldap.MOD_REPLACE, attr_name, attr_val)
        mods = (mod,)

        self._conn.modify_s(dn, mods)

    def create_ou(self, dn, name, description):
        """Create an LDAP ou
        """
        attrs = {'objectclass': ['top', 'organizationalUnit'], 'ou': name, 'description': description}
        self.add_entry(dn, attrs)

    def del_one_attr(self, dn, attr_name, attr_val):
        mod = (ldap.MOD_DELETE, attr_name, attr_val)
        modlist = (mod,)

        self._conn.modify_s(dn, modlist)


if __name__ == '__main__':
    server = Server('xfd4',1389,'abc')
    print server
    print server.uri

    server = Server('xfd4',1389,None)
    print server
    print server.uri
    pass
