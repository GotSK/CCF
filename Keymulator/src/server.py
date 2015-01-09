'''
@author: Christian
'''
import KeyCtl

import tornado.ioloop
import tornado.web
import tornado.websocket
import os
import json

from tornado.options import define, options, parse_command_line
import commandConfig
import queue
import GameControlThread
from threading import Thread
define("port", default=8888, help="run on the given port", type=int)

clientId = 0
clients = []
clientById = {}
idByClient = {}

votingOptions =["Mob", "Majority Vote"]
controlInputQueue = queue.Queue()
controlOutputQueue = queue.Queue()

gameControl = GameControlThread.GameControlThread(controlInputQueue, controlOutputQueue)
gameControl.start()
class IndexHandler(tornado.web.RequestHandler):
  @tornado.web.asynchronous
  def get(self):
    self.render("index.html")
  def check_origin(self, origin):
    return True

class WebSocketChatHandler(tornado.websocket.WebSocketHandler):
    
    
  def open(self, *args):
    global clientId
    print("open", "WebSocketChatHandler")
    clients.append(self)
    clientById[clientId] = self
    idByClient[self] = clientId
    clientId += 1
    
    for vote in votingOptions:
        self.write_message(json.dumps({'type':'voteOption', 'message':vote, 'author':'[SYSTEM]'}))

  def on_message(self, message):        
    print (message)
    #KeyCtl.test()
    print (json.loads(message)['message'])
    print (idByClient[self] )
    if json.loads(message)['type']=='chatMsg' or json.loads(message)['type'] == 'keystroke':
        controlInputQueue.put(message)
    
    for client in clients:
          client.write_message(message)
        
  def on_close(self):
      clients.remove(self)
  def check_origin(self, origin):
    return True

#app = tornado.web.Application([(r'/chat', WebSocketChatHandler), (r'/', IndexHandler)])
settings = {
    "static_path": os.path.dirname(__file__)
}
app = tornado.web.Application([
(r'/', IndexHandler),
(r'/ws', WebSocketChatHandler),
], **settings)

#print(os.path.join(os.path.dirname(__file__), "static"))
      
app.listen(options.port)
tornado.ioloop.IOLoop.instance().start()