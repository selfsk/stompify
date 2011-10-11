'''
Created on Sep 30, 2011

@author: sk
'''

from twisted.application import service
from twisted.internet import defer

from stompify import proto, dispatcher

class StompService(service.Service):
    _dispatcher = dispatcher.StompServer
    _port = 61613
    _start_defer = defer.Deferred()
    _factory = proto.StomServerFactory
    
    def setFrameDispatcher(self, _dispClass):
        self._dispatcher = _dispClass
     
    def setPort(self, port):
        self._port = port
        
    def startService(self):
        service.Service.startService(self)
        
        f = self._factory()
        f.setDispatcher(self._dispatcher, self._start_defer)
        
        self._start(f)
    
    def _start(self, f):
        from twisted.internet import reactor
        reactor.listenTCP(self._port, f)
     
    def start(self):
        return self._start_defer
       
class StompClientService(StompService):
    _dispatcher = dispatcher.StompClient
    _host = 'localhost'
    _factory = proto.StompClientFactory
  
    def connect(self):
        return self._start_defer
      
    def setHost(self, host):
        self._host = host
        
    def _start(self, f):
        from twisted.internet import reactor
        reactor.connectTCP(self._host, self._port, f)
        
            

    