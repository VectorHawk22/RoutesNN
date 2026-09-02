# -*- coding: utf-8 -*-
"""PIL image loaders + Kivy texture conversion (pygame-free)."""
import os

from PIL import Image as PILImage
from PIL import ImageChops
from kivy.graphics.texture import Texture


def load_pil_cropped(filename, base_dir):
    """Load an RGBA image, cropping transparent borders (same as before)."""
    path = os.path.join(base_dir, filename)
    if not os.path.exists(path):
        return None
    try:
        img = PILImage.open(path).convert("RGBA")
        mask = img.getchannel("A").point(lambda a: 255 if a > 100 else 0)
        bbox = mask.getbbox()
        if bbox:
            img = img.crop(bbox)
        return img
    except Exception:
        return None


def _premultiply(img):
    r, g, b, a = img.split()
    r = ImageChops.multiply(r, a)
    g = ImageChops.multiply(g, a)
    b = ImageChops.multiply(b, a)
    return PILImage.merge("RGBA", (r, g, b, a))


def pil_to_texture(pil_img):
    """Premultiplied RGBA texture (Kivy uses premultiplied blending)."""
    img = _premultiply(pil_img)
    tex = Texture.create(size=img.size, colorfmt="rgba")
    tex.blit_buffer(img.tobytes(), colorfmt="rgba", bufferfmt="ubyte")
    tex.flip_vertical()
    return tex