# ldap utility python script

## Depedencies

1. **python 2.7**
2. python-ldap: sudo yum install -y python-ldap

## Features

suppose:

1. ou=people,dc=example,dc=com exists to store all users
2. ou=organization,dc=example,dc=com exists to store all organizations

features:

1. bulk sample inetOrgPerson:(all passwords are set to 1)
   1. ./samper.py --subject 10 --prefx test // create 10 users whose username starts with test
   2. ./samper.py --subject 10 --chinese // create 10 users for whom, randomize username, and randomize with a chinese name
2. bulk sample groupOfUniqueNames: ./samper.py --org // create organizations
3. bulk sample inetOrgPerson and groupOfUniqueNames:
   1. ./samper.py --subject 100 --prefix test --org // create 100 users and some orgs, then randomize the membership
4. login test:
   1. ./login.py --uri ldap://localhost:1389 -D 'uid=test.0@mailinator.com,ou=people,dc=example,dc=com' -w '1'
