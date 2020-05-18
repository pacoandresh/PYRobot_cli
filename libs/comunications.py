
from gevent import socket
from gevent import Timeout
from gevent import monkey
import paho.mqtt.publish as pub
import paho.mqtt.client as mqtt
from gevent.server import DatagramServer
import time
monkey.patch_all(thread=False)
import json

class Mqtt_Pub(object):
    def __init__(self,host,port,qos=0,retain=False):
        self.host=host
        self.port=port
        self.qos=qos
        self.retain=retain

    def pub(self,topic,data,data_type="TOPICS"):
        payload =json.dumps([data,data_type,time.time()])
        #print("Mqtt: ",topic,payload)
        pub.single(topic,payload, hostname=self.host, port=self.port,qos=self.qos,retain=self.retain)
        
class Broadcast_Pub(object):
    def __init__(self,port):
        self.broad_host = '255.255.255.255'
        self.port=port
        self.client=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.client.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    def pub(self,topic,data,data_type="TOPICS"):
        robot,comp,topic=topic.split("/")
        data=[robot+"/"+comp,topic,data]
        payload =json.dumps([data,data_type,time.time()])
        #print("broadcast:",topic,payload)
        self.client.sendto(payload.encode(), (self.broad_host,self.port))
        
class Mqtt_Sub(object):
    def __init__(self,host,port,on_handler,qos=0):
        self.host=host
        self.port=port
        self.qos=qos
        self.client = mqtt.Client()
        self.client.on_message=on_handler
        self.client.connect(host=self.host, port=self.port, keepalive=60)
        self.client.loop_start()

    def connect(self,proxys):
        topics=[(proxy,self.qos) for proxy in proxys]
        #events=[(proxy,self.qos) for proxy in self.events]
        self.client.subscribe(topic=topics)

    # def loop(self):
    #     self.client.loop()


class Broadcast_Sub(object):
    def __init__(self,host,port,on_handler,qos=0):
        self.host=host
        self.port=port
        self.qos=qos
        self.bcast = DatagramServer(('', self.port), handle=on_handler)
        self.bcast.start()
        
    def receive(self, data, address):
        value=json.loads(data.decode())
        payload,type,date=json.loads(data.decode())
