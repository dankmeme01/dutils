from pathlib import Path
from ..util import Pathlike, randname, NotInstalledError
from PIL import Image as PImage

def asave(image: PImage.Image, path: Pathlike):
    path = Pathlike(path)
    if not path.is_dir(): path = path.parent
    try:
        sname = Path(image.filename).name
    except AttributeError:
        sname = randname(10, 'png')
    image.save(path / sname)

try:
    import img2pdf
    def pdf_from_images(images: list[Pathlike], outputname: Pathlike = None):
        if outputname is None: outputname = Path.cwd() / "output.pdf"
        outputname = Pathlike(outputname)
        if outputname.exists(): outputname.unlink()
        with open(outputname.path, "wb") as f:
            images = [str(i) for i in images if not i.is_dir()]
            data = img2pdf.convert(images)
            f.write(data)

except (ImportError, ModuleNotFoundError):
    def pdf_from_images(*a, **kw):
        raise NotInstalledError("img2pdf", "pdf_from_images")

if __name__ == '__main__':
    PATH = r'C:\Users\User\OneDrive\Изображения\veryvery.png'
    img = PImage.open(Pathlike(PATH))
    new = img.resize((1024, 1024))
    asave(new, r'C:\Users\User\OneDrive\Изображения\Снимки экрана')