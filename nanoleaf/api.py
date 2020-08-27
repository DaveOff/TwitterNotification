import requests
import json
from time import sleep

class nanoleaf2twitter:

    def __init__(self, ip, token):
        self.ip = ip
        self.token = token
        response = self.request(method='get', path='', data=None)
        if response.status_code != 200:  raise Exception("[Init] Nanoleaf Auth Error!")

    def run(self):
        self.setRGB()
        self.turnOn()
        sleep(1)
        self.turnOff()

    def setRGB(self):
        self.request(method='put', path='state', data={"sat" : {"value": 88}, 'brightness': {'value': 94}, 'hue': {'value': 200}})

    def turnOff(self):
        self.request(method='put', path='state', data={'on': {'value': False}})

    def turnOn(self):
        self.request(method='put', path='state', data={'on': {'value': True}})

    def request(self, method, path, data):
        headers = None
        if data is not None:
            data = json.dumps(data)
            headers = {
                'Content-Type': 'application/json',
                'Content-Length': str(len(data))
            }
        func = getattr(requests, method)
        response = func('http://'+self.ip+':16021/api/v1/'+self.token+'/'+path, data=data, headers=headers)
        return response
