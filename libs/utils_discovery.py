#!/usr/bin/env python3
# ____________developed by paco andres_29/02/2020___________________

from gevent.server import DatagramServer
from gevent import socket
import json
import re
import inspect 
import importlib

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
    instances=[json.loads(x) for x in instances]
    interfaces={x[0]:x[1] for x in instances if "Control_Interface" not in x[0]}
    #print("get ",interfaces)
    return interfaces
    
def _Get_Control(instances):
    instances=[json.loads(x) for x in instances]
    interfaces={x[0]:x[1] for x in instances if "Control_Interface" in x[0]}
    #print("get ",interfaces)
    return interfaces

def _Get_nothing(instances):
    return []


class Discovery(object):
    def __init__(self,broadcast_port=9999,act=False,name="PYROBOT"):
        self.broadcast_port=broadcast_port
        self.name=name
        self.active_server=act
        self.client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.client.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.client.settimeout(0.2)
        self.server= DatagramServer(('', self.broadcast_port), handle=self._receive)
        if self.active_server:
            self.server.start()

    def Get(self,key):
        robot,comp,query=key.split("/")
        key="{}::{}".format(self.name,key)
        self.client.sendto(key.encode(), ("255.255.255.255", self.broadcast_port))
        #print("getting",key)
        instances=[]
        try:
           while True:
               data,address = self.client.recvfrom(buff_size)
               data=data.decode()
               #print("raw data",data)
               instances.append(data)
        except:
            pass
        return getters.get("_Get_"+query,_Get_nothing(instances))(instances)
            

    def _receive(self, key, address):
        # data sender::robot/component/required
        key=key.decode()
        sender,query=key.split("::")
        if not self.active_server:
            return False
        robot,comp,query=query.split("/")
        name=robot+"/"+comp
        name=name.replace("*",".+")
        name=name.replace("?",".+")
        if re.match(name,self.name):
            pass
            #send=senders.get("_Send_"+query,_Send_nothing(instances))(instances)
    
        
    
module=importlib.import_module("PYRobot_cli.libs.utils_discovery")
getters={name:obj for name,obj in inspect.getmembers(module,inspect.isfunction) if "_Get_" in name}
senders={name:obj for name,obj in inspect.getmembers(module,inspect.isfunction) if "_Send_" in name}
#methods={name:obj for name,obj in inspect.getmembers(Discovery,inspect.ismethod)}
#print(methods)

if __name__ == '__main__':
    pass
