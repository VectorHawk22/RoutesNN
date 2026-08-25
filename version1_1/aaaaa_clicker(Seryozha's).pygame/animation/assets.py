import os
import pygame
from PIL import Image as PILImage


def load_cropped(filename, base_dir):
    path = os.path.join(base_dir, filename)
    if not os.path.exists(path):
        return None
    try:
        img = PILImage.open(path).convert("RGBA")
        mask = img.getchannel("A").point(lambda a: 255 if a > 100 else 0)
        bbox = mask.getbbox()
        if bbox:
            img = img.crop(bbox)
        data = img.tobytes()
        return pygame.image.fromstring(data, img.size, "RGBA").convert_alpha()
    except Exception as e:
        print(f"Error loading {filename}: {e}")
        return None


def pil_to_pygame(pil_img):
    data = pil_img.tobytes()
    return pygame.image.fromstring(data, pil_img.size, "RGBA").convert_alpha()


def load_pil_cropped(filename, base_dir):
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
