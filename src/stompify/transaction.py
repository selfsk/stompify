class Transaction(object):
    
    def __init__(self, proto, _transId):
        self._id = _transId
        self._frames = []
        
    def getId(self):
        return self._id
    
    def addFrame(self, _frame):
        self._frames.append(_frame)
        
        
class TransactionManager(object):
    
    def __init__(self):
        self._trans = {}
        
        
    def begin(self, trans):
        self._trans[trans.getId()] = trans
        
    def add(self, transId, frame):
        self._trans[transId].addFrame(frame)
        
    def commit(self, transId):
        self._trans[transId].addFrame(None)
        
    def abort(self, transId):
        del self._trans[transId]