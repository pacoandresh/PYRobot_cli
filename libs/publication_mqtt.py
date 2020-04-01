#!/usr/bin/env python3
# ____________developed by paco andres_15/04/2019___________________

import time
import paho.mqtt.publish as pub
from  threading import Thread
from PYRobot_cli.libs.utils import get_ip_port
from PYRobot_cli.libs.botlogging.coloramadefs import P_Log
import json
from deepdiff import DeepDiff

time_Max_interval=2

class Publication(object):

    def __init__(self,component,mqtt_uri,obj,sync=True,frec=0.1,qos=0):
        self._host,self._port=get_ip_port(mqtt_uri)
        if len(component.split("/"))==2:
            self._robot,self._comp=component.split("/")
        else:
            self._robot="ALL"
            self._comp=component
        self._qos=qos
        self.topics=set()
        self.topics_last={}
        self.time_last=time.time()
        self.time_last_events=time.time()
        self.events={}
        self.events_last={}
        self.sync=sync
        self.obj=obj
        self.frec=frec
        self.work=True
        self.pre= str(component) + "/"
        self.pre_events=self._robot+"/events/"+self._comp+"/"

    def add_topics(self,*topics):
        for n in topics:
            if hasattr(self.obj,n):
                self.topics.add(n)
                self.topics_last[n]={}
            else:
                P_Log("{} not registered".format(n))

    def get_topics(self):
        return list(self.topics)

    def get_events(self):
        return [x for x in self.events]

    def add_event(self,entity,event):
        try:
            name,fn=event.split("::")
            self.events.setdefault(entity,[])
            fn=fn.replace("self.","self.obj.")
            self.events[entity].append((name,fn))
            self.events_last[entity]=[]
            #print("Pub events",self.events)
        except:
            P_Log("error loading {}".format(event))

    def check(self,fn):
        try:
            return eval(fn)
        except Exception as ex:
            #print(str(ex))
            return "ERR"

    def Pub_topics(self,remember=False):
        nowtime=time.time()
        sal={self.pre+n:getattr(self.obj,n) for n in self.topics if
                DeepDiff(self.topics_last[n],getattr(self.obj,n))!={}}
        self.topics_last={n:getattr(self.obj,n) for n in self.topics}
        if len(sal)>0:
            self.time_last=nowtime
            for topic,data in sal.items():
                payload_value =json.dumps([data,"V",nowtime])
                #print("publication",topic,payload_value)
                pub.single(topic,payload_value, hostname=self._host, port=self._port,qos=self._qos,retain=False)
        elif remember and (nowtime-self.time_last)>time_Max_interval:
            self.time_last=nowtime
            #print(self.time_last,self.topics_last)
            for topic,data in self.topics_last.items():
                payload_value =json.dumps([data,"V",nowtime])
                #print("publication on time",self.pre+topic,payload_value)
                pub.single(self.pre+topic,payload_value, hostname=self._host, port=self._port,qos=self._qos,retain=False)

    def Pub_events(self,remember=False):
        # todo if no events what happend
        nowtime=time.time()
        events_sal={}
        for entity,events in self.events.items():
            send_events=[k for k,v in events if self.check(v)==True]
            if DeepDiff(send_events,self.events_last[entity])!={}:
                events_sal[self.pre_events+entity]=send_events
                self.events_last[entity]=send_events
        if len(events_sal)>0:
            self.time_last_events=nowtime
            for topic,data in events_sal.items():
                payload_value =json.dumps([data,"E",time.time()])
                #print("event",topic,payload_value)
                pub.single(topic,payload_value, hostname=self._host, port=self._port,qos=self._qos,retain=False)
        elif remember and (nowtime-self.time_last_events)>time_Max_interval:
            self.time_last_events=nowtime
            for topic,data in self.events_last.items():
                payload_value =json.dumps([data,"E",time.time()])
                #print("event on time",self.pre_events+topic,payload_value)
                pub.single(self.pre_events+topic,payload_value, hostname=self._host, port=self._port,qos=self._qos,retain=False)


    def Public(self,remember=False):
        if not self.sync:
            self.Pub_topics(remember)
            self.Pub_events(remember)
        else:
            P_Log("[FB]<{}/{}>[FW] Mode syncronous activated".format(self._robot,self._comp))

    def _Do_Pub(self):
        while self.work:
            self.Pub_topics(remember=False)
            self.Pub_events(remember=False)
            time.sleep(self.frec)

    def stop(self):
        self.work=False

    def change_frec(self,frec):
        if frec>0:
            self.frec=frec

    def start(self):
        if self.sync:
            self.work=True
            self.thread=Thread(target=self._Do_Pub,name=self._comp+":PUB")
            self.thread.setDaemon(True)
            self.thread.start()
        else:
            P_Log("[FB]<{}/{}>[FW] Mode Asyncronous activated".format(self._robot,self._comp))
