#/\/\/\/\/\/\/\
r'r'  r'r'   #| Made and signed by dank_meme#0210 on discord.
b'b'   b'b'  #| Free software. Editing is highly unrecommended.
f'f'    f'f' #|
u'u'     u'u'#|
f'f'    f'f' #|
b'b'   b'b'  #| Don't touch this code unless you know what you are doing.
r'r'  r'r'   #| Will be better for you...
#\/\/\/\/\/\/\/

import socket
import os
import random
import sys
import time
import json
#import pif
#import tkinter.messagebox as msb
#from tkinter import *
from datetime import datetime
from enum import Enum
from functools import partial as pt
#root = Tk()
#root.withdraw()

def getvalidip(local: bool = False):
    """ Try to get a valid IP address of machine. If local is True, tries to return an ip address starting with 192.168.(0/1) if one found. If nothing matches, returns 127.0.0.1 """
    ips = socket.gethostbyname_ex(socket.gethostname())[-1]
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    for ip in ips:
        if (not "192.168.0." in ip) and (not "192.168.1." in ip) and local: continue
        try:
            s.connect((ip, 1))
            s.close()
            return ip
        except Exception as e:
            s.close()
    #return pif.get_public_ip()
    return "127.0.0.1"

def format_addr(address: tuple) -> str:
    return f"{address[0]}:{address[1]}"

def get_size(bytes, suffix="B"):
    factor = 1024
    for unit in ["", "K", "M", "G", "T", "P", "E", "Z", "Y"]:
        if bytes < factor:
            return f"{bytes:.2f}{unit}{suffix}"
        bytes /= factor

