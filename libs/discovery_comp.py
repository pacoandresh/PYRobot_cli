#!/usr/bin/env python3
# ____________developed by paco andres_29/02/2020___________________

from gevent.server import DatagramServer
from gevent import socket
import json
import re

buff_size=4096

class discovery(object):
    def __init__(self,discovery_port,delay=1):
        #print("port discovery ",self._etc["DISCOVERY_port"])
        self._PROC["dsc_client"] = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._PROC["dsc_client"].setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._PROC["dsc_client"].setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self._PROC["dsc_client"].settimeout(delay)
        self._etc["dsc_delay"]=delay
        self.discovery_port=discovery_port
        #print("discovery on port:",discovery_port)
        self._PROC["dsc_server"] = DatagramServer(('', self.discovery_port), handle=self._receive)
        self._PROC["dsc_server"].start()
        #print(self.__dict__)
        self._PROC["dsc_enabled"]=False
    
    def dsc_enabled(self):
        self._PROC["dsc_enabled"]=True
        
    def dsc_isenable(self):
        return self._PROC["dsc_enabled"]
    
    def dsc_disabled(self):
        self._PROC["dsc_enabled"]=False
    

    def dsc_get(self,key):
        robot,comp,query=key.split("/")
        key="{}::{}".format(self._etc["name"],key)
        self._PROC["dsc_client"].sendto(key.encode(), ("255.255.255.255", self.discovery_port))
        instances=[]
        #time.sleep(self._PROC["dsc_delay"])
        try:
           while True:
               data,address = self._PROC["dsc_client"].recvfrom(buff_size)
               data,rec_query,sender=json.loads(data.decode())
               if rec_query==query:
                   instances.append(data)
        except:
            pass
        if query=="Broker":
            inst= self._Get_Broker(instances)
            return inst
        if query=="Name":
            inst= self._Get_Name(instances)
            return inst
        if query=="Interfaces":
            inst= self._Get_Dict(instances)
            #print("send", inst)
            return inst
        if query=="InterfacesOK":
            inst= self._Get_Dict(instances)
            #print("send", inst)
            return inst
        if query=="Control":
            inst= self._Get_Dict(instances)
            #print("send", inst)
            return inst
        if query=="ControlOK":
            inst= self._Get_Dict(instances)
            #print("send", inst)
            return inst
        if query=="Running":
            inst= self._Get_Running(instances)
            #print("send", inst)
            return inst
        if query=="Topics":
            inst= self._Get_Dict(instances)
            #print("send", inst)
            return inst
        if query=="Events":
            inst= self._Get_Dict(instances)
            #print("send", inst)
            return inst
        return []

    def _receive(self, key, address):
        # data sender::robot/component/required
        key=key.decode()
        #print(key)
        sender,query=key.split("::")
        if sender==self._etc["name"]:
            return False
        if not self.dsc_isenable():
            print("{} rechazado desde {}".format(key,self._etc["name"]))
        else:     
            robot,comp,query=query.split("/")
            name=robot+"/"+comp
            name=name.replace("*",".+")
            name=name.replace("?",".+")
            if re.match(name,self._etc["name"]):
                if query=="Broker":
                    data=self._Send_Broker()
                    payload=json.dumps([data,query,self._etc["name"]])
                    self._PROC["dsc_server"].sendto(payload.encode(), address)
                if query=="Name":
                    data=self._Send_Name()
                    payload=json.dumps([data,query,self._etc["name"]])
                    self._PROC["dsc_server"].sendto(payload.encode(), address)
                if query=="Interfaces":
                    data=self._Send_Interfaces()
                    payload=json.dumps([data,query,self._etc["name"]])
                    self._PROC["dsc_server"].sendto(payload.encode(), address)
                if query=="InterfacesOK":
                    data=self._Send_InterfacesOK()
                    payload=json.dumps([data,query,self._etc["name"]])
                    self._PROC["dsc_server"].sendto(payload.encode(), address)
                if query=="Control":
                    data=self._Send_Control()
                    payload=json.dumps([data,query,self._etc["name"]])
                    self._PROC["dsc_server"].sendto(payload.encode(), address)
                if query=="ControlOK":
                    data=self._Send_ControlOK()
                    payload=json.dumps([data,query,self._etc["name"]])
                    self._PROC["dsc_server"].sendto(payload.encode(), address)               
                if query=="Running":
                    data=self._Send_Running()
                    payload=json.dumps([data,query,self._etc["name"]])
                    self._PROC["dsc_server"].sendto(payload.encode(), address)
                if query=="Topics":
                    data=self._Send_Topics()
                    payload=json.dumps([data,query,self._etc["name"]])
                    self._PROC["dsc_server"].sendto(payload.encode(), address)
                if query=="Events":
                    data=self._Send_Events()
                    payload=json.dumps([data,query,self._etc["name"]])
                    self._PROC["dsc_server"].sendto(payload.encode(), address)            
                #print("send ",key,"--",payload)
            
    def _Send_Broker(self):
        return self._etc["MQTT_uri"]
    
    def _Get_Broker(self,instances):
        broker=[x for x in instances if x!="0.0.0.0:0"]
        if len(broker)>=1:
            return broker[0]
        else:
            return "0.0.0.0:0"
    
    def _Send_Name(self):
        return self._etc["name"]
    
    def _Get_Name(self,instances):
        return instances

    def _Send_Running(self):
        if self._PROC["running"]=="RUN":
            return self._etc["name"]
        else:
            return self._PROC["running"]
    
    def _Get_Running(self,instances):
        return instances
    
    def _Send_Interfaces(self):
            #print(self._PROC["info"])
            interfaces={x[0]:x[1] for x in self._PROC["info"]}
            return interfaces
        
    def _Send_InterfacesOK(self):
        #print(self._PROC["info"])
        if self._PROC["status"]=="OK":    
            interfaces={x[0]:x[1] for x in self._PROC["info"]}
        else:
            interfaces={}
        return interfaces
          
    def _Send_Control(self):
        interfaces={x[0]:x[1] for x in self._PROC["info"] if "Control_Interface" in x[0]}
        return interfaces        
       
    def _Send_ControlOK(self):
        if self._PROC["status"]=="OK":
            interfaces={x[0]:x[1] for x in self._PROC["info"] if "Control_Interface" in x[0]}
        else:
            interfaces={}
        return interfaces        
    
    def _Get_Dict(self,instances):
        interfaces={}
        for d in instances:
            interfaces.update(d)
        #print("get ",interfaces)
        return interfaces
    
    def _Send_Topics(self):
            #print("enviado ",{k:getattr(self,k) for k,v in self._PROC["PUB"].get_topics().items()})
            #print("getss",self._PROC["PUB"].get_topics().items())
            name=self._etc["name"]+"/"
            return {name+k:getattr(self,k) for k,v in self._PROC["PUB"].get_topics().items()}

    def _Send_Events(self):
            #print("enviado ",{k:getattr(self,k) for k,v in self._PROC["PUB"].get_topics().items()})
            #print("getss",self._PROC["PUB"].get_topics().items())
            name=self._etc["name"]+"/"
            return {name+k:getattr(self,k) for k,v in self._PROC["PUB"].get_events().items()}
        

if __name__ == '__main__':
    pass