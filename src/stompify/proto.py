'''
Created on Sep 30, 2011

@author: sk
'''

from twisted.internet import protocol
from twisted.protocols import basic
from twisted.python import log

from stompify import dispatcher

#from twisted.internet import protocol

_stomp_frames = ['SEND', 'CONNECT', 'CONNECTED', 'SEND', 'SUBSCRIBE', 'UNSUBSCRIBE', 
                'BEGIN', 'COMMIT', 'ABORT', 'ACK', 'NACK', 'DISCONNECT', 'MESSAGE', 'RECEIPT', 'ERROR']

class StompFrame(object):
    
    def __init__(self, frame_type):
        """
        @param frame_type: frame type (i.e. CONNECT, CONNECTED, SEND)
        """
        self._frame = frame_type.lower()
        self._headers = {}
        self._body = [] #FIXME: use something like StringIO is more preferrable
    
        self._in_header = True

    def parse(self, raw_line):
        if self._in_header:
            if raw_line.find(':') > 0:
                header, value = raw_line.split(':')
            
                self.setHeader(header, value)
            elif raw_line == '':
                self._in_header = False
        else:
            self._body.append(raw_line)
            
    def setHeader(self, header, value):
        self._headers[header] = value
        
    def getHeader(self, header):
        return self._headers.get(header)
    
    def getType(self):
        return self._frame
    
    def getBody(self):
        return self._body
    
class StompFrameObserver(object):
    
    def __init__(self, factory):
        self._frames = []
        self._factory = factory
        
    def get(self, idx=0):
        f = None
        try:
            f = self._frames[idx]
        except:
            pass
        
        return f
    
    def put(self, frame):
        self._frames.append(frame)
        
    def dispatch(self, proto):
        self._factory.dispatch(self._frames.pop(0), proto)
        
class StompProtocol(protocol.Protocol):
    
    def setBuffer(self, size):
        self._buffer = ''
        self._buffer_size = size
        
    def dataReceived(self, data):

        if len(data) > self._buffer_size:
            pass
        elif len(data) + len(self._buffer) > self._buffer_size:
            pass
        
        for c in data:
            if c == '\0':
                self._parse(self._buffer[:] + '\0')
                self._buffer = ''
            else:
                self._buffer += c
            
    def _parse(self, _buf):
        for line in _buf.split('\n'):
            self.lineReceived(line)
            
    def lineReceived(self, line):
        #print "<-- %r" % line
        line = line.strip()
        
        # check for already processing frame
        frame = self.frameObserver.get()
        
        # if not, create a new one
        if not frame:
            if line in _stomp_frames:
                frame = StompFrame(line)
                self.frameObserver.put(frame)
            else:
                log.msg("How does that happen that we get a data(%s) outside of frame?" % line)
        else:
            # we're in a frame already, so keep parsing it
            if line == '\0':
                log.msg("frame %s(%s) ended" % (frame.getType(), frame._headers))
                self.frameObserver.dispatch(self)
            else:    
                frame.parse(line)
                
class StompFactory(protocol.ServerFactory):
    protocol = StompProtocol
    _dispatcher = dispatcher.StompServer
    
    def setDispatcher(self, dispatcherClass):
        self._dispatcher = dispatcherClass 
        
    def startFactory(self):
        #print "dispatcher" % self._dispatcher
        self.dispatcher = self._dispatcher()
        
        print self.dispatcher
        
    def dispatch(self, frame, proto):
        print "Frame: %s" % frame.getType()
        self.dispatcher.dispatch(frame, proto)
        
    def buildProtocol(self, addr):
        print "connection %s" % addr
        proto = self.protocol()
        proto.setBuffer(16384)
        proto.frameObserver = StompFrameObserver(self)
        
        return proto
