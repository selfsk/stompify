'''
Created on Oct 3, 2011

@author: sk
'''

class SubscriptionManager(object):
    
    def __init__(self):
        self._subscriptions = {}
        self._subsIds = {} # make a match between _id and _dest (to make quick lookup over _subscriptions in case of unsub
    
    def _clean_by_proto(self, _dest, proto):
        for _id, items in self._subscriptions[_dest].items():
            for t in items:
                if t[1] == proto:
                    self._subscriptions[_dest][_id].remove(t)
                    break
                
    def add(self, proto, _id, _dest, _ack='auto'):
        
        if self._subscriptions.has_key(_dest):
            self._subscriptions[_dest][_id].add((_ack, proto))
        else:
            self._subscriptions[_dest] = {}
            self._subscriptions[_dest][_id] = set([(_ack, proto)])
           
        if self._subsIds.has_key(_id): 
            self._subsIds[_id].add(_dest)
        else:
            self._subsIds[_id] = set([_dest])
    
    def get(self, _dest, _id):
        pass

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

        