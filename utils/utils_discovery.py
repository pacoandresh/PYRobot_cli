#!/usr/bin/env python3
# ____________developed by paco andres_29/02/2020___________________

from gevent.server import DatagramServer
from gevent import socket
import json
import re
import inspect 
import importlib
import time

buff_size=4096

def _Get_Broker(instances):
    broker=[x for x in instances if x!="0.0.0.0:0"]
    if len(broker)>=1:
        return broker[0]
    else:
        return "0.0.0.0:0"
    
def _Get_Name(instances):
    return instances
    
def _Get_Running(instances):
    return instances
    
def _Get_Interfaces(instances):
    interfaces={}
    for d in instances:
        interfaces.update(d)
    #print("get ",interfaces)
    return interfaces

def _Get_InterfacesOK(instances):
    interfaces={}
    for d in instances:
        interfaces.update(d)
    #print("get ",interfaces)
    return interfaces
    
def _Get_Control(instances):
    interfaces={}
    for d in instances:
        interfaces.update(d)
    #print("get ",interfaces)
    return interfaces

def _Get_ControlOK(instances):
        interfaces={}
        for d in instances:
            interfaces.update(d)
        #print("get ",interfaces)
        return interfaces

def _Get_Topics(instances):
    interfaces={}
    for d in instances:
        interfaces.update(d)
    #print("get ",interfaces)
    return interfaces

def _Get_Events(instances):
    interfaces={}
    for d in instances:
        interfaces.update(d)
    #print("get ",interfaces)
    return interfaces

def _Get_nothing(instances):
    return []


class Discovery(object):
    def __init__(self,discovery_port=9000,act=False,name="PYROBOT",delay=1):
        self.discovery_port=discovery_port
        self.name=name
        self.delay=delay
        self.active_server=act
        self.client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.client.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.client.settimeout(delay)
        #print("utils discovery port",self.discovery_port)
        self.server= DatagramServer(('', self.discovery_port), handle=self._receive)
        if self.active_server:
            self.server.start()

    def Get(self,key):
        #print("key ",key)
        robot,comp,query=key.split("/")
        key="{}::{}".format(self.name,key)
        self.client.sendto(key.encode(), ("255.255.255.255", self.discovery_port))
        #time.sleep(self.delay)
        instances=[]
        try:
           while True:
               data,address = self.client.recvfrom(buff_size)
               data,rec_query,sender=json.loads(data.decode())
               if rec_query==query:
                   instances.append(data)
        except:
            pass
        return getters["_Get_"+query](instances)
            

    def _receive(self, key, address):
        pass
    
        
    
module=importlib.import_module("PYRobot_cli.utils.utils_discovery")
getters={name:obj for name,obj in inspect.getmembers(module,inspect.isfunction) if "_Get_" in name}
senders={name:obj for name,obj in inspect.getmembers(module,inspect.isfunction) if "_Send_" in name}
#print(classes)

if __name__ == '__main__':
    pass
