'''
Created on Sep 30, 2011

@author: sk
'''

from twisted.python import log

from twisted.internet import defer
from stompify import subscription, transaction

import uuid

class _StompFrameDispatcher(object):
    def dispatch(self, frame, proto):
        
        if hasattr(self, 'on_%s' % frame.getType()):
            m = getattr(self, 'on_%s' % frame.getType())
            m(frame, proto)
            
            if frame.getHeader('receipt'):
                proto.sendFrame('RECEIPT', **{'receipt-id': frame.getHeader('receipt')})

    def onStart(self, defer):
        self._start = defer
        
    def connected(self, proto, start_defer):
        pass
    
    def cleanup(self, proto):
        """
        Handles connection lost, do all necessary cleanup for specified proto (i.e. not ack messages etc.)
        """
        
class StompServer(_StompFrameDispatcher):
    """
    STOMP server dispatcher. Handles server frames 
    http://stomp.github.com//stomp-specification-1.1.html
    
    @ivar _version: version protocol 
    """
    
    _subscription = subscription.SubscriptionManager
    _transaction = transaction.TransactionManager
    
    _version = [1.1]        
    def __init__(self):
        
        self.submngr = self._subscription()
        # ack queue
        self._ack = {}
        self.trans = self._transaction()
        
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
        _trans = frame.getHeader('transaction')
        _body = frame.getBody()
        
        _msg_headers = {'destination': _dest}
                        
        
        if _trans:
            self.trans.add(_trans, frame)
            
        if frame.hasBody():
            _content_type = frame.getHeader('content-type') or 'text/plain'
            _content_length = frame.getHeader('content-length') or len(frame.getBodyStr())

            _msg_headers['content-type'] = _content_type
            _msg_headers['content-length'] = _content_length

        for _id, rcpts in self.submngr.lookup(_dest).items():
            for r in rcpts:
                p = r.getProto()
                _msg_headers['message-id'] = r.messageId()
                _msg_headers['subscription'] = _id
            
                if frame.hasBody():
                    p.sendFrame('MESSAGE', body=frame.getBody(), **_msg_headers)
                else:
                    p.sendFrame('MESSAGE', **_msg_headers)
                
                if r.getAck() == 'client':
                    self._ack[_msg_headers['message_id']] = (p, frame)
                    
    def on_ack(self, frame, proto):
        _message_id = frame.getHeader('message-id')
        _subId = frame.getHeader('subscription')
        _trans = frame.getHedaer('transaction')
        _sub, _frame = self._ack.get(_message_id)
        
        if _sub and _subId:
            if _sub.getId() == _subId: 
                log.msg("Message(%s) acknowledged" % _message_id)
                del self._ack[_message_id]
            
    def on_nack(self, frame, proto):
        pass
    
    def on_begin(self, frame, proto):
        _trans = frame.getHeader('transaction')
        if _trans:
            self.trans.begin(_trans)
            self.trans.add(_trans, frame)
            
    def on_commit(self, frame, proto):
        _trans = frame.getHeader('transaction')
        if _trans:
            self.trans.add(_trans, frame)
            self.trans.commit(_trans)
    
    def on_abort(self, frame, proto):
        _trans = frame.getHeader('transaction')
        if _trans:
            self.trans.abort(_trans)

class StompClient(_StompFrameDispatcher):
    
    def __init__(self):
        self._started = False
        self._proto = None
        
    def connected(self, proto, start_defer):
        self._proto = proto
        proto.sendFrame('CONNECT', version='1.1')
        self.start_defer = start_defer
        
    def on_connected(self, frame, proto):
        self._started = True
        self.start_defer.callback(self)
        
    def on_message(self, frame, proto):
        pass
    
    def on_error(self, frame, proto):
        if not self._started:
            self.start_defer.errback(self)
            
    def on_receipt(self, frame, proto):
        pass
    
    def subscribe(self, _dest, _ack='auto'):
        _id = str(uuid.uuid4())
        self._proto.sendFrame('SUBSCRIBE', ack=_ack, destination=_dest, id=_id)
    
        return _id
    
    def unsubscribe(self, _id):
        self._proto.sendFrame('UNSUBSCRIBE', id=_id)
    
    def send(self, body=None, **headers):
        if body:
            self._proto.sendFrame('SEND', body=body, **headers)
        else:
            self._proto.sendFrame('SEND', **headers)
    
    def _ack_nack(self, _type, _sub, _messageId, _trans=None):
        _headers = {'subscription': _sub, 'message-id': _messageId}
        if _trans:
            _headers['transaction'] = _trans
            
        self._proto.sendFrame(type, **_headers)
    
    def ack(self, _sub, _messageId, _trans):
        self._ack_nack('ACK', _sub, _messageId, _trans)
        
    def nack(self, _sub, _messageId, _trans):
        self._ack_nack('NACK', _sub, _messageId, _trans)
    
    def begin(self):
        _trans = str(uuid.uuid4())
        self._proto.sendFrame('BEGIN', transaction=_trans)
    
        return _trans
    
    def commit(self, _trans):
        self._proto.sendFrame('COMMIT', transaction=_trans)
    
    def abort(self, _trans):
        self._proto.sendFrame('ABORT', transaction=_trans)
         
    def disconnect(self, _receipt=None):
        if _receipt:
            self._proto.sendFrame('DISCONNECT', receipt=_receipt)
        else:
            self._proto.sendFrame('DISCONNECT')