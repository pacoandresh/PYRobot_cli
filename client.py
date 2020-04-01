#!/usr/bin/env python3
# ____________developed by paco andres_15/04/2019___________________

from PYRobot_cli.libs.proxy import Proxy
from PYRobot_cli.libs.botlogging.botlogging import Logging
from PYRobot_cli.libs.subscription_mqtt import subscriptions
from PYRobot_cli.libs.utils_discovery import Discovery

broadcast_port=9999

class Client(Logging):
    def __init__(self,broadcast=broadcast_port):
        self._etc={}
        self._PROC={}
        self._etc["name"]="PYRobot"
        self.broadcast=broadcast_port
        self._PROC["event_handlers"]={}
        self.dsc=Discovery(broadcast_port=self.broadcast)
        super().__init__(level=50)

        
            
    def Connect_Robot(self,robot):
        robots=self.Available_Robots(show=False)
        
        if robot in robots:
            self._etc["name"]=robot
            self._etc["TOPICS"]=[]
            self._etc["EMIT_TOPICS"]=[]
            self._etc["SERVICES"]={}
            self._etc["CONTROLS"]={}
            self._etc["EVENTS"]=[]
            self._etc["EMIT_EVENTS"]=[]
            self.robot=robot
            self._etc["BROKER"]=self.dsc.Get(self.robot+"/*/Broker")
            self._PROC["SUB"]=subscriptions(robot+"/client",self._etc["BROKER"],self)
            controls=self.dsc.Get(self.robot+"/*/Control")
            for c,uri in controls.items():
                proxy=Proxy(uri)
                if proxy():
                    data=proxy.Get_INFO()
                    robot,comp=data["_etc"]["name"].split("/")
                    for s in data["_PROC"]["info"]:
                        if "Control_Interface" not in s[0]:
                            self._etc["SERVICES"][s[0]]=s[1]
                        else:
                            self._etc["CONTROLS"][s[0]]=s[1]
                    for s in data["_PROC"]["PUB"]:
                        self._etc["TOPICS"].append(robot+"/"+comp+"/"+s)
                    for s in data["_PROC"]["EMIT"]:
                        self._etc["EMIT_TOPICS"].append(robot+"/"+comp+"/"+s)
                    for s in data["_PROC"]["PUB_EVENT"]:
                        self._etc["EVENTS"].append(robot+"/"+comp+"/"+s)
                    for s in data["_PROC"]["EMIT_EVENT"]:
                        self._etc["EMIT_EVENTS"].append(robot+"/"+comp+"/"+s)    
            
            self.L_info("Robot Connected")          
        else:
            self.L_error("Robot not is on line")
            exit()
        
    
    
                
    def Available_Robots(self,show=True):
        get=self.dsc.Get("*/*/Running")
        robots={}
        for x in get:
            r,c=x.split("/")
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
        
    def connect(self):
        self._PROC["SUB"].connect()

    def close(self):
        self._PROC["SUB"].stop()
        try:
            for I in self._etc["SERVICES"]:
                s=getattr(self,I)
                s._close()
        except:
            raise
            self.L_error("{} Error stoping".format(I))


    def SERVICES(self,**services):
        if "name" in self._etc:
           robot=self._etc["name"]
           available=self._etc["SERVICES"]
           for item,service in services.items():
               service="{}/{}".format(self._etc["name"],service)
               if service in available:
                   uri=available[service]
                   if uri!="0.0.0.0:0":
                       proxy=Proxy(uri)
                       if proxy():
                           setattr(self,item,proxy)
                           self.L_info("{} Connected".format(item,uri))
                       else:
                           self.L_error("Conneting {} on {}".format(item,uri))
                           exit()
                   else:
                       self.L_error("{} Not Found".format(service))
                       exit()
               else:
                   self.L_error("{} Not available".format(service))
                   exit()
        else:
            print("Client Not connected")
            exit()
                


    def TOPICS_list(self,*topics):
        available=self._etc["TOPICS"]
        TOPICS={}
        for t in topics:
            t="{}/{}".format(self._etc["name"],t)
            if t in available:
                robot,comp,topic=t.split("/")
                setattr(self,topic,None)
                TOPICS[topic]=t
            else:
                self.L_error("Topic {} Not Found".format(t))
                exit()
        self._PROC["SUB"].subscribe_topics(**TOPICS)
        self._PROC["SUB"].connect()
        self.L_info("Topics {} Subcripted".format(",".join(topics)))

    def TOPICS(self,**topics):
        available=self._etc["TOPICS"]
        TOPICS={}
        for t,v in topics.items():
            v="{}/{}".format(self._etc["name"],v)
            if v in available:
                robot,comp,topic=v.split("/")
                setattr(self,t,None)
                TOPICS[t]=v
            else:
                self.L_error("Topic {} Not Found".format(t))
                exit()
        self._PROC["SUB"].subscribe_topics(**TOPICS)
        self._PROC["SUB"].connect()
        self.L_info("Topics {} Subcripted".format(",".join(topics)))

    def EVENTS(self,**events):
        EVENTS={}
        available=self._etc["EVENTS"]
        for e,v in events.items():
            v="{}/{}".format(self._etc["name"],v)
            if v in available:
                setattr(self,e,[])
                EVENTS[e]=v
            else:
                self.L_error("Event {} Not Found".format(v))
                exit()
        self._PROC["SUB"].subscribe_events(**EVENTS)
        for e in EVENTS:
            self._PROC["SUB"].add_handler(e,self.on_event)
        self._PROC["SUB"].connect()
        self.L_info("Events {} Subcripted".format(",".join(events.values())))

    def add_HANDLER(self,ent_event,handler):
        if ent_event.find("::")>-1:
            entity,event = ent_event.split("::")
            available=self._etc["EVENTS"]
            if entity in available:
                self._PROC["event_handlers"][ent_event]=handler
        #print(self._PROC["event_handlers"])

    def show_info(self):
        self.L_print("Showing info from [FY]{}".format(self._etc["name"]))
        self.L_print("\t [FY]Available INTERFACES:")
        for s in self._etc["SERVICES"]:
            self.L_print("\t\t {}".format(s))
        self.L_print("\t [FY]Available PUB TOPICS:")
        for s in self._etc["TOPICS"]:
            self.L_print("\t\t {}".format(s))
        self.L_print("\t [FY]Available EMIT TOPICS:")
        for s in self._etc["EMIT_TOPICS"]:
            self.L_print("\t\t {}".format(s))
        self.L_print("\t [FY]Available PUB_EVENT channels:")
        for s in self._etc["EVENTS"]:
            self.L_print("\t\t {}".format(s))
        self.L_print("\t [FY]Available EMIT EVENT channels:")
        for s in self._etc["EMIT_EVENTS"]:
            self.L_print("\t\t {}".format(s))
        self.L_print("\t [FY]MQTT BROKER:[FW]{}".format(self._etc["BROKER"]))
        self.L_print("")

    def on_event(self,channel,msg):
        for e in msg:
            evhan="{}::{}".format(channel,e)
            try:
                doit=self._PROC["event_handlers"][evhan]
                doit()
            except:
                pass
