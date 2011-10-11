from twisted.application import service
from stompify import app, dispatcher

    
application = service.Application('stomp')
stomp = app.StompClientService()
stomp.start().addCallback(lambda dispatcher: dispatcher.subscribe('/queue/temp'))

stomp.setServiceParent(application)

