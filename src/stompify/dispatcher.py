'''
Created on Sep 30, 2011

@author: sk
'''

from stompify import subscription
class _StompFrameDispatcher(object):
    def dispatch(self, frame, proto):
        
        if hasattr(self, 'on_%s' % frame.getType()):
            m = getattr(self, 'on_%s' % frame.getType())
            m(frame, proto)
    
class StompServer(_StompFrameDispatcher):
    """
    STOMP server dispatcher. Handles server frames 
    http://stomp.github.com//stomp-specification-1.1.html
    
    @ivar _version: version protocol 
    """
    
    _subscription = subscription.SubscriptionManager
    
    _version = [1.1]        
    def __init__(self):
        
        self.submngr = self._subscription()
     
    def on_connect(self, frame, proto):
        #print "--> %s" % proto.transport.getPeer()
        _match_vers = []
        if frame.hasHeader('accept-version'):
            _vers = frame.getHeader('accept-version')
            for v in _vers:
                if float(v) in self._version:
                    _match_vers.append(v)
    
            if len(_match_vers) == 0:
                # not supported version of protocol?
                # send error frame and close the connection
                proto.sendFrame('ERROR', version=",".join(self._version))
                proto.loseConnection()
                return
        
        # we're good to go
        if len(_match_vers):
            proto.sendFrame('CONNECTED', version=max(_match_vers))
        else:
            proto.sendFrame('CONNECTED')
    
        return
    
   

    def on_disconnect(self, frame, proto):
        self.submngr.remove_by_proto(proto)
                
        proto.sendFrame('DISCONNECT')
        proto.transport.loseConnection()
        
    def on_subscribe(self, frame, proto):
        _dest = frame.getHeader('destination')
        _id = frame.getHeader('id')
        _ack = frame.getHeader('ack') or 'auto'
    
        if not _id or not _dest or not _ack:
            proto.sendFrame('ERROR', body="Missing header")
            proto.transport.loseConnection()
            
        self.submngr.add(proto, _id, _dest, _ack)
        
    def on_unsubscribe(self, frame, proto):
        _id = frame.getHeader('id')
        
        self.submngr.remove(proto, _id)
             
    def on_send(self, frame, proto):
        _dest = frame.getHeader('destination')
        _body = frame.getBody()
        
        _msg_headers = {'destination': _dest,
                        'message-id': '0xdeadbeaf'}
        
        if frame.hasBody():
            _content_type = frame.getHeader('content-type') or 'text/plain'
            _content_length = frame.getHeader('content-length') or len(frame.getBodyStr())

            _msg_headers['content-type'] = _content_type
            _msg_headers['content-length'] = _content_length

        for _id, rcpts in self.submngr.lookup(_dest).items():
            for r in rcpts:
                _ack, p = r
                _msg_headers['subscription'] = _id
            
                if frame.hasBody():
                    p.sendFrame('MESSAGE', body=frame.getBody(), **_msg_headers)
                else:
                    p.sendFrame('MESSAGE', **_msg_headers)
                
    def on_ack(self, frame, proto):
        pass
    
    def on_nack(self, frame, proto):
        pass
    
    def on_begin(self, frame, proto):
        pass
    
    def on_commit(self, frame, proto):
        pass
    
    def on_abort(self, frame, proto):
        pass

class StompClient(_StompFrameDispatcher):
    
    def on_connected(self, frame, proto):
        pass
    
    def on_message(self, frame, proto):
        pass
    
    def on_error(self, frame, proto):
        pass
    
    def on_receipt(self, frame, proto):
        pass     