#!/usr/bin/env python3
# ____________developed by paco andres_15/04/2019___________________


from mprpc import RPCClient
import types
import time
from PYRobot.botlogging.coloramadefs import P_Log


def_skel_old="""
def {0}{1}:
    try:
        return self._link_.call('{0}'{2})
    except Exception as ex:
        P_Log("[[FR]ERROR[FW]] Running {0}{1} on Proxy {3}")
        P_Log(str(ex))
        return None
"""

def_skel="""
def {0}{1}:
    try:
        return self._link_.call('{0}'{2})
    except:
        raise
        return None
"""

class Proxy(object):
    def __init__(self,uri, show=False):
        self.showerr=show
        try:
            self.host,self.port=uri.split(":")
        except:
            self.host="0.0.0.0"
            self.port=0

        self.OK=False
        self.__linked=False
        try:
            self._link_=RPCClient(self.host,int(self.port),timeout=10)
            self.__linked=True
        except:
            self.__linked=False
            if show:
                P_Log("[FR]ERROR [FW] No Link to {}".format(uri))
            

    def _close(self):
        if self._link_.is_connected():
            self._link_.close()

    def connect(self):
        try:
            if not self.OK:
                self._link_=RPCClient(self.host,int(self.port),timeout=20)
                if self._link_.is_connected():
                    self.OK=self.__create_hooks()
                else:
                    self.OK=False
        except:
            self.OK=False
            if self.showerr:
                P_Log("[FR]ERROR [FW] No Connect to {}".format(uri))
        finally:
            return self.OK

    def __call__(self):
        return self.connect()

    def __str__(self):
        if self.OK:
            return "{}:{}::Connected".format(*self._link_.getpeername())
        elif self.__linked:
            return "{}:{}::Linked".format(*self._link_.getpeername())
        else:
            return "Disconected 1.1.1.1:1"

    def __create_hooks(self):
        try:
            _config=self._link_.call('G_E_T_Configuration')
        except:
            _config={}
            #print("error creating hooks {}:{}".format(self.host,self.port))
        hooks=[]
        for defs,params in _config.items():
            params_def=params[0]
            params_call=""
            for x in params[1]:
                params_call=params_call+","+str(x)
            d=def_skel.format(defs,params_def,params_call,self.host+":"+str(self.port))
            #print(d)
            hooks.append((defs,d))
        for defs,fun in hooks:
            #print(defs,fun)
            exec(fun)
            self.__dict__[defs] = types.MethodType(eval(defs), self)
        self.functions=hooks
        return len(self.functions)>0

    def get_uri(self):
        return "{}:{}".format(self.host, self.port)

    def get_functions(self):
        return [a for a,b in self.functions]

    def call(self,fn,*args):
        try:
            return self._link_.call(fn,*args)
        except Exception as ex:
            #raise
            P_Log("[[FR]ERROR[FW]] Running call on Proxy {}".format(self.get_uri()))
            P_Log(str(ex))
            return None
