'''
Created on Oct 3, 2011

@author: sk
'''

import uuid


class Subscription(object):
    
    def __init__(self, proto, _id, _dest, _ack):
        self._id = _id
        self._ack = _ack
        self._dest = _dest
        self._proto = proto
        
    def getId(self):
        return self._id
    def getAck(self):
        return self._ack
    
    def getDest(self):
        return self._dest
    
    def getProto(self):
        return self._proto
    
    def messageId(self):
        return str(uuid.uuid4())
    
class SubscriptionManager(object):
    
    def __init__(self):
        self._subscriptions = {}
        self._subsIds = {} # make a match between _id and _dest (to make quick lookup over _subscriptions in case of unsub
        self._ack = {}
        
    def _clean_by_proto(self, _dest, proto):
        for _id, items in self._subscriptions[_dest].items():
            for subitem in items:
                if subitem.getProto() == proto:
                    self._subscriptions[_dest][_id].remove(subitem)
                    break
                
    def add(self, proto, _id, _dest, _ack='auto'):
        
        subs = Subscription(proto, _id, _dest, _ack)
        
        if self._subscriptions.has_key(_dest):
            self._subscriptions[_dest][_id].add(subs)
        else:
            self._subscriptions[_dest] = {}
            self._subscriptions[_dest][_id] = set([subs])
           
        if self._subsIds.has_key(_id): 
            self._subsIds[_id].add(_dest)
        else:
            self._subsIds[_id] = set([_dest])
    
    def get(self, _dest, _id):
        if self._subscriptions.has_key(_dest):
            return self._subscriptions[_dest].get(_id)

        return set([None])
    
    def remove_by_proto(self, proto):
        for _dest in self._subscriptions:
            self._clean_by_proto(_dest, proto)
            
    def remove(self, proto, _id):
        if self._subsIds.has_key(_id):
            for _dest in self._subsIds[_id]:
                self._clean_by_proto(_dest, proto)
                    
    def lookup(self, _dest):
        if self._subscriptions.get(_dest):
            return self._subscriptions[_dest]
        
        return {}

        