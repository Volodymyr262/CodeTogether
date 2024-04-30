from time import sleep

from channels.generic.websocket import WebsocketConsumer
import json
from random import randint


class WSConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()
        for i in range(1000):
            self.send(json.dumps({'message': randint(1, 100)}))
            sleep(1)