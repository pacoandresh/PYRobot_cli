#!/usr/bin/env python3
# ____________developed by paco andres_15/04/2019___________________

import paho.mqtt.client as mqtt
from PYRobot.botlogging.coloramadefs import P_Log

def mqtt_alive(uri):
    ip,port=uri.split(":")
    try:
        client = mqtt.Client()
        client.connect(ip, int(port), 60)
        return True
    except:
        raise
        return False

def mqtt_is_run(mosquito_uri):
    P_Log("[FY] Finding BROKER MQTT on {}".format(mosquito_uri))
    if mqtt_alive(mosquito_uri):
        P_Log("\t[[FG]OK[FW]] BROKER MQTT Located on {}".format(mosquito_uri))
        P_Log("")
    else:
        P_Log("\t[[FR]ERROR[FW]] BROKER MQTT NOT Located")
        exit()
