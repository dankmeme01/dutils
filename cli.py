from colored import bg as _bg, fg as _fg, attr as _attr
from enum import Enum
import traceback
import inspect

class Color(Enum):
    # its a mess but whatever
    BLACK = 0
    RED = 1
    GREEN = 2
    YELLOW = 3
    BLUE = 4
    PURPLE = 5
    CYAN = 6
    WHITE = 7
    GRAY = 8
    ORANGE = 202
    OLIVE = "chartreuse_2b"
    BLURPLE = 111
    LIGHT_OLIVE = 191
    LIME = 119
    LIGHT_LIME = 82
    MAGENTA = 175
    LIGHT_BLUE = "dark_slate_gray_1"
    SKY_BLUE = "sky_blue_2"
    PALE_GREEN = "pale_green_1a"
    LIGHT_PINK = 197

RESET = _attr(0)

TEXT_SUCCESS = _fg(Color.GREEN.value)
TEXT_FAILURE = _fg(Color.RED.value)
TEXT_WARNING = _fg(Color.YELLOW.value)

def command(func):
    """Decorator which indicates that this is a command that should be executable and shown in help menu"""
    func.__is_cli_command__ = True
    return func

class CommandError(Exception):
    pass

class CommandLineInterface:
    def __init__(self, color = True):
        self.colored = color

    def color(self, text, fg = None, bg = None, attr_ = None, noreset = False):
        if not self.colored:
            return text

        base_text = text
        if fg is not None:
            base_text = _fg(fg.value) + base_text

        if bg is not None:
            base_text = _bg(bg.value) + base_text

        if attr_ is not None:
            base_text = attr_ + base_text

        if noreset is True:
            base_text += RESET

        return base_text

    def cprint(self, text, fg = None, bg = None, attr_ = None, noreset = False, *args, **kwargs):
        """Same as color, but also print it."""
        print(self.color(text, fg, bg, attr_, noreset), *args, **kwargs)

    @command
    def help(self):
        """List all the available commands"""
        for c in sorted(dir(self)):
            if c.startswith('_'):
                continue

            cmd = getattr(self, c)
            if not callable(cmd):
                continue

            if not getattr(cmd, '__is_cli_command__', False):
                continue

            doc = getattr(cmd, "__doc__", None)
            if not doc:
                doc = "No doc available"

            fullc = self.color(c, fg=Color.SKY_BLUE)
            args = inspect.getfullargspec(cmd)
            args, defaults = args[0], args[3]
            args = args[1:]
            sdef = len(args) - len(defaults if defaults else ()) # defaults start at this index
            for i, name in enumerate(args):
                if i >= sdef:
                    fullc += self.color(f' [{name}={defaults[i - sdef]!r}]', fg=Color.PALE_GREEN)
                else:
                    fullc += self.color(f' <{name}>', fg=Color.LIGHT_BLUE)

            print(f'{fullc} - {self.color(doc, fg=Color.OLIVE)}')

    def run_loop(self):
        while True:
            try:
                raw_inp = input(self.color('> ', fg=Color.GREEN)).strip().split(' ')
            except (KeyboardInterrupt, EOFError):
                print(RESET)
                exit(0)
            else:
                print(RESET, end='')

            if not raw_inp:
                continue

            cmd = getattr(self, raw_inp.pop(0).lower(), None)
            if not cmd or not getattr(cmd, '__is_cli_command__', False):
                self.cprint("Invalid command, type help for command list.", fg=Color.LIGHT_PINK)
                continue

            try:
                argspec = inspect.getfullargspec(cmd)
                minargs = len(argspec.args) - len(argspec.defaults if argspec.defaults else ()) - 1
                maxargs = len(argspec.args) - 1
                userargs = len(raw_inp)

                if not (minargs <= userargs <= maxargs):
                    self.cprint(f"Invalid amount of arguments passed: should be from {minargs} to {maxargs}.", fg=Color.LIGHT_PINK)
                    continue

                res = cmd(*raw_inp)
                if res is not None:
                    print(res)
            except CommandError as e:
                self.cprint(str(e), fg=Color.LIGHT_PINK)
            except Exception:
                traceback.print_exc()
