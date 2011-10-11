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

    def __repr__(self):
        return repr("type:%s, headers:%s" % (self._frame, self._headers))
    
    def toWire(self):
        """
        converts object to STOMP frame ready to send on wire
        """
        _frame = []
        _frame.append(self.getType().upper())
        for k,v in self._headers.items():
            _frame.append("%s:%s" % (k, v))
            
        _frame.append('\n')
        _frame.append(''.join(self._body))
        _frame.append('\0')
        
        _to_wire = '\n'.join(_frame)
    
        return _to_wire
    
    def parse(self, raw_line):
        if self._in_header:
            if raw_line.find(':') > 0:
                header, value = raw_line.split(':')
            
                self.setHeader(header, value)
            elif raw_line == '':
                self._in_header = False
        else:
            self._body.append(raw_line)
      
    def hasHeader(self, header):
        return self._headers.has_key(header)
          
    def setHeader(self, header, value):
        self._headers[header] = value
        
    def getHeader(self, header):
        return self._headers.get(header)
    
    def setType(self, frame_type):
        self._frame = frame_type.lower()
        
    def getType(self):
        return self._frame
    
    def setBody(self, body):
        self._body = body
     
    def hasBody(self):
        return len(self._body)
       
    def getBody(self):
        return self._body
    
    def getBodyStr(self):
        return '\n'.join(self._body)
    
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
       
    def connected(self, proto):
        self._factory.connected(proto)
         
    def dispatch(self, proto):
        #print "frames %s" % self._frames
        self._factory.dispatch(self._frames.pop(0), proto)
        
    def cleanup(self, proto):
        self._factory.cleanup(proto)
            
class StompProtocol(protocol.Protocol):
    
    def connectionMade(self):
        self.frameObserver.connected(self)
        
    def sendFrame(self, frame_type, body=None, **headers):
        
        _frame = StompFrame(frame_type)
        for k,v in headers.items():
            _frame.setHeader(k, v)
            
        if body:
            _frame.setBody(body)
            
        self.transport.write(_frame.toWire())
        
    def setBuffer(self, size):
        self._buffer = ''
        self._buffer_size = size
        
    def dataReceived(self, data):
        #print "<--- %r" % repr(data)
        
        if len(data) > self._buffer_size:
            pass
        elif len(data) + len(self._buffer) > self._buffer_size:
            pass
        
        for c in data:
            if c == '\0':
                self._parse(self._buffer[:] + '\n\0')
                self._buffer = ''
            else:
                self._buffer += c
            
    def _parse(self, _buf):
        #print "<-- line %r" % repr(_buf)
         
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
                
    def connectionLost(self, reason):
        self.frameObserver.cleanup(self)
                    
class StompFactory(protocol.Factory):
    protocol = StompProtocol
    _dispatcher = dispatcher.StompServer
    _start = None
        
    def setDispatcher(self, dispatcherClass, start_defer):
        self._dispatcher = dispatcherClass 
        self._start = start_defer
        
    def startFactory(self):
        #print "dispatcher" % self._dispatcher
        self.dispatcher = self._dispatcher()
        self.dispatcher.onStart(self._start)
        
        print self.dispatcher
        
        #self._defer.callback(self.dispatcher)
        
    def connected(self, proto):
        self.dispatcher.connected(proto, self._start)
        
    def cleanup(self, proto):
        self.dispatcher.cleanup(proto)
        
    def dispatch(self, frame, proto):
        print "Frame: %s" % frame.getType()
        self.dispatcher.dispatch(frame, proto)
        
    def buildProtocol(self, addr):
        print "connection %s" % addr
        proto = self.protocol()
        proto.setBuffer(16384)
        proto.frameObserver = StompFrameObserver(self)
        
        return proto

class StomServerFactory(StompFactory, protocol.ServerFactory):
    pass

class StompClientFactory(StompFactory, protocol.ClientFactory):
    pass
