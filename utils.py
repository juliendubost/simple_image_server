# coding:utf-8

import os
import urllib.parse as urlparse
import redis
from PIL import Image
from io import BytesIO, StringIO
from flask import Flask, request, send_file, redirect, render_template

# from media import sanitze, ratio, measurements
import random

ext2conttype2 = {
    "jpg": "JPEG",
    "jpeg": "JPEG",
    "png": "PNG",
    "gif": "GIF",
    "image/jpeg": "JPEG",
    "image/png": "PNG",
    "image/gif": "GIF",
    b"image/jpeg": "JPEG",
    b"image/png": "PNG",
    b"image/gif": "GIF",
}

REDIS_URL = urlparse.urlparse(
    os.environ.get("REDISCLOUD_URL", "redis://:@localhost:6379/")
)
r = redis.StrictRedis(
    host=REDIS_URL.hostname, port=REDIS_URL.port, password=REDIS_URL.password
)


def dump_keys():
    for src in r.keys():
        if len(src) == len("Image-0dfe0plo3om23kfnn1lb91adrtqlq0wl"):
            buf = BytesIO()
            buf.save(r.get(src))
            buf.seek(0)
            img = Image.open(buf)
            img.save(src.remove("Image-"))


def export_all():
    for i in r.keys():
        if len(i) == len("Image-pxrl4xd4er6a5kw5eeqx5oq0nlg8sg13"):
            buf = BytesIO()
            buf.write(r.get(i))
            buf.seek(0)
            content = r.get(i.replace(b"Image", b"Content-type"))
            img = Image.open(buf)
            img.save("export/%s.%s" % (i.decode("ascii"), ext2conttype2[content]))
