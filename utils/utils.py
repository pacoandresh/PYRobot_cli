
#!/usr/bin/env python3
# ____________developed by paco andres_15/04/2019___________________

import netifaces as ni
import traceback
import sys
from termcolor import colored
import threading
import os
import paho.mqtt.client as mqtt
import socket
import setproctitle
import psutil
from gevent.subprocess import Popen
from PYRobot.botlogging.coloramadefs import P_Log
import time
import socket


def change_process_name(name):
    setproctitle.setproctitle(name)

def get_process_name():
    return setproctitle.getproctitle()

def mqtt_alive(uri):
    ip,port=uri.split(":")
    try:
        client = mqtt.Client()
        client.connect(ip, int(port), 60)
        return True
    except:
        return False

def get_host_name():
    return socket.gethostname()

def get_ip_address(ifname="lo"):
    """Return IP address from a specific interface."""
    try:
        ip = ni.ifaddresses(ifname)[ni.AF_INET][0]['addr']
    except Exception:
        #  Invalid interface name
        try:
            interface_list = ni.interfaces()
            for x in interface_list:
                if x != "lo":
                    return ni.ifaddresses(x)[ni.AF_INET][0]['addr']
            ip = "127.0.0.1"
        except Exception:
            print("ERROR: Obtaining IP from the network interface. "
                  + colored(ifname, "red"))
            sys.exit()
    return ip

def get_all_ip_eths():
    address = []
    try:
        for x in ni.interfaces():
            add=ni.ifaddresses(x)
            ips=add.get(ni.AF_INET,[])
            if x!="lo":
                if len(ips)>0:
                    address.append((ips[0]["addr"],x))
    except Exception:
        print("ERROR: get_all_ip_eths")
        raise
    #print(address)
    return address

def get_ethernets():
    eths=get_all_ip_eths()
    sal={e:ip for ip,e in eths}
    sal["lo"]="127.0.0.1"
    return sal

def set_eth_ip(eth):
    ethernets=get_ethernets()
    ip="0.0.0.0"
    if eth in ethernets:
        ip=ethernets[eth]
    else:
        eth=list(ethernets)[0]
        ip=list(ethernets.values())[0]
    return eth,ip


def get_all_ip_address(broadcast=False):
    """Return the list of IPs of all network interfaces.

    If broadcast = True, returns the list of broadcast IPs of all network
    interfaces.
    """
    address = []
    try:
        for x in ni.interfaces():
            add = ni.ifaddresses(x)
            try:
                for ips in add[ni.AF_INET]:
                    if broadcast:
                        address.append(ips["broadcast"])
                    else:
                        address.append(ips["addr"])
            except Exception:
                pass
    except Exception:
        print("ERROR: utils.get_all_ip_address()")
        exit()
        raise
    return address


def get_gateway_address(ifname="lo"):
    """Return gateway address from a specific interface."""
    ip = None
    try:
        gateway_list = ni.gateways()
        for gw in gateway_list[2]:
            if gw[1] is ifname:
                ip = gw[0]
                break
    except Exception:
        raise
    return ip


def get_interface():
    """Return the name of the first network interface other than loopback."""
    interface = None
    loopback = None
    try:
        for x in ni.interfaces():
            try:
                if ni.ifaddresses(x)[ni.AF_INET][0]['addr'] != "127.0.0.1":
                    interface = x
                    break
                else:
                    loopback = x
            except Exception:
                pass
    except Exception:
        raise

    if not interface:
        interface = loopback

    return interface


def get_free_ports(ip, port,num=1):
    #free_ports=[[port,socket.socket(socket.AF_INET, socket.SOCK_STREAM)] for i in range(num)]
    free_ports=[]
    for n in range(num):
        result=False
        while not result:
            try:
                sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.bind((ip, port))
                free_ports.append([port,sock])
                #print("free",port,ip)
                port=port+1
                result=True
            except socket.error as e:
                #print(e)
                #print("ocupado",port,e)
                port=port+1
    return free_ports        


