'''
@author: Christian
'''
import os, time
import threading, queue
import json
import commandConfig, KeyCtl, keyConfig

class GameControlThread(threading.Thread):

    def __init__(self, inputQ, outputQ):
        super(GameControlThread, self).__init__()
        self.inputQ = inputQ
        self.outputQ = outputQ
        self.stoprequest = threading.Event()

    def run(self):
        # As long as we weren't asked to stop, try to take new tasks from the
        # queue. The tasks are taken with a blocking 'get', so no CPU
        # cycles are wasted while waiting.
        # Also, 'get' is given a timeout, so stoprequest is always checked,
        # even if there's nothing in the queue.
        while not self.stoprequest.isSet():
            try:
                message = self.inputQ.get(True, 0.05)
                self.executeMessage(message)
            except queue.Empty:
                continue

    def join(self, timeout=None):
        self.stoprequest.set()
        super(GameControlThread, self).join(timeout)

    def executeMessage(self, message):
        sm = json.loads(message)['message']
        if sm in commandConfig.commands.keys():
            KeyCtl.sendImmediateKeystroke(commandConfig.commands[sm])