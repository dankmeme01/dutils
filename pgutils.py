import pygame
import pygame.freetype
from . import util
from enum import Enum, auto
from itertools import product
from pygame.constants import K_BACKSPACE, K_DELETE, MOUSEBUTTONDOWN
from pygame.locals import K_LEFT, K_RIGHT, K_ESCAPE, KEYDOWN, QUIT, K_SPACE, KEYUP
from functools import wraps

pygame.freetype.init()
pygame.font.init()
parsekey = {}
states = {}
curstate = None

def change_state(new_state):
    global curstate
    curstate = new_state

def state(state_name: str, fps: int = 60):
    def decorator(func):
        states[state_name] = (func, fps)
        return None
    return decorator

def run_app(default_state: str, screensize: tuple[int, int]):
    global curstate
    change_state(default_state)
    window = pygame.display.set_mode(screensize)
    clock = pygame.time.Clock()
    inp = PlayerInput()
    while curstate != None:
        gdz = states.get(curstate, None)
        if not gdz: raise ValueError("Invalid state: '" + str(curstate) + "'")
        events_ = pygame.event.get()
        for e in events_:
            if e.type == QUIT:
                change_state(None)
                break
        clock.tick(gdz[1])
        inp.tick()
        gdz[0](window, events_, inp, pygame.mouse.get_pressed(), pygame.mouse.get_pos())
        pygame.display.update()
    else:
        pygame.quit()

def col_to_row(columns):
    # convert columns to rows
    if not util.all_equal([len(x) for x in columns]):
        # gotta fill em up
        longest = sorted([len(x) for x in columns])[-1]
        ind = 0
        for i in columns:
            while len(i) < longest:
                i.append(None)
                if len(i) == longest: columns[ind] = i
            ind += 1
    rows = []
    for i in range(len(columns[0])):
        rows.append([])
    for i in columns:
        ind2 = 0
        for j in i:
            rows[ind2].append(j)
            ind2 += 1
    return rows

def row_to_col(rows):
    if len(rows) == 0: return []
    #back baby
    if not util.all_equal([len(x) for x in rows]):
        # gotta fill em up
        longest = sorted([len(x) for x in rows])[-1]
        ind = 0
        for i in rows:
            while len(i) < longest:
                i.append("")
                if len(i) == longest: rows[ind] = i
            ind += 1
    cols = []
    for i in range(len(rows[0])):
        cols.append([x[i] for x in rows])
    return cols

class PositionVars:
    def __init__(self, width: int, height: int):
        self.props = (width, height)
        self.LEFT = 0
        self.RIGHT = width
        self.TOP = 0
        self.BOTTOM = height
        self.HORMID = width / 2
        self.VERMID = height / 2


class TextEntry:
    def __init__(self,
                size=(200,50),
                default="",
                allowchars=None,
                unseltext=None,
                maxchar=20,
                selcolor=(160,160,160),
                unselcolor=(127,127,127),
                textcolor=(255,255,255),
                font=pygame.font.SysFont(pygame.font.get_fonts()[0], 10)):
        self.size = size
        self.surf = pygame.Surface(size)
        self.text = default
        self.max = maxchar
        self.selected = False
        self.selc = selcolor
        self.nsel = unselcolor
        self.font = font
        self.textc = textcolor
        self.nochar = unseltext
        self.allowed = allowchars

    def add(self,symbols):
        if type(symbols) != str: symbols = str(symbols)
        if len(self.text + symbols) > self.max: return False
        self.text += symbols
        return True

    def remove(self,amount=1):
        if len(self.text) < amount or amount == -1: self.text= ""
        else: self.text = self.text[:len(self.text)-amount]

    def mousebtn(self, mpos):
        if self.rect.collidepoint(mpos): self.selected= True
        else: self.selected= False

    def keydown(self, event):
        if self.selected:
            if event.key == K_BACKSPACE: return self.remove()
            if event.key == K_ESCAPE: self.selected = False
            if not self.allowed: return self.add(event.unicode)
            elif event.unicode in self.allowed: return self.add(event.unicode)

    def draw(self, pos, surface):
        self.surf.fill(self.selc if self.selected else self.nsel)
        self.rect = surface.blit(self.surf,pos)
        txt = self.nochar if self.nochar and not self.text and not self.selected else self.text
        text = self.font.render(txt,False,self.textc)
        rect = text.get_rect()
        rect.center = (pos[0] + self.size[0]/2, pos[1]+self.size[1]/2)
        surface.blit(text, rect)

    def get_text(self):
        return self.text

