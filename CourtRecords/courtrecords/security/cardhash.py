from courtrecords.models import Users,GuestUser
from courtrecords.security.acl import ACL
from pyramid.decorator import reify
from pyramid.request import Request
from pyramid.security import Allow, Authenticated, ALL_PERMISSIONS, Everyone, unauthenticated_userid, has_permission

import hashlib

ORDERING = ['orderType','orderNumber','orderName','orderDescription','amount','orderFee','currentAmountDue','balance','currentBalance',
'dueDate','userChoice1','userChoice2','userChoice3','userChoice4','userChoice5','userChoice6','userChoice7','userChoice8','userChoice9',
'userChoice10','userChoice11','userChoice12','userChoice13','userChoice14','userChoice15','userChoice16','userChoice17','userChoice18','userChoice19',
'userChoice20','userChoice21','userChoice22','userChoice23','userChoice24','userChoice25','paymentMethod','streetOne','streetTwo','city','state','zip',
'country','daytimePhone','eveningPhone','email','redirectUrl','redirectUrlParameters','retriesAllowed','contentEmbedded','timestamp',
]
    
    
def hash_transaction(**kwargs):
    return sha256(hash_ordering(**kwargs))
    
def hash_ordering(**kwargs):

    hash_string = ""
    for name in ORDERING:
        value = kwargs.get(name, None)
        if value:
            hash_string += str(value)

    print "HASH ORDER: " + hash_string
    return hash_string + kwargs.get('key', '')
    
def generate_return_url(url, **kwargs):
    params = ''
    for name,value in kwargs.items():
        params += str(name) + "=" + str(value) + '&'
    return url + '?' + params[:-1]
     
    
def generate_url(url, hash, **kwargs):
    params = ''
    for name in ORDERING:
        value = kwargs.get(name, "")
        if value:
            params += str(name) + "=" + str(value) + '&'
    return url + '?' + params[:-1] + '&hash=' + hash
    
def sha256(string):
    return hashlib.sha256(string.encode('utf-8')).hexdigest()
    
def md5(string):
    return hashlib.md5(string.encode('utf-8')).hexdigest()
    