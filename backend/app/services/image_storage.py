"""Private local storage; not a public/static directory. No filenames from callers."""
import io
import re
import warnings
from pathlib import Path
from typing import Protocol
from PIL import Image, ImageOps, UnidentifiedImageError


class InvalidImage(ValueError):
    pass


def sanitize_image(data: bytes) -> bytes:
    try:
        with warnings.catch_warnings():
            warnings.simplefilter('error', Image.DecompressionBombWarning)
            with Image.open(io.BytesIO(data), formats=['JPEG', 'PNG']) as image:
                if image.width * image.height > 12_000_000 or getattr(image, 'n_frames', 1) != 1:
                    raise InvalidImage('Image dimensions or frame count are unsupported.')
                image.verify()
            with Image.open(io.BytesIO(data), formats=['JPEG', 'PNG']) as image:
                image.load()
                oriented = ImageOps.exif_transpose(image).convert('RGB')
                clean = Image.new('RGB', oriented.size)
                clean.paste(oriented)
                output = io.BytesIO()
                clean.save(output, format='PNG')
                return output.getvalue()
    except (UnidentifiedImageError, OSError, ValueError, SyntaxError,
            Image.DecompressionBombWarning, Image.DecompressionBombError) as error:
        raise InvalidImage('Use a valid single-frame JPEG or PNG up to 12 megapixels.') from error


class ImageStorage(Protocol):
    def put(self, key: str, content: bytes) -> None: ...
    def read(self, key: str) -> bytes: ...
    def delete(self, key: str) -> None: ...


class LocalImageStorage:
    def __init__(self, root: Path):
        self.root = root.resolve()

    def path(self, key: str) -> Path:
        if not re.fullmatch(r'[a-f0-9]{32}', key):
            raise ValueError('Invalid storage key.')
        target = self.root / f'{key}.png'
        if target.resolve().parent != self.root:
            raise ValueError('Invalid storage path.')
        return target

    def put(self, key: str, content: bytes) -> None:
        self.root.mkdir(parents=True, exist_ok=True, mode=0o700)
        with self.path(key).open('xb') as output:
            output.write(content)

    def read(self, key: str) -> bytes:
        return self.path(key).read_bytes()

    def delete(self, key: str) -> None:
        self.path(key).unlink(missing_ok=True)