def format_exception(e):
    """Representation of exceptions."""
    exception_list = traceback.format_stack()
    exception_list = exception_list[:-2]
    exception_list.extend(traceback.format_tb(sys.exc_info()[2]))
    exception_list.extend(traceback.format_exception_only(
        sys.exc_info()[0], sys.exc_info()[1]))

    exception_str = "Traceback (most recent call last):\n"
    exception_str += "".join(exception_list)

    exception_str = exception_str[:-1]

    return exception_str

def run_component(*args,run="start"):
    try:
        args=list(args)
        args.insert(0,"python3")
        args[1]=args[1]+".py"
        if run in ["start","stop","kill","status"]:
            args.append(run)
            args.append("&")
            p=Popen(args)
    except:
        raise
        P_Log("[FR][ERROR][FY] initiating Component {}".format(args[2]))

def kill_process(pid):
     p = psutil.Process(pid)
     p.terminate()

def findProcessIdByName(processName):
    '''
    Get a list of all the PIDs of a all the running process whose name contains
    the given string processName
    '''

    listOfProcessObjects = []

    #Iterate over the all the running process
    for proc in psutil.process_iter():
       try:
           pinfo = proc.as_dict(attrs=['pid', 'name', 'cmdline'])
           if len(pinfo['cmdline'])>0:
               if processName in pinfo['cmdline'][0] :
                   listOfProcessObjects.append(pinfo)

       except (psutil.NoSuchProcess, psutil.AccessDenied , psutil.ZombieProcess) :
           pass

    return [(item["pid"],item["cmdline"][0]) for item in listOfProcessObjects];

def ping(uri):
    """Ping and return True if there is connection, False otherwise."""
    response = False
    try:
        response = os.system("ping -c 1 -w2 " + uri + " > /dev/null 2>&1")
    except Exception:
        pass
    return not response

def get_ip_port(uri):
    try:
        ip,port=uri.split(":")
    except:
        ip="0.0.0.0"
        port=0
    return ip,int(port)


def get_PYRobots_dir():
    """ It turns back the environment path of the program Pyro4Bot """
    if "PYROBOTS" not in os.environ:
        print("ERROR: PYROBOTS not setted")
        print("please type export PYROBOT=<DIR> to set it up")
        sys.exit()
    else:
        return os.environ["PYROBOTS"]
    
def show_PROC(data):
    if data["_PROC"]["status"]=="OK":
        P_Log("[FG] [OK][FY] Starded Component {}".format(data["_etc"]["name"]))
    else:
        P_Log("[FR] [FAIL][FY] Starded Component {}".format(data["_etc"]["name"]))
    P_Log("\t Network:{} Host: {} Pid:{}".
            format(data["_etc"]["ethernet"],data["_etc"]["host"],data["_PROC"]["PID"]))
    if all:
        for t in data["_PROC"]["info"]:
            P_Log("\t {} {}".format(t[1],t[0]))
            for w in data["_PROC"]["warnings"][t[0]]:
                P_Log("\t\t Warning: {} not implemented".format(w))
        topics=data["_PROC"]["PUB"]
        mq={top:tip for top,tip in topics.items() if tip=="MQ"}
        br={top:tip for top,tip in topics.items() if tip=="BR"}
        mc={top:tip for top,tip in topics.items() if tip=="MC"}
        if len(topics)>0:
            P_Log("\t Publicating:")
            if len(mq)>0:
                P_Log("\t\t Broker MQTT: {}".format(",".join(mq)))
            if len(br)>0:
                P_Log("\t\t IP Broadcast: {}".format(",".join(br)))
            if len(mc)>0:
                P_Log("\t\t IP Multicast: {}".format(",".join(mc)))
        suscribers=data["_PROC"]["SUS"]
        if len(suscribers)>0:
            P_Log("\t Suscribing:")
            for s,v in suscribers.items():
                P_Log("\t\t{}={}".format(v,s))
        proxys=data["_PROC"]["PROXYS"]
        if len(proxys)>0:
            P_Log("\t Proxys connected:")
            for at,pro in proxys.items():
                P_Log("\t\t{}={}".format(at,pro))
    P_Log("")