class FontManager:
    def __init__(self, fontpath, sysfont):
        self.manager = pygame.freetype.SysFont if sysfont else pygame.freetype.Font
        self.fonts = {1: self.manager(fontpath, 1)}
        self.path = fontpath

    def get(self,fontsize):
        if fontsize in self.fonts: return self.fonts[fontsize]
        self.fonts[fontsize] = self.manager(self.path, fontsize)
        return self.fonts[fontsize]

    def clear(self):
        self.fonts = {}

class FontsManager:
    def __init__(self):
        self.fonts = {}

    def add(self, id, fontpath, sysfont):
        self.fonts[id] = FontManager(fontpath, sysfont)
        return self

    def get(self, id):
        return self.fonts.get(id, None)

class Table:
    def __init__(self, rows, font, linec=(255, 255, 255), bgc=(127, 127, 127)):
        self.rows = rows
        self.cols = row_to_col(rows)
        self.font = font
        self.bg = bgc
        self.ltext = linec

    def update(self, rows):
        self.rows = rows
        self.cols = row_to_col(rows)

    def _calcsize(self):
        longest = (0,0)
        total = ""
        for i in self.cols:
            longest_ = ["", 0]
            for j in i:
                s = self.font.size(j)
                if s[0] > longest_[1]: longest_ = [j, s[0]]
            total += longest_[0]
        for i in self.rows:
            size = self.font.size(total)
            size = (size[0]+len(i)*20, size[1])
            if size[0] > longest[0]: longest = size
        k = 0.33
        return longest[0],(longest[1]+self.font.get_height()*k) * len(self.rows) +self.font.get_height()/4

    def draw(self, centpos, surf, nobox=False):
        size = self._calcsize()
        k = 2
        startpos = centpos[0]-size[0]/k
        top,bottom = (centpos[1]-size[1]/k, centpos[1]+size[1]/k)
        for index in range(len(self.cols)):
            i = self.cols[index]
            longest = 0
            for j in i:
                s = self.font.size(j)
                if s[0] > longest: longest = s[0]
            startpos += longest+20
            #if index == 0: pygame.draw.line(surf, self.ltext, (startpos-longest-20, top), (startpos-longest-20, bottom-1))
            if index != len(self.cols)-1: pygame.draw.line(surf, self.ltext, (startpos, top), (startpos, bottom-1))
            slot = 0
            for j in i:
                text = self.font.render(j, False, self.ltext)
                #surf.blit(text, text.get_rect(center=(startpos-longest/2-10, top+self.font.get_height()/1.25+slot*self.font.get_height())))
                surf.blit(text, text.get_rect(center=(startpos-longest/2-10, top+self.font.get_height()/1.25+slot*size[1]/len(self.rows))))
                slot += 1
        p1 = (int(centpos[0]-size[0]/k), int(centpos[1]-size[1]/k))
        #p2 = (int(centpos[0]+size[0]/k), int(centpos[1]-size[1]/k))
        p3 = (int(centpos[0]+size[0]/k), int(bottom))
        if not nobox: pygame.draw.rect(surf, self.ltext, (p1[0], p1[1], startpos-p1[0], p3[1]-p1[1]), 1)
        right = startpos
        startpos = top
        for i in self.rows:
            pygame.draw.line(surf, self.ltext, (p1[0], startpos), (right-1, startpos))
            startpos += size[1]/len(self.rows)

