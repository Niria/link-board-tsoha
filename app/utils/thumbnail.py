import base64
from io import BytesIO

import requests
from PIL import Image
from bs4 import BeautifulSoup


def b64encode(data):
    return base64.b64encode(data).decode()


def fetch_thumbnail(url, size=(64, 64)):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        og_image = soup.find("meta", property="og:image")
        if not og_image or not og_image.get("content"):
            raise ValueError
        og_image_url = og_image.get("content")

        image_response = requests.get(og_image_url)
        image_response.raise_for_status()
        image = Image.open(BytesIO(image_response.content))

        if image.mode != "RGB":
            image = image.convert("RGB")

        image.thumbnail(size)
        color = image.getpixel((0, 0))

        background = Image.new("RGB", size, color)
        background.paste(image, (
        (size[0] - image.size[0]) // 2, (size[1] - image.size[1]) // 2))

        byte_array = BytesIO()
        background.save(byte_array, format="PNG")
        return byte_array.getvalue()
    except ValueError:
        return None
