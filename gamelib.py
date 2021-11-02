"""The goal of this is to be able to create multiplayer games super easily such as:

>>> from gamelib import *
>>> import event as evt
>>> import time
>>> s = Server((evt.getvalidip(), 8090))
>>> @s.event
>>> def on_connect(manager, player):
>>>     print(player + " connected")
>>> @s.event
>>> def loop(manager):
>>>     for client in s.players:
>>>         client["socket"].send("Server is alive!")
>>>     time.sleep(5)

Pre-available events (ones that can be called by program if were registered using server.event decorator). "manager" argument must be specified for every event, but doesn't need to be used:
on_connect - (manager, address)
on_disconnect - (manager, address, playername)
on_error - (manager, player, data, ex)
on_shutdown - (manager)
raw_data - (manager, player, data)
"""
from . import event as evt
from .pyutils import NotInstalledError
import selectors
import socket
import types
import json
import sys
from typing import NoReturn
CRYPTOGRAPHY_DISABLED = False
try:
    from cryptography.fernet import Fernet, InvalidToken
except(ModuleNotFoundError, ImportError):
    CRYPTOGRAPHY_DISABLED = True

class EncryptedData(bytes):
    def __init__(self, string):
        self._string = string
        super().__init__()
    def get(self):
        return self._string

if not CRYPTOGRAPHY_DISABLED:
    class DataCryptor(Fernet):
        def __init__(self, key=None):
            if key is None: key = DataCryptor.generate_key()
            self.key = key
            super().__init__(self.key)
        def __lshift__(self, data):
            if isinstance(data, EncryptedData):
                return self.decrypt(data.get().partition(b'ENC!')[2])
            else:
                return EncryptedData(b'ENC!' + self.encrypt(data))
else:
    class DataCryptor:
        def __init__(self, *a, **kw): raise NotInstalledError("cryptography", "DataCryptor")
        def generate_key(*a, **kw): raise NotInstalledError("cryptography", "DataCryptor")

