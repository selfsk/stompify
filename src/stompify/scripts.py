'''
Created on Sep 30, 2011

@author: sk
'''

from twisted.application import service
from stompify import app

def run_simple():
    from twisted.scripts.twistd import run
    run()
    #from twisted.internet import reactor
    
    #appl = service.Application('stomp')
    #stomp = app.StompService()
    
    #stomp.setServiceParent(appl)
    
    
    #f = proto.StompFactory()
    #f.dispatcher = dispatcher.StompFrameDispatcher()
    
    #reactor.listenTCP(61613, f)
    #reactor.run()

    
    