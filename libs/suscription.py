#!/usr/bin/env python3
# ____________developed by paco andres_15/04/2019___________________


import time
from  threading import Thread
from PYRobot_cli.utils.utils import get_ip_port
from PYRobot_cli.libs.comunications import Mqtt_Sub,Broadcast_Sub
import json


class Suscriptions(object):
    def __init__(self,name,mqtt_uri,broadcast,mqtt_handler,broad_handler,qos=0):
        self.host,self.mqtt_port=get_ip_port(mqtt_uri)
        self.qos=0
        self.broadcast_port=broadcast
        self.robot,self.comp=name.split("/")
        self.suscribers={}
        self.first=[]
        self.mqtt = Mqtt_Sub(self.host,self.mqtt_port,mqtt_handler,self.qos)
        self.broadcast=Broadcast_Sub(self.host,self.broadcast_port,on_handler=broad_handler,qos=self.qos)

    def add_suscribers(self,**suscriptions):
        for s,l in suscriptions.items():
            self.add_suscriber(l,s)

    def add_suscriber(self,suscriber,link):
        self.suscribers[suscriber]=link
        self.first.append(suscriber)
        self.mqtt.connect(self.suscribers)
    
    def del_first(self,suscriber):
        if suscriber in self.first:
            self.first.remove(suscriber)

    def get_first(self):
        return self.first
    
    def get_suscribers(self):
        return self.suscribers


    
