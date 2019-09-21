from PIL import Image
import requests
from io import BytesIO

def getImgSize(img):
    width, height = img.size
    return width, height

def getImgSizeURL(url):
    img = getImg(url)
    width, height = img.size
    return width, height

def getImg(url):
    response = requests.get(url)
    img = Image.open(BytesIO(response.content))
    return img
