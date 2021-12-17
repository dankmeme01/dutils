import re

class Locale:
    def __init__(self, fullname, shortname):
        self.code = shortname
        self.name = fullname

    def __hash__(self):
        return hash(self.code)

class LocalizationString:
    def __init__(self, key, default_code, **kw):# locale=str
        self.tr = kw
        self.default = kw[default_code]
        self.key = key

    def get(self, locale=None):
        return self.tr.get(locale, self.default)

    def __str__(self):
        return self.get()

class LocalizationManager:
    def __init__(self, strings):
        self.strings = {}
        for s in strings:
            self.strings[s.key] = s

    def get(self, key) -> LocalizationString:
        if not isinstance(key, str):
            raise ValueError(f"Expected str, got '{type(key).__name__}'")
        if not key in self.strings:
            raise ValueError(f"String '{key}' was not found")
        return self.strings[key]

    @staticmethod
    def from_obj(locales: list, strings: list):
        locales = { x["code"]: Locale(x["name"], x["code"]) for x in locales }
        strings_ = [
            LocalizationString(
                key, list(s.keys())[0],
                **{locales[k].code: v for k,v in s.items()}
            )
            for key,s in strings.items()
        ]

        obj = LocalizationManager(strings_)
        return obj

def parse_str_fun(string: str, func) -> str:
    allvars = re.findall(r'(?<=\{)(.*?)(?=\})', string) # Searches for everything between {}
    for v in allvars:
        string = string.replace('{%s}' % v, func(v)) # Runs the func on found value

    return string

def parse_str(string: str, loc_manager: LocalizationManager = None, locale_code: str = None):
    return parse_str_fun(string, lambda key: loc_manager.get(key).get(locale_code))

del re