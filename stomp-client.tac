from twisted.application import service
from stompify import app, dispatcher

class MyDispatcher(dispatcher.StompClient):
    def on_message(self, frame, proto):
        print "message received: %s" % frame
        self.disconnect('eof')

    def on_receipt(self, frame, proto):
        print "receipt received: %s" % frame
        if frame.getHeader('receipt-id') == 'eof':
             from twisted.internet import reactor
             reactor.callLater(2, self._halt)
 
    def _halt(self):
        print "eof eof eof"

def _started(dispatcher):
   dispatcher.subscribe('/queue/temp')
   dispatcher.send(body="hello world", destination='/queue/temp')
     
application = service.Application('stomp')
stomp = app.StompClientService()
stomp.setFrameDispatcher(MyDispatcher)

stomp.start().addCallback(_started)

stomp.setServiceParent(application)

