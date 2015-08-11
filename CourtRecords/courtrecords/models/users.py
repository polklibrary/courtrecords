from sqlalchemy import Column,Integer,BigInteger,String,Unicode,Boolean,TIMESTAMP,ForeignKey,Table
from sqlalchemy.orm import relation
from hashlib import sha1
from courtrecords.models import Base,DBSession,Model

import os,transaction,datetime


class Users(Base,Model):
    __tablename__ = 'users'

    # __scaffold__ = [{'id': { 'widget': 'input', 'label': 'ID', 'attributes': {'type':'text', 'disabled':'true'} } },
                    # {'email': { 'widget': 'input', 'label': 'Email', 'attributes': {'type':'text'} } },
                    # {'group': { 'widget': 'select', 'label': 'Group', 'attributes': {'type':'text'} , 'options': { 'Authenticated':'Authenticated', 
                                                                                                                   # 'Editor':'Editor',
                                                                                                                   # 'Administrator':'Administrator', } } },
    # ]

    
    id = Column(Integer, primary_key=True)
    email = Column(Unicode(25), unique=True)
    password = Column(Unicode(255))
    group = Column(Unicode(25))
    
    def __init__(self, **kwargs):
        from courtrecords.security.acl import ACL
        self.email = kwargs.get('email','')
        self.set_password(kwargs.get('password',None))
        self.group = ACL.AUTHENTICATED

    def set_password(self, password):
        hashed_password = password
        if isinstance(password, unicode):
            password_8bit = password.encode('UTF-8')
        else:
            password_8bit = password

        salt = sha1()
        salt.update(os.urandom(60))
        hash = sha1()
        hash.update(password_8bit + salt.hexdigest())
        hashed_password = salt.hexdigest() + hash.hexdigest()

        if not isinstance(hashed_password, unicode):
            hashed_password = hashed_password.decode('UTF-8')
        self.password = hashed_password

    def validate_password(self, password):
        hashed_pass = sha1()
        hashed_pass.update(password + self.password[:40])
        return self.password[40:] == hashed_pass.hexdigest() and self.password != None

    def add_user(self):
        if self.__class__.__name__ == 'Users':
            DBSession.add(self)
            transaction.commit()
    
    
    
class GuestUser(object):
    id = 0
    user = 'Guest'
    password = 'Guest'
    group = 'Anonymous'
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    