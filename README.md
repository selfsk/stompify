# STOMPify

STOMPify is a implementation of [STOMP][1] protocol on top of [twisted][2].

# Code
    from twisted.internet import reactor, defer
    from stompify import proto, dispatcher

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
     

    start_defer = defer.Deferred()
    f = proto.StompClientFactory()
    f.setDispatcher(MyDispatcher, start_defer)

    start_defer.addCallback(_started)
    reactor.connectTCP('localhost', 61613, f)
    reactor.run()

# Goals
 * Follow twisted coding style and standard
 * Make it possible to embed this implementation in any twisted application

# Install (easy_install based)

python setup.py install (or develop for development)

# Examples

There are few examples of NodeSet framework usage:

 * stomp.tac - twistd .tac file for STOMP server
 * stomp-client.tac - twisted .tac file for STOMP client
 * stom_c.py - python script with twisted reactor.run()

[1]: http://stomp.github.com/
[2]: http://twistedmatrix.com

