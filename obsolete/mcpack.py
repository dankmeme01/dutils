# Make a minecraft texture pack with music
from pathlib import Path
from tkinter import filedialog, Tk
from json import dump
from os import getenv
from shutil import copy
from PIL import Image
from pydub import AudioSegment
from tqdm import tqdm

PACK_FORMAT = 7 # afaik 7 is for 1.16 and higher but im too lazy to check

class ResourcePack:
    def __init__(self, name = None, desc = None, imgpath = None):
        self.name = name
        self.desc = desc
        self.icon = imgpath
        self.assetpath = None
        self.localization = {}
        self.path = ResourcePack.get_tp_folder() / self.name
        try:
            if self.path.exists(): self.path.unlink()
        except PermissionError:
            print("Failed to delete existing folder. Please do it manually: " + str(self.path))
            exit(1)
        self.path.mkdir(exist_ok=True)

    @staticmethod
    def get_tp_folder():
        dotmc = Path(getenv("APPDATA")) / ".minecraft" / "resourcepacks"
        if not dotmc.exists():
            alternate = Path.home() / "tp_folder"
            print("Resource pack folder does not exist by path " + str(dotmc))
            print("Saving in " + str(alternate) + " instead\n")
            return alternate
        return dotmc

    def gen_meta(self):
        content = { "pack": { "pack_format": PACK_FORMAT, "description": str(self.desc) } }
        with open(self.path / "pack.mcmeta", "w") as f: dump(content, f, ensure_ascii=True, indent=4)

    def construct(self):
        self.gen_meta()
        if self.icon:
            # This is here just in case the format is not PNG
            img = Image.open(self.icon)
            img.save(self.path / "pack.png")
        (self.path / "assets").mkdir(exist_ok=True)
        self.assetpath = self.path / "assets" / "minecraft"
        self.assetpath.mkdir(exist_ok=True)

    def add_asset(self, path: str, asset: Path):
        # path is a string relative to ./assets/minecraft/, such as lang/en_us.json
        # asset if the path to the asset itself
        folder = self.assetpath / path
        folder.mkdir(exist_ok=True)
        copy(asset, folder)

    def add_localization(self, loc: str, loc_string: str, loc_value: str):
        if not loc in self.localization: self.localization[loc] = {}
        self.localization[loc][loc_string] = loc_value

    def save_localization(self):
        outpath = self.assetpath / "lang"
        outpath.mkdir(exist_ok=True)
        for k,v in self.localization.items():
            with open(outpath / (k + ".json"), "w") as f:
                dump(v, f, ensure_ascii=True, indent=4)

# end ResourcePack class file

songs = iter(["13", "cat", "blocks", "chirp", "far", "mall", "mellohi", "stal", "strad", "ward", "11", "wait"])
# Pigstep is not replaced because it is cool
def get_musics() -> list[tuple[str, Path, str]]:
    root = Tk()
    root.withdraw()
    root.wm_attributes('-topmost', 1)
    # Name of the music track and actual path to it
    # The name will be displayed in game (such as Now Playing: Never Gonna Give You Up)
    musics = []
    dontgen = False
    while True:
        if not dontgen:
            try:
                codename = next(songs)
            except StopIteration:
                print("Reached song limit, breaking")
                break
        name = input("Enter music name (leave empty for exit): ")
        if not name.strip(): break
        music = filedialog.askopenfilename(title="Select a music file", parent=root)

        # If the user cancels, dont generate another codename
        if music == None: dontgen = True
        else: dontgen = False

        path = Path(music)
        musics.append((name, path, codename))
    return musics

def format_music(path: Path, out: Path):
    AudioSegment.from_file(str(path)).export(str(out), format='ogg')

if __name__ == "__main__":
    pack = ResourcePack("MusicLib", "Music library generated with mcpack.py")
    pack.construct()
    music = get_musics()

    sounds = pack.assetpath / "sounds"
    sounds.mkdir(exist_ok=True)

    out = sounds / "records"
    out.mkdir(exist_ok=True)

    print("Formatting music and adding localization")
    for m in tqdm(music):
        format_music(m[1], out / (m[2] + ".ogg"))
        for i in ["en_us", "ru_ru"]:
            pack.add_localization(i, "item.minecraft.music_disc_" + m[2] + ".desc", m[0])
    pack.save_localization()
    print("Successfully saved!")