class CheckButton:
    def __init__(self, outc=(255, 255, 255), emptyc=(100, 100, 100), defaulton=False, size=10, callback=None, variable=None, sound=None):
        self.outl = outc
        self.emptyc = emptyc
        self.state = defaulton
        self.rect = None
        self.size = size
        self.callback = callback
        self.var = variable
        self.sound = sound

    def switch(self):
        self.state = not self.state
        if self.sound: self.sound.play()
        if self.var: self.var.set(self.state)
        if self.callback: self.callback(self.state)

    def on_click(self, pos):
        if self.rect and self.rect.collidepoint(pos):
            self.switch()

    def get_state(self):
        return self.state

    def draw(self, surface, pos):
        self.rect = pygame.draw.rect(surface, self.outl, (*pos, self.size, self.size), 1 if not self.state else 0)
        return self.rect

class Button:
    def __init__(self, bgc=(127,127,127), dims='adjust', callback=None, text=None, font=None, textc=(255,255,255)):
        self.bgc = bgc
        self.dims = dims
        self.callback = callback
        self.rect = None
        #self.size = font.size(text)
        if font: self.text = font.render(text, textc)
        self.size = (self.text[1].w, self.text[1].h)

    def mousebtn(self, pos):
        if self.rect and self.rect.collidepoint(pos):
            self.callback()

    def draw(self, surface, pos):
        if not self.dims or self.dims == "adjust": self.dims = (int(self.size[0]*1.7), int(self.size[1]*1.7))
        surf = pygame.Surface(self.dims)
        surf.fill(self.bgc)
        self.rect = surface.blit(surf, (pos[0]-self.dims[0]/2, pos[1]-self.dims[1]/2))
        #textr = self.text
        #textr.center = (pos[0]+self.dims[0]/2, pos[1]+self.dims[1]/2)
        #textr.center = (pos[0], pos[1])
        surface.blit(self.text[0], (pos[0]-self.dims[0]/4, pos[1]-self.dims[1]/4))

class Var:
    def __init__(self, value): self.val = value
    def __str__(self): return str(self.val)
    def __float__(self): return float(self.val)
    def get(self): return self.val
    def set(self, value): self.val = value

class Var2:
    def __init__(self, value: None): self.val = value
    def get(self): return self.val
    def set(self, value): self.val = value
    def __getattr__(self, __name: str):
        return getattr(self.val, __name)
    def __str__(self): return str(self.val)

class ProgressBar:
    def __init__(self, dims=(200, 16), bounds=(0, 100), default=0, buttons=False, emptyc=(120,120,120), fillc=(200, 200, 200), variable=None):
        self.value = default
        self.bounds = bounds
        if self.bounds[0] >= self.bounds[1]: raise ValueError("bounds argument must be two numbers where first is less than second")
        self.buttons = buttons
        self.dims = dims
        self.colors = (emptyc, fillc)
        self.var = variable

    def set(self, value):
        self.value = value
        self._maxcheck()
        if self.var: self.var.set(self.value)

    def get(self):
        return self.value

    def increment(self, amnt=1):
        self.set(self.value + amnt)

    def decrement(self, amnt):
        self.set(self.value - amnt)

    def _maxcheck(self):
        if self.value > self.bounds[1]:
            self.value = self.bounds[1]
        elif self.value < self.bounds[0]:
            self.value = self.bounds[0]

    def draw(self, surface, center):
        surf = pygame.Surface(self.dims)
        surf.fill(self.colors[0])
        self.rect = surface.blit(surf, (center[0]-self.dims[0]/2, center[1]-self.dims[1]/2))
        fillperc = self.value/(self.bounds[1]-self.bounds[0])
        filled = pygame.Surface((int(self.dims[0]*fillperc), self.dims[1]))
        filled.fill(self.colors[1])
        surface.blit(filled, (int(center[0]-self.dims[0]/2), center[1]-self.dims[1]/2))

