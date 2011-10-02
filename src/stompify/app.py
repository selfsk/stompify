'''
Created on Sep 30, 2011

@author: sk
'''

from twisted.application import service

from stompify import proto, dispatcher

class StompService(service.Service):
    _dispatcher = dispatcher.StompServer
    
    def setFrameDispatcher(self, _dispClass):
        self._dispatcher = _dispClass
     
    def startService(self):
        service.Service.startService(self)
        from twisted.internet import reactor
        
        
        f = proto.StompFactory()
        f.setDispatcher(self._dispatcher)
        
        reactor.listenTCP(61613, f)
        
    