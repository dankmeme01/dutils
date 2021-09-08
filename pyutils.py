from functools import wraps, partial
from itertools import groupby, zip_longest
from inspect import getfullargspec
from threading import Timer, Lock
from datetime import datetime
from socket import socket
from pathlib import Path
from typing import Any, Union
from pynput import mouse, keyboard
import json
import os
import time

overloaded = {}

class ReusableTimer(object):
    """
    A reusable thread safe timer implementation
    """

    def __init__(self, interval_sec, function, *args, **kwargs):
        """
        Create a timer object which can be restarted

        :param interval_sec: The timer interval in seconds
        :param function: The user function timer should call once elapsed
        :param args: The user function arguments array (optional)
        :param kwargs: The user function named arguments (optional)
        """
        self._interval_sec = interval_sec
        self._function = function
        self._args = args
        self._kwargs = kwargs
        # Locking is needed since the '_timer' object might be replaced in a different thread
        self._timer_lock = Lock()
        self._timer = None

    def start(self, restart_if_alive=True):
        """
        Starts the timer and returns this object [e.g. my_timer = TimerEx(10, my_func).start()]

        :param restart_if_alive: 'True' to start a new timer if current one is still alive
        :return: This timer object (i.e. self)
        """
        with self._timer_lock:
            # Current timer still running
            if self._timer is not None:
                if not restart_if_alive:
                    # Keep the current timer
                    return self
                # Cancel the current timer
                self._timer.cancel()
            # Create new timer
            self._timer = Timer(self._interval_sec, self.__internal_call)
            self._timer.start()
        # Return this object to allow single line timer start
        return self

    def cancel(self):
        """
        Cancels the current timer if alive
        """
        with self._timer_lock:
            if self._timer is not None:
                self._timer.cancel()
                self._timer = None

    def is_alive(self):
        """
        :return: True if current timer is alive (i.e not elapsed yet)
        """
        with self._timer_lock:
            if self._timer is not None:
                return self._timer.is_alive()
        return False

    def __internal_call(self):
        # Release timer object
        with self._timer_lock:
            self._timer = None
        # Call the user defined function
        self._function(*self._args, **self._kwargs)

def colormsg(color, content, send=True):
    colord = {"blue": "\u001b[34m", "red": "\u001b[31m", "green":"\u001b[32m", "yellow": "\u001b[33m", "reset": "\u001b[0m", "black": "\u001b[30m", "wild": "\u001b[30m"}
    if not color in colord.keys():
        raise ValueError('Invalid color: ' + color)
    else:
        if send:
            code = colord[color]
            print(u"" + code + str(content) + colord["reset"])
        else:
            return u""+colord[color]+str(content)+colord["reset"]

def whole(number: float) -> bool:
    return (number - int(number) == 0)

def beautify(num: float) -> str:
    """
    Beautify a float number. Returns int of it if the number is whole. Otherwise returns number with 3 digits after comma
    """
    if whole(num): return str(int(num))
    if len(str(num)) > 6: return "{:.3f}".format(round(num, 3))
    return str(num)

def timeit(func):
    @wraps(func)
    def wrap(*args, **kwargs):
        before = time.time()
        val = func(*args, **kwargs)
        print("Function took", beautify(time.time() - before), "s")
        return val
    return wrap