class Slider:
    def __init__(self, dims=(200, 2), bounds=(0, 100), default=0, buttons=False, emptyc=(120,120,120), fillc=(200, 200, 200), variable=None, callback=None):
        if not default and variable: default = variable.get()
        self.value = default
        self.bounds = bounds
        if self.bounds[0] >= self.bounds[1]: raise ValueError("bounds argument must be two numbers where first is less than second")
        self.buttons = buttons
        self.dims = dims
        self.colors = (emptyc, fillc)
        self.var = variable
        self.callback = callback

    def set(self, value):
        self.value = value
        if self.var: self.var.set(self.value)
        if self.callback: self.callback(value)

    def get(self):
        return self.value

    def on_click(self, pos):
        # less go
        thickness: float = self.dims[1]
        center: float = self.rect.center[1]
        if (center-thickness*5) < pos[1] < (center+thickness*5):
            leftmost = self.rect.center[0]-self.dims[0]/2
            #pos = (leftmost, pos[1])
            if pos[0] < leftmost or pos[0] > (leftmost+self.dims[0]): return
            # some logic n math
            in_slider_distance = pos[0] - leftmost
            isd_ratio = in_slider_distance/self.dims[0]
            #ratio = self.dims[0]/(self.bounds[1]-self.bounds[0])
            #clickedperc = in_slider_distance / ratio
            clickedperc = self.bounds[0] + (self.bounds[1]-self.bounds[0])*isd_ratio
            if not isinstance(self.bounds[0], float) and not isinstance(self.bounds[1], float):
                clickedperc = round(clickedperc)
            self.set(clickedperc)

    def draw(self, surface, center):
        surf = pygame.Surface(self.dims)
        surf.fill(self.colors[0])
        self.rect = surface.blit(surf, (center[0]-self.dims[0]/2, center[1]-self.dims[1]/2))
        leftmost = self.rect.center[0]-self.dims[0]/2
        isdratio = (self.value - self.bounds[0]) /(self.bounds[1]-self.bounds[0])
        isd = isdratio*self.dims[0]
        fillperc = (isd)/self.dims[0]
        filled = pygame.Surface((int(self.dims[0]*fillperc), self.dims[1]))
        filled.fill(self.colors[1])
        surface.blit(filled, (int(center[0]-self.dims[0]/2), center[1]-self.dims[1]/2))

class PlayerInput:
    def __init__(self):
        self.pressed = None

    def tick(self):
        self.pressed = pygame.key.get_pressed()

    def down(self, *k):
        press = False
        for k_ in k:
            if self.pressed[k_]: press = True; break
        return press

class SoundManager:
    def __init__(self, volume: float = 1.0):
        self.sounds = {}
        self.volume = volume

    def check(self, name: str, should_exist: bool) -> None:
        if (name in self.sounds and not should_exist) or (name not in self.sounds and should_exist):
            raise ValueError("Sound with name of %s %s" % (name, "already exists" if not should_exist else "does not exist"))

    def add_sound(self, name, path):
        self.check(name, False)
        self.sounds[name] = path

    def del_sound(self, name):
        self.check(name, True)
        del self.sounds[name]

    def play_sound(self, name, volume_mult = 1.0):
        self.check(name, True)
        self.sounds[name].play(self.volume * volume_mult)

    def set_volume(self, vol: float):
        if not isinstance(vol, float) or not (0 <= vol <= 1.0):
            raise ValueError("Invalid volume, should be a float in range [0.0; 1.0]")
        self.volume = vol

if __name__ == '__main__':
    man = FontManager("times", True)
    import string
    from random import choice,randint
    rows = []
    rows2 = []
    rows3 = []
    for lmao in rows,rows2,rows3:
        for x in range(randint(1,5)):
            lmao.append([])
            for y in range(randint(1,6)):
                lmao[x].append("".join([choice(string.ascii_letters+string.digits) for z in range(randint(2,8))]))
    tab = Table(rows, man.get(10))
    tab2 = Table(rows2,man.get(15))
    tab3 = Table(rows3,man.get(20))
    pygame.init()
    screen = pygame.display.set_mode((800,600))
    run = True
    while run:
        screen.fill((0,0,0))
        tab.draw((400,100), screen)
        tab2.draw((400,300), screen)
        tab3.draw((400,500), screen)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: run = False
            if event.type == pygame.KEYDOWN: run = False