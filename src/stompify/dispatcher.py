'''
Created on Sep 30, 2011

@author: sk
'''

class _StompFrameDispatcher(object):
    def dispatch(self, frame, proto):
        
        if hasattr(self, 'on_%s' % frame.getType()):
            m = getattr(self, 'on_%s' % frame.getType())
            m(frame, proto)
    
class StompServer(_StompFrameDispatcher):
            
    def on_connect(self, frame, proto):
        pass
    
    def on_disconnect(self, frame, proto):
        pass
    
    def on_subscribe(self, frame, proto):
        pass
    
    def on_unsubscribe(self, frame, proto):
        pass
    
    def on_send(self, frame, proto):
        pass
    
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