class Server(evt.eventmanager):
    def __init__(self, address: tuple, encryption: bool = False):
        self.datac = None
        if encryption:
            k = DataCryptor.generate_key()
            print("Your encryption key is {}".format(str(k)))
            self.datac = DataCryptor(k)
            del k
        super().__init__()
        self.register(evt.eventpackage.time)
        self.address = address
        self.debug = False
        self.running = False
        self.players = []
        self.ascii = False

    def event(self, func):
        self.listen(func.__name__, func)
        return func

    def accept_wrapper(self, sock):
        conn, addr = sock.accept()  # Should be ready to read
        self.players.append({"address": addr, "name": None, "socket": conn})
        if "on_connect" in self.listeners: self.emit("on_connect", addr[0]+":"+str(addr[1]))
        if "on_connect2" in self.listeners: self.emit("on_connect2", self.players[-1])
        conn.setblocking(False)
        data = types.SimpleNamespace(addr=addr, inb=b'', outb=b'')
        events = selectors.EVENT_READ | selectors.EVENT_WRITE
        self.sel.register(conn, events, data=data)

    def service_connection(self, key, mask):
        sock = key.fileobj
        data = key.data
        if mask & selectors.EVENT_READ:
            try:
                recv_data = sock.recv(1024)  # Should be ready to read
            except ConnectionResetError:
                return
            if self.debug: print(sock.getpeername(), recv_data)
            if recv_data:
                for pl in self.players:
                    if pl["address"] == sock.getpeername(): break
                if "enc_data" in self.listeners and self.datac:
                    res = self.emit("enc_data", pl, recv_data)
                    if res: return sock.send(res.encode('utf-8'))
                if self.datac and recv_data.startswith(b'ENC!'):
                    try: recv_data = self.datac >> recv_data
                    except Exception as e: print('Got fernet error: %s' % type(e).__name__ + (": " + str(e) if str(e) else "")); return sock.send(bytes(type(e).__name__ + (": " + str(e) if str(e) else ""), 'utf-8', 'ignore'))
                elif recv_data.startswith(b'ENC!'):
                    return sock.send(b'Server error: You are sending encrypted data to the server when the server has encryption disabled.')
                elif self.datac:
                    return sock.send(b"Server error: You are sending unencrypted data when server has encryption enabled.")
                recv_data : str = recv_data.decode('utf-8', 'ignore')
                if self.ascii and not recv_data.isascii(): return sock.send(b'Tried to send non-ASCII data to server with ASCII lock enabled.')
                try:
                    if "raw_data" in self.listeners: self.emit("raw_data", pl, recv_data)
                    gotit = json.loads(str(recv_data) if not "{" in str(recv_data).replace("{", "", 1) else str(recv_data).partition("}{")[0]+"}")
                    if gotit["event"] not in self.listeners and gotit["event"] != "ping": return sock.send(f"Event type {gotit['event']} doesn't exist.".encode('utf-8'))
                    res = self.emit(gotit["event"], pl, *gotit["args"])
                    if res: sock.send(str(res).replace("'", '"').encode('utf-8'))
                except Exception as e:
                    if "on_error" in self.listeners:
                        res = self.emit("on_error", pl, recv_data, e)
                        if res: sock.send(res.encode('utf-8'))
            else:
                addr = sock.getpeername()
                self.sel.unregister(sock)
                for pl in self.players:
                    if pl["address"] == sock.getpeername():
                        playername = pl["name"]
                        self.players.pop(self.players.index(pl))
                if "on_disconnect" in self.listeners: self.emit("on_disconnect", addr[0]+":"+str(addr[1]), playername)
                sock.close()
        if mask & selectors.EVENT_WRITE:
            if data.outb:
                #print(f"{self.datac=} {data.outb=}")
                if self.datac: data.outb = self.datac << data.outb
                #print('echoing', repr(data.outb), 'to', data.addr)
                sent = sock.send(data.outb)  # Should be ready to write
                data.outb = data.outb[sent:]

    def startup(self) -> NoReturn:
        sel = selectors.DefaultSelector()
        self.sel = sel
        lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        lsock.bind(self.address)
        lsock.listen()
        print("Server started. Connect by %s:%s" % (self.address[0], str(self.address[1])))
        lsock.setblocking(False)
        sel.register(lsock, selectors.EVENT_READ, data=None)

        self.running = True
        while self.running:
            try:
                events = sel.select(timeout=None)
            except KeyboardInterrupt:
                if "on_shutdown" in self.listeners: self.emit("on_shutdown")
                self.close_()
                sys.exit(0)
            for key, mask in events:
                if key.data is None:
                    self.accept_wrapper(key.fileobj)
                else:
                    try:
                        self.service_connection(key, mask)
                    except ConnectionResetError:
                        sock = key.fileobj
                        addr = sock.getpeername()
                        self.sel.unregister(sock)
                        for pl in self.players:
                            if pl["address"] == sock.getpeername():
                                playername = pl["name"]
                                self.players.pop(self.players.index(pl))
                        if "on_disconnect" in self.listeners: self.emit("on_disconnect", addr[0]+":"+str(addr[1]), playername)
                        sock.close()
            try:
                if "loop" in self.listeners: self.emit("loop")
            except KeyboardInterrupt:
                if "on_shutdown" in self.listeners: self.emit("on_shutdown")
                self.close_()
                sys.exit(0)

    def set(self, **kwargs):
        arguments = {
            "ascii": self.ascii,
            "debug": self.debug
        }
        for k,v in kwargs.items():
            if not k in arguments: raise ValueError("Invalid argument %s" % k)
            arguments[k] = v

    def close_(self, message=None):
        if message:
            for i in self.players:
                try:
                    i["socket"].send(message.encode('utf-8'))
                except Exception:
                    continue
        #self.sel.close()
        #for i in self.players:
        #    i["socket"].close()

