#!/usr/bin/env python3
# ____________developed by paco andres_15/04/2019___________________

from PYRobot_cli.libs.proxy import Proxy
from PYRobot_cli.botlogging.botlogging import Logging
from PYRobot_cli.libs.suscription import Suscriptions
from PYRobot_cli.utils.utils_discovery import Discovery
from PYRobot_cli.utils.utils import get_host_name
import json

discovery_port=9000
broadcast_port=9999
hostname=get_host_name()

class Client(Logging):
    def __init__(self,discovery_port=discovery_port,broadcast_port=broadcast_port,delay=0.3):
        self._etc={}
        self._PROC={}
        self._etc["name"]="PYR_"+hostname
        self._etc["delay"]=delay
        self.discovery_port=discovery_port
        self.broadcast_port=broadcast_port
        self._PROC["handlers"]={}
        self.dsc=Discovery(discovery_port=self.discovery_port,delay=delay)
        super().__init__(level=50)

    def Connect_Robot(self,robot):
        robots=self.Available_Robots(show=False)      
        if robot in robots:
            self._etc["name"]=robot
            self._etc["BROADCAST_PORT"]=self.broadcast_port
            self.robot=robot
            self._etc["BROKER"]=self.dsc.Get(self.robot+"/*/Broker")
            self._PROC["SUS"]=Suscriptions(robot+"/client",self._etc["BROKER"],self.broadcast_port,self._Handler_Mqtt,self._Handler_Broadcast)
            topics=self.dsc.Get(self.robot+"/*/Topics")
            self._etc["EVENTS"]=self.dsc.Get(self.robot+"/*/Events")
            self._etc["TOPICS"]={k:v for k,v in topics.items() if k not in self._etc["EVENTS"]}
            interfaces=self.dsc.Get(self.robot+"/*/InterfacesOK")
            self._etc["INTERFACES"]={k:v for k,v in interfaces.items() if k.find("/Control_Interface")==-1}
            self._etc["CONTROLS"]={k:v for k,v in interfaces.items() if k.find("/Control_Interface")!=-1}
            self.L_info("Robot Connected")          
        else:
            self.L_error("Robot not is on line")
            exit()
                
    def Available_Robots(self,show=True):
        get=self.dsc.Get("*/*/Name")
        robots={}
        for x in get:
            r,c=x.split("/")
            if r!="PYRobot":
                if r not in robots:
                    robots[r]=[]
                robots[r].append(c)
        if show:
            if len(robots)>0:  
                self.L_print("[FY] Available Robots:")
                for r in robots:
                    self.L_print("\t[FY]Robot: [FW]{} [FY]".format(r))
            else:
                self.L_print("There are not Robots")
        self.L_print("")
        return robots              

    def _check_connectors(self,topics):
        if isinstance(topics,dict):
            CONNECTORS={}
            for k,v in topics.items():
                if len(v.split("/"))==2:
                    CONNECTORS[k]="{}/{}".format(self._etc["name"],v)
                if len(v.split("/"))==1:
                    self.L_error("Topic {} not found".format(k))
                    exit()
        
        if isinstance(topics,list) or isinstance(topics,tuple):
            CONNECTORS=[]
            for t in topics:
                if len(t.split("/"))==2:
                    CONNECTORS.append("{}/{}".format(self._etc["name"],t))
                if len(t.split("/"))==3:
                    CONNECTORS.append(t)
                if len(t.split("/"))==1:
                    self.L_error("Topic {} not found".format(t))
                    exit()
            CONNECTORS={v.split("/")[2]:v for v in CONNECTORS}
        return CONNECTORS
            
    def INTERFACES_list(self,*interfaces):
        INTERFACES=self._check_connectors(interfaces)
        self._CONNECT_INTEFACES(**INTERFACES)
    
    def INTERFACES(self,**interfaces):
        INTERFACES=self._check_connectors(interfaces)
        self._CONNECT_INTERFACES(**INTERFACES)        
        
    def TOPICS_list(self,*topics):
        TOPICS=self._check_connectors(topics)
        self._SUS_TOPICS("TOPICS",**TOPICS)
    
    def TOPICS(self,**topics):
        TOPICS=self._check_connectors(topics)
        self._SUS_TOPICS("TOPICS",**TOPICS)
        
    def EVENTS_list(self,*topics):
        TOPICS=self._check_connectors(topics)
        self._SUS_TOPICS("EVENTS",**TOPICS)
    
    def EVENTS(self,**topics):
        TOPICS=self._check_connectors(topics)
        self._SUS_TOPICS("EVENTS",**TOPICS)
                       
    def _SUS_TOPICS(self,tipe,**topics):
        available=self._etc[tipe]
        TOPICS={}
        for t,v in topics.items():
            if v in available:
                robot,comp,topic=v.split("/")
                setattr(self,t,available[v])
                TOPICS[t]=v
            else:
                self.L_warning("{} {} Not Found".format(tipe,t))
                setattr(self,t,None)
        self._PROC["SUS"].add_suscribers(**TOPICS)
        self.L_info("{} {} Subcripted".format(tipe,",".join(topics)))

    def _CONNECT_INTERFACES(self,**interfaces):
        robot=self._etc["name"]
        available=self._etc["INTERFACES"]
        for attr,connector in interfaces.items():
            if connector in available:
                uri=available[connector]
                proxy=Proxy(uri)
                if proxy():
                    setattr(self,attr,proxy)
                    self.L_info("{} Connected".format(attr,uri))
                else:
                    self.L_warning("Conneting {} on {}".format(attr,uri))
                    setattr(self,attr,proxy)
            else:
                self.L_warning("{} Not Found".format(connector))
                setattr(self,attr,None)
 

    def add_HANDLER(self,handler):
        name=handler.__name__
        if len(name.split("_"))==4:
            _,on,event,activator=name.split("_")
            if on!="on" or event not in self._PROC["SUS"].get_suscribers().values():
                self.L_error("{} handler name incorrect".format(name))
            else:
                self._PROC["handlers"][name]=handler
        else:
            self.L_error("{} handler name incorrect".format(name))
        print(self._PROC["handlers"])
        

    def show_info(self):
        self.L_print("Showing info from [FY]{}".format(self._etc["name"]))
        self.L_print("\t [FY]Available INTERFACES:")
        for inter in self._etc["INTERFACES"]:
            r,c,t=inter.split("/")
            self.L_print("\t\t {}/{}".format(c,t))
        self.L_print("\t [FY]Available PUB TOPICS:")
        for topic in self._etc["TOPICS"]:
            r,c,t=topic.split("/")
            self.L_print("\t\t {}/{}".format(c,t))
        self.L_print("\t [FY]Available EVENTS:")
        for event in self._etc["EVENTS"]:
            r,c,t=event.split("/")
            self.L_print("\t\t {}/{}".format(c,t))
        self.L_print("\t [FY]MQTT BROKER:[FW]{}".format(self._etc["BROKER"]))
        self.L_print("")
        
    def _Handler_Broadcast(self, payload, address):
        payload,tipe,date=json.loads(payload.decode())
        if self._etc["name"] not in payload:
            #print("BR RECEIVE {}    {} {} {}".format(self._etc["name"],payload,tipe,date))
            suscriber="{}/{}".format(payload[0],payload[1])
            data=payload[2]
            self._PROC["SUS"].del_first(suscriber)
            if suscriber in self._PROC["SUS"].suscribers:
                link=self._PROC["SUS"].suscribers[suscriber]
                setattr(self,link,data)
            if tipe=="EVENTS":
                attr=payload[1]
                #print("EVENT",data,attr,link)
                for ev in data:
                    try:
                        func=self._PROC["handlers"]["_on_{}_{}".format(link,ev)]
                        print("eject",func)
                        func()
                    except:
                        pass
    
    def _Handler_Mqtt(self,client, userdata, msg):
        data,tipe,date=json.loads(msg.payload.decode())
        payload={msg.topic:data}
        #print("MQ REC {}  _______________{} {} {}".format(self._etc["name"],payload,tipe,date))
        r,c,attr=msg.topic.split("/")
        self._PROC["SUS"].del_first(msg.topic)
        if msg.topic in self._PROC["SUS"].suscribers:
            setattr(self,self._PROC["SUS"].suscribers[msg.topic],data)
        if tipe=="EVENTS":
            print(data)
            for ev in data:
                try:
                    func="self.on_{}_{}()".format(attr,ev)
                    eval(func)
                except:
                    #print("err",func)
                    pass
                    
    
    def _Handler_multicast(self, payload, address):
        print("multi: ",payload)

