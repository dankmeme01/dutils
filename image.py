from pathlib import Path
from .pyutils import Pathlike, randname
from PIL import Image as PImage

def asave(image: PImage.Image, path: Pathlike):
    path = Pathlike(path)
    if not path.is_dir(): path = path.parent
    try:
        sname = Path(image.filename).name
    except AttributeError:
        sname = randname(10, 'png')
    image.save(path / sname)



if __name__ == '__main__':
    PATH = r'C:\Users\User\OneDrive\Изображения\veryvery.png'
    img = PImage.open(Pathlike(PATH))
    new = img.resize((1024, 1024))
    asave(new, r'C:\Users\User\OneDrive\Изображения\Снимки экрана')