class eventpackage(Enum):
    all = 1
    safe = 2 # safe is all BUT cmd, run, execute, ex
    basic = 3# only basic and useful commands, such as time, broadcast, cmd and response
    def _time(manager, args):
        """ Returns current computer time. """
        return datetime.today().strftime('%d-%m-%Y-%H:%M:%S')
    time = pt(_time)
    curtime = pt(_time)
    def _run(manager, args):
        """ Runs a command in console. Use carefully. """
        cmd = "|".join(args)
        if type(cmd) == list: cmd = " ".join(cmd)
        return os.system(cmd)
    cmd = pt(_run)
    run = pt(_run)
    def _broadcast(manager, args):
        """ Broadcasts(prints) a message on end server. """
        message = "|".join(args)
        return print(message)
    broadcast = pt(_broadcast)
    bc = pt(_broadcast)
    def _execute(manager, args):
        """ Executes a piece of python code (or evals if possible). Be careful. """
        code = "|".join(args)
        try:
            resp = eval(code)
        except:
            resp = exec(code)
        return resp
    execute = pt(_execute)
    ex = pt(_execute)
    def _listcmds(server, args):
        """ List all commands(events) that server listens for if no arguments are specified. If you specify a command, returns a docstring for the command"""
        if len(args) < 1 or (len(args) == 1 and args[0] == ""): return "Possible commands: " + ", ".join([i for i in server.listeners]) + "\nTo get help on each command, add the command name as an arg"
        if args[0] in server.listeners: return "No documentation had been found for this command." if not server.listeners[args[0]].__doc__ else server.listeners[args[0]].__doc__
        return "Command " + args[0] + " not found."
    listcmds = pt(_listcmds)
    help = pt(_listcmds)
    #@server.event
    #def message(*args):
    #    msb.showinfo("Received message", "|".join(args[0]))     
    def _response(manager, args):
        """ Asks for an input from a server. Beware, that while server hasn't responded yet, client will be timed out. """
        print("|".join(args))
        return input("Respond: ")    
    response = pt(_response)
    input = pt(_response)
    def _hardware(manager, args):
        """ Prints a brief information about hardware of server. If psutil is installed, prints a lot more. """
        import os,platform
        uname = platform.uname()
        try:
            import psutil
        except ImportError:
            osi = f"{platform.system()} {platform.release()} ({os.name.upper()})"
            cpu = uname.processor
            boot = "Unknown"
            mem = "Unknown"
            disc = "Unknown"
            network = "Unknown"
            additional = "To get info about all unknown specifications, install psutil module on target machine."
        else:
            additional = ""
            from datetime import datetime
            osi = f"{platform.system()} {platform.release()} ({os.name.upper()})"
            cpu = f"{uname.processor} | {str(psutil.cpu_count(logical=True))} cores {psutil.cpu_freq().max}MHz"
            try:
                bot = datetime.fromtimestamp(psutil.boot_time())
            except PermissionError:
                boot = "No permission to get data"
            else:
                boot = f"{bot.day}.{bot.month}.{bot.year}-{bot.hour}:{bot.minute}:{bot.second}"
            mm = psutil.virtual_memory()
            mem = f"{get_size(mm.used)}/{get_size(mm.total)} used"
            disc = ""
            for p in psutil.disk_partitions():
                disc += f"\n{p.device} : {p.fstype} : "
                try:
                    usage = psutil.disk_usage(p.mountpoint)
                except PermissionError:
                    disc += "Uninitialized"
                    continue
                disc += f"{get_size(usage.used)}/{get_size(usage.total)}({usage.percent}%) used"
            # networking
            network = "\n"
            for name,addr in psutil.net_if_addrs().items():
                for adr in addr:
                    network += "="*20 + f"Interface: {name}" + "="*20 + "\n"
                    if str(adr.family) == "AddressFamily.AF_INET":
                        network += f"IP: {adr.address}\nNetmask: {adr.netmask}\nBroadcast IP: {adr.broadcast}\n"
                    else:
                        network += f"MAC: {adr.address}\nNetmask: {adr.netmask}\nBroadcast MAC: {adr.broadcast}\n"
        string = f"System information:\nOS: {osi}\nProcessor: {cpu}\nMachine: {uname.machine}\nNode: {uname.node}\nBoot time: {boot}\nMemory: {mem}\nDisk usage: {disc}\nNetwork info: {network}\n{additional}"
        return string
    hardware = pt(_hardware)
    hw = pt(_hardware)
    time.__doc__, curtime.__doc__, cmd.__doc__, run.__doc__ = _time.__doc__, _time.__doc__, _run.__doc__, _run.__doc__
    broadcast.__doc__, bc.__doc__, execute.__doc__, ex.__doc__ = _broadcast.__doc__, _broadcast.__doc__, _execute.__doc__, _execute.__doc__
    listcmds.__doc__, help.__doc__, response.__doc__, input.__doc__, hardware.__doc__, hw.__doc__ = _listcmds.__doc__, _listcmds.__doc__, _response.__doc__, _response.__doc__, _hardware.__doc__, _hardware.__doc__

class eventmanager:
    """
    A very basic event manager.
    Syntax:
    ```
        evt = eventmanager()
        def add(n1, n2):
            print(n1 + n2)
        evt.listen("add", add)
        evt.emit("add", 5, 7)
    ```
    Decorator syntax:
    ```
        evt = eventmanager()
        @evt.event
        def add(n1, n2):
            print(n1 + n2)
        evt.emit("add", 5, 7)
    ```
    Output:
        >>> 12
    """
    def __init__(self):
        self.listeners = {}

    def emit(self, event, *args):
        """ Try to play the event specified. """
        try:
            return self.listeners[event](self, *args)
        except KeyError:
            raise ValueError("Command " + str(event) + " does not exist. Use listcmds or help")
        except KeyboardInterrupt:
            raise KeyboardInterrupt()
        except BaseException as e:
            import traceback
            traceback.print_exception(*sys.exc_info())
            return "There was an error during the execution: " + str(e)

    def listen(self, event, func):
        """ Add a simple event listener. """
        self.listeners[event] = func
        return print("Added event " + event)

    def event(self, func):
        """ A decorator function for adding an event. Could be an alternative to listen, but without custom alias. """
        self.listeners[func.__name__] = func
        return func

    def close(self, name: str):
        """ Removes an event. """
        try:
            del self.listeners[name]
        except KeyError:
            return print("Event " + name + " was not found.")
        except BaseException as e:
            raise e

    def register(self, event: eventpackage):
        """ Registers an event from eventpackage. """
        if event == eventpackage.all:
            for name, fn in {i.name: i.value for i in eventpackage if i.name not in ["all", "safe", "basic"]}.items(): self.listen(name, fn)
            return
        elif event == eventpackage.safe:
            for name, fn in {i.name: i.value for i in eventpackage if i.name not in ["all", "safe", "basic", "cmd", "run", "execute", "ex"]}.items(): self.listen(name, fn)
            return
        elif event == eventpackage.basic:
            for name, fn in {i.name: i.value for i in eventpackage if i.name in ["time", "broadcast", "cmd", "response"]}.items(): self.listen(name,fn)
            return
        return self.listen(event.name, event.value)
        #print("Added event " + event.name)

    def unregister(self, event: eventpackage):
        """ Unregisters events from eventpackage. Shorthand for .close(event.name) """
        return self.close(event.name)