def repeat(times):
    def deco(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            vals = []
            for _ in range(times):
                vals.append(func(*args, **kwargs))
            return vals
        return wrapper
    return deco

def multi_thread(amount: int, function):
    from threading import Thread
    for _ in range(amount):
        th = Thread(target=function)
        th.daemon = False
        th.start()

def multi_thread_deco(threads: int):
    def deco(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            from threading import Thread
            for i in range(threads):
                th = Thread(target=(lambda a = args, b = kwargs : func(*a, *b)))
                th.daemon = False
                th.start()
        return wrapper
    return deco

def minify(path: str) -> None:
    if not os.path.exists(path): raise FileNotFoundError("File was not found by path %s" % path)
    raise NotImplementedError("Not done yet.")

def all_equal(iterable):
    """ Checks if all array elements are equal"""
    g = groupby(iterable)
    return next(g, True) and not next(g, False)

def search(string: str, start: str, end: str):
    import re
    res = re.search(f"{start}(.*){end}", string)
    if not res: return res
    return res.group(1)

def replace_mul(string: str, strings: dict) -> str:
    for k,v in strings.items():
        string = string.replace(k, v)
    return string

def browser_open(path: str):
    import webbrowser
    print("Opening", path)
    browser = webbrowser.get("C:\\Users\\User\\AppData\\Local\\Programs\\Opera GX\\73.0.3856.434\\opera.exe %s".replace("\\", "/"))
    browser = webbrowser.get('windows-default')
    #print(type(browser))
    return browser.open(path)

def print_ret(*msg, **kwargs):
    print(*msg, **kwargs)
    if len(msg) == 1: return msg[0]
    return msg

def overload(func):
    if not func.__name__ in overloaded: overloaded[func.__name__] = []
    overloaded[func.__name__].append(func)
    def returned(func, *args, **kwargs):
        for fun in overloaded[func.__name__]:
            args_ = getfullargspec(fun)
            ans = args_.annotations
            if len(ans) == 0: continue
            for arg, sup in zip_longest(args_.args, list(args)+list(kwargs.keys())):
                if ans.get(arg, Any) == Any: continue
                if not ans[arg] == type(sup): break
            else:
                return fun(*args, **kwargs)
        raise TypeError("Could not find overloaded function %s for arguments: %s" % (func.__name__,
            ", ".join(str(type(x).__name__) for x in list(args)+list(kwargs.keys()))))

    return partial(returned, func)

def switch(var: str, **kwargs):
    # goin to be useless when py3.10
    for k,v in kwargs.items():
        if var == k: v()

def between(string, char1, char2):
    """Returns a string between first occurence of char1 and last occurence of char2 (exclusive)"""
    if not char1 in string or not char2 in string: return ValueError("One of characters is not in the string.")
    return string.partition(char1)[2].rpartition(char2)[0]

def get_ip():
    """Returns a list with 2 elements: local ip and public ip"""
    import socket, requests
    return [socket.gethostbyname(socket.gethostname()), requests.get('https://api.ipify.org').text]

class Logger:
    def __init__(self, console : bool, file : Union[bool, str], timestamp : Union[bool, str] ="$day.$month.$year $hour:$minute:$second.$ms", sock: socket = None):
        self.console = console
        self.file = file
        self.timestamp = timestamp
        self.sock = sock
        self.io = None
        if file and not os.path.exists(file):
            self.io = open(file, 'w')
        elif file and os.path.exists(file):
            self.io = open(file, 'a')

    def _timestamp(self):
        if not self.timestamp: ts = ""
        else:
            dt = datetime.now()
            repl = {"$day": dt.day, "$month": dt.month, "$year": dt.year, "$hour": dt.hour, "$minute": dt.minute, "$second": dt.second, '$ms': dt.microsecond if len(str(dt.microsecond)) < 4 else int(str(dt.microsecond)[:-3])}
            ts = self.timestamp
            for k,v in repl.items():
                if len(str(v)) == 1: v = "0"+str(v)
                else: v = str(v)
                if k == '$ms' and len(str(v)) < 3: v = '0'+v
                ts = ts.replace(k,v)
            ts += " "
        return ts

    def _clog(self, content: str):
        ts = self._timestamp()
        print(ts + str(content))

    def _slog(self, content: str):
        ts = self._timestamp()
        self.sock.send(ts.encode('utf-8') + content.encode('utf-8'))

    def _flog(self, content: str):
        if not isinstance(content, str): content = str(content)
        ts = self._timestamp()
        self.io.write("\n" + ts + content)
        self.io.flush()

    def config(self, console=None, file=None, sock=None):
        if console is not None: self.console = console
        if file is not None:
            if file != False:
                self.file = file
                if os.path.exists(file):
                    self.io = open(file, 'a')
                else:
                    self.io = open(file, 'w')
            else:
                if self.io: self.io.close()
                self.io = None
                self.file = False
        if sock is not None:
            if type(sock) != socket: raise ValueError("sock argument must be a socket.socket")
            if self.sock: self.sock.close()
            self.sock = sock

    def log(self, msg: str):
        if self.console: self._clog(msg)
        if self.sock: self._slog(msg)
        if self.file: self._flog(msg)

    def clean(self):
        if self.io: self.io.truncate(0)

    def __del__(self):
        if self.io: self.io.close()
        if self.sock: self.sock.close()

class Config:
    def __init__(self, savepath, default):
        self.path = Path(savepath).resolve()
        self.default = default
        self.data : dict = None

    def save(self):
        with open(self.path, 'w') as f:
            f.write(json.dumps(self.data))

    def load(self):
        try:
            with open(self.path, 'r') as f:
                self.data = json.loads(f.read())
        except FileNotFoundError:
            self.data = self.default

    def get(self, key: Any, default: Any = None):
        return self.data.get(key, default)

    def set(self, key: Any, value: Any):
        self.data[key] = value

class DiscordManager:
    # TODO
    def mute(state: bool): ...
    def deafen(state: bool): ...

class MouseManager(mouse.Controller):
    def __init__(self):
        super().__init__()

    def logi_g7(self):
        self.click(mouse.Button.x1)

class KeyboardManager(keyboard.Controller):
    def __init__(self):
        super().__init__()