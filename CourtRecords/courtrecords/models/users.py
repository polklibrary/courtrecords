from sqlalchemy import Column,Integer,BigInteger,String,Unicode,Boolean,TIMESTAMP,ForeignKey,Table,Text
from sqlalchemy.orm import relation
from courtrecords.models import Base,DBSession,Model
import os, transaction, datetime, time,hashlib


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
    password_failures = Column(Integer)
    session_timestamp = Column(BigInteger(unsigned=True))
    password_timestamp = Column(BigInteger(unsigned=True))
    password_history = Column(Text)
    
    def __init__(self, **kwargs):
        from courtrecords.security.acl import ACL
        self.email = kwargs.get('email','')
        self.set_password(kwargs.get('password',None))
        self.group = ACL.AUTHENTICATED
        self.update_session_timestamp()
        self.update_password_timestamp()
        self.password_history += self.password
        self.password_failures = 0


    def check_old_passwords(self, password):
        if isinstance(password, unicode):
            password_8bit = password.encode('UTF-8')
        else:
            password_8bit = password
        password_hash = hashlib.sha256(password_8bit).hexdigest()
        return password_hash in self.password_history

    def set_password(self, password):
        if isinstance(password, unicode):
            password_8bit = password.encode('UTF-8')
        else:
            password_8bit = password
            
        password_hash = hashlib.sha256(password_8bit).hexdigest()

        if self.password_history:
            self.password_history += '|' + password_hash
        else:
            self.password_history = password_hash
            
        self.password = password_hash

    def validate_password(self, password):
        if isinstance(password, unicode):
            password_8bit = password.encode('UTF-8')
        else:
            password_8bit = password
        password_hash = hashlib.sha256(password_8bit).hexdigest()
        return self.password == password_hash and self.password != None
        

    def add_user(self):
        if self.__class__.__name__ == 'Users':
            DBSession.add(self)
            transaction.commit()
    
    
    def update_session_timestamp(self):
        self.session_timestamp = int(time.time())
        
    def update_password_timestamp(self):
        self.password_timestamp = int(time.time())
        
    
    
    
class GuestUser(object):
    id = 0
    user = 'Guest'
    password = 'Guest'
    group = 'Anonymous'
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    