class eventlistener(eventmanager):
    """
    Basic event listener.
    """
    def __init__(self, ip=getvalidip(True), port=random.randint(10000,60000)):
        #global msb#, root
        super().__init__()
        if not ip: ip = getvalidip(True)
        print(ip)
        self.address = (ip, port)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((ip, port))
        print(f"Server started. Connect by {ip}:{port}")
        #from tkinter import Tk
        #import tkinter.messagebox as msb
        #root = Tk()
        #root.withdraw()

    def receive(self, data, addr):
        """ Handle receiving data """
        try:
            if data == "ping": return self.sendback(addr, "Pong!".encode("utf-8"))
            cnt = json.loads(data)
            self.sendback(addr, self.emit(cnt["name"], *cnt["args"]))
        except ValueError as e:
            print("Message from: " + str(addr))
            print("Content: " + data)
            self.sendback(addr, "Successfully received response.")
        except Exception as e:
            self.sendback(addr, "An error occured: " + str(e))

    def sendback(self, address, content):
        self.socket.sendto(str(content).encode("utf-8"), address)

    def loop(self, stopat: int = 0):
        """Creates a server loop that stops in stopat seconds. Doesn't stop if stopat == 0"""
        if stopat == 0:
            while True:
                data, addr = self.socket.recvfrom(1024)
                data = data.decode("utf-8")
                self.receive(data, addr)
                #root.update()
        else:
            stoptime = time.time() + stopat
            while True:
                if time.time() > stoptime: exit()
                data, addr = self.socket.recvfrom(1024)
                data = data.decode("utf-8")
                self.receive(data, addr)
                #root.update()

    def loopfn(self) -> None:
        data, addr = self.socket.recvfrom(1024)
        data = data.decode("utf-8")
        self.receive(data, addr)

class eventemitter(eventmanager):
    """
    Basic event emitter
    """
    def __init__(self, ip, port):
        self.address = (ip, port)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.connect(self.address)
        print(f"Connected to {self.address[0]}:{self.address[1]}")

    def ping(self): 
        curtime = time.time()
        self.socket.sendto("ping".encode("utf-8"), self.address)
        data, addr = self.socket.recvfrom(1024)
        data = data.decode("utf-8")
        print(str(data) + " Current ping is " + str(round((time.time() - curtime) * 1000)) + " ms")

    def send(self, event, *args):
        message = {"name":event, "args":args}
        self.socket.sendto(json.dumps(message).encode("utf-8"), self.address)
        data, addr = self.socket.recvfrom(1024)
        data = data.decode("utf-8")
        print(f"Response from {addr[0]}:{addr[1]}: {data}")

    def close(self):
        self.socket.close()


def initserver(customport: int=random.randint(10000,60000), customhost: str=None, eventpack: eventpackage = eventpackage.safe):
    """ Main function for initializing a server. Change eventpack to eventpackage.all or eventpackage.basic if you want more/less commands"""
    server = eventlistener(port=customport, ip=customhost)
    server.register(eventpack)
    server.loop()


def initclient(host: str, port: int):
    client = eventemitter(host, port)
    while True:
        prompt = input("Enter event to send to host: ").strip()
        if len(prompt) == 0: continue
        if prompt == "ping": client.ping(); continue
        arguments = input("Enter additional arguments, separated by '|': ").strip().split('|')
        client.send(prompt, arguments)


if __name__ == "__main__":
    initserver(33094, "")