class Player(evt.eventmanager):
    def __init__(self, address: tuple, encryption_key: bytes = b""):
        self.datac = None
        if encryption_key: self.datac = DataCryptor(encryption_key)
        super().__init__()
        self.sel = selectors.DefaultSelector()
        self.addr = address
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setblocking(False)
        try:
            sock.connect_ex(self.addr)
        except:
            raise ValueError("Incorrect IP address")
        self.sock = sock
        self.player = None
        self.events = selectors.EVENT_READ | selectors.EVENT_WRITE
        data = types.SimpleNamespace(outb=b"")
        self.sel.register(sock, self.events, data=data)
        self.tosend = None
        self.receiving = False

    def send_message(self, message):
        self.tosend = message

    def service_connection(self, key, mask):
        sock = key.fileobj
        data = key.data
        if mask & selectors.EVENT_READ:
            recv_data = sock.recv(1024)  # Should be ready to read
            if recv_data:
                if self.datac and recv_data.startswith(b'ENC!'): recv_data = self.datac >> recv_data
                return recv_data.replace(b"'", b'"')
            if not recv_data:
                if "on_shutdown" in self.listeners: self.emit("on_shutdown")
                else: print('Server shut down.')
                self.sel.unregister(sock)
                sock.close()
        if mask & selectors.EVENT_WRITE:
            if not data.outb:
                if self.tosend: data.outb = bytes(self.tosend, "utf-8")
                self.tosend = None
            if data.outb:
                if self.datac: data.outb = self.datac << data.outb
                sent = sock.send(data.outb)  # Should be ready to write
                data.outb = data.outb[sent:]

    def start(self, no_reg=False):
        if not no_reg:
            msg = input("Your name that other players will see: ").strip()
            self.tosend = json.dumps({"event": "register", "args": [msg]})
            self.receiving = True
        while True:
            events = self.sel.select(timeout=1)
            if not self.receiving:
                evt = input("Choose an event to send >> ")
                args = input("Enter additional arguments split by | >> ").strip().split("|")
                self.tosend = json.dumps({"event": evt, "args": args})
                self.receiving = True
            else:
                if events:
                    for key, mask in events:
                        data = self.service_connection(key, mask)
                        if data: print(data)
                if not self.sel.get_map(): break

    def disconnect(self):
        self.sel.close()
        self.sock.close()

class ServerAlt(evt.eventmanager):
    def __init__(self, address: tuple, debug: bool = False):
        super().__init__()
        self.register(evt.eventpackage.time)
        self.address = address
        self.debug = debug
        self.running = False
        self.players = []

    def event(self, func):
        self.listen(func.__name__, func)

    def accept_wrapper(self, sock):
        conn, addr = sock.accept()  # Should be ready to read
        if "on_connect" in self.listeners: self.emit("on_connect", addr[0]+":"+str(addr[1]))
        conn.setblocking(False)
        data = types.SimpleNamespace(addr=addr, inb=b'', outb=b'')
        events = selectors.EVENT_READ | selectors.EVENT_WRITE
        self.sel.register(conn, events, data=data)
        self.players.append({"address": addr, "name": None, "socket": conn})

    def service_connection(self, key, mask):
        sock = key.fileobj
        data = key.data
        if mask & selectors.EVENT_READ:
            recv_data = sock.recv(1024)  # Should be ready to read
            if recv_data:
                recv_data = recv_data.decode('utf-8')
                try:
                    gotit = json.loads(str(recv_data))
                    for pl in self.players:
                        if pl["address"] == sock.getpeername():
                            if gotit["event"] not in self.listeners: return sock.send(f"Event type {gotit['event']} doesn't exist.".encode('utf-8'))
                            res = self.emit(gotit["event"], pl, *gotit["args"])
                            if res: sock.send(str(res).encode('utf-8'))
                except json.decoder.JSONDecodeError as e:
                    print("Error", e)
                    print(recv_data)
                    sock.send(b"Error has occured.")
            else:
                addr = sock.getpeername()
                self.sel.unregister(sock)
                for pl in self.players:
                    if pl["address"] == sock.getpeername():
                        playername = pl["name"]
                        self.players.pop(self.players.index(pl))
                        break
                if "on_disconnect" in self.listeners: self.emit("on_disconnect", addr[0]+":"+str(addr[1]), playername)
                if "on_disconnect2" in self.listeners: self.emit("on_disconnect2", pl)
                sock.close()
        if mask & selectors.EVENT_WRITE:
            if data.outb:
                print('echoing', repr(data.outb), 'to', data.addr)
                sent = sock.send(data.outb)  # Should be ready to write
                data.outb = data.outb[sent:]

    def startup(self):
        sel = selectors.DefaultSelector()
        self.sel = sel
        lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        lsock.bind(self.address)
        lsock.listen()
        print("Server started. Connect by %s:%s" % (self.address[0], str(self.address[1])))
        lsock.setblocking(False)
        sel.register(lsock, selectors.EVENT_READ, data=None)

        self.running = True
        while self.running:
            events = sel.select(timeout=None)
            for key, mask in events:
                if key.data is None:
                    self.accept_wrapper(key.fileobj)
                else:
                    data = self.service_connection(key, mask)
                    print(data)
            try:
                if "loop" in self.listeners: self.emit("loop")
            except KeyboardInterrupt:
                sys.exit(0)

class PlayerAlt:
    pass