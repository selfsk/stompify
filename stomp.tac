from twisted.application import service
from stompify import app, dispatcher

    
application = service.Application('stomp')
stomp = app.StompService()
#stomp.setDispatcher(dispatcher.StompClient)
stomp.setServiceParent(application)

