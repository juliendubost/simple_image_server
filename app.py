import os
import urllib.parse as urlparse
import redis
from PIL import Image
from io import BytesIO, StringIO
from flask import Flask, request, send_file, redirect, render_template
from media import sanitze, ratio, measurements
import random

from constant import MAX_FILE_SIZE


CHARACTERS = "azertyuiopqsdfghjklmwxcvbn0123456789"
REDIS_URL = urlparse.urlparse(
    os.environ.get("REDISCLOUD_URL", "redis://:@localhost:6379/")
)
r = redis.StrictRedis(
    host=REDIS_URL.hostname, port=REDIS_URL.port, password=REDIS_URL.password
)

app = Flask(__name__)
app.config["DEBUG"] = True
"""
if os.environ.get('DEVELOPMENT'):
    app.config['DEBUG'] = True
else:
    app.config['DEBUG'] = False
"""
ext2conttype2 = {
    "jpg": "JPEG",
    "jpeg": "JPEG",
    "png": "PNG",
    "gif": "GIF",
    "image/jpeg": "JPEG",
    "image/png": "PNG",
    "image/gif": "GIF",
}

ext2conttype = {
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
    "png": "image/png",
    "gif": "image/gif",
}

HTML_UPLOAD_GET_FORM_G111 = """
    <!doctype html>
    <title>Uploader</title>
    <h1>Uploader d'image privé pour garage111.com</h1>
    <h3>Choisissez un fichier et cliquez sur upload pour récupérer le lien de partage</h3>
    <form action="" method=post enctype=multipart/form-data>
    <p><input type=radio name=resize value="resize1024" checked>Retailler en 1024p de largeur (utilisation dans un 
    message)<br>
    <p><input type=radio name=resize value="noresize">Pas de modification de taille<br>
    <p><input type=file name=file>
    <input type=submit value=Upload>
    </form>
    <h4><b>Ce service est réservé aux uploads garage111, merci de ne pas diffuser l'URL d'upload publiquement</b></h4>
"""

HTML_UPLOAD_GET_FORM_SEVENER = """
    <!doctype html>
    <title>Uploader</title>
    <h1>Uploader d'image privé pour sevener.fr</h1>
    <h3>Choisissez un fichier et cliquez sur upload pour récupérer le lien de partage</h3>
    <form action="" method=post enctype=multipart/form-data>
    <p><input type=radio name=resize value="resize1024" checked>Retailler en 1024p de largeur (utilisation dans un 
    message)<br>
    <p><input type=radio name=resize value="noresize">Pas de modification de taille<br>
    <p><input type=file name=file>
    <input type=submit value=Upload>
    </form>
    <h4><b>Ce service est réservé aux uploads sevener.fr, merci de ne pas diffuser l'URL d'upload publiquement</b></h4>
"""


HTML_UPLOAD_POSTED = """
    <br>Votre image est <a href=%s>ici</a><br><br>
    Pour partager dans un message, copiez le lien ci-dessous et collez le dans votre message<br>
    <input type="text" value=[img]%s[/img] id="imglink">
    <button onclick="copyFunc()">Copier le lien</button>
    <script>
    function copyFunc() {
      var copyText = document.getElementById("imglink");
      copyText.select();
      document.execCommand("copy");
      alert("URL Copiée");
    }
    </script>
"""


@app.route("/g111deepweburl", methods=["GET", "POST"])
@app.route("/sevenerfrdeepweburl", methods=["GET", "POST"])
def uploader():
    if "sevener" in request.url:
        GET_FORM = HTML_UPLOAD_GET_FORM_SEVENER
    else:
        GET_FORM = HTML_UPLOAD_GET_FORM_G111
    if request.method == "POST":
        file = request.files["file"]
        if file and file.filename:
            filename = file.filename
            extension = filename[filename.rfind(".") + 1 :].lower()
            if extension not in ext2conttype:
                return "Extension '%s' non gérée, les extensions gérées sont %s" % (
                    extension,
                    ",".join(ext2conttype.keys()),
                )
            content_type = ext2conttype[extension]
            image = Image.open(file)
            resize = request.form["resize"] == "resize1024"
            if resize:
                image = resize_1024p(image)
            buff_img = BytesIO()
            image.seek(0)
            image.save(buff_img, ext2conttype2[extension])
            if buff_img.tell() > MAX_FILE_SIZE:
                return f"Le fichier est trop large, limite max : {MAX_FILE_SIZE/1000000} Mo"
            key = "%s" % "".join([random.choice(CHARACTERS) for _ in range(32)])
            r.set("Image-%s" % key, buff_img.getvalue())
            r.set("Content-type-%s" % key, content_type)
            r.set("Image-source-%s" % key, "garage111")
            buff_img.seek(0)
            get_url = request.url_root + key
            ret = HTML_UPLOAD_POSTED % (get_url, get_url)

            return ret
    return GET_FORM


@app.route("/<img_id>", methods=["GET"])
def get_image(img_id):
    if img_id == "favicon.ico":
        return ""
    data = r.get("Image-%s" % img_id)
    content_type = r.get("Content-type-%s" % img_id)
    buff = BytesIO()
    buff.write(data)
    buff.seek(0)
    print(content_type)
    return send_file(buff, mimetype=content_type.decode("ascii"))


def resize_1024p(img):
    target_width = 1024
    width, height = measurements(img, target_width)
    print("resize: %s %s" % (width, height))
#    return img.resize((width, height), Image.ANTIALIAS)
    return img.resize((width, height))


if __name__ == "__main__":
    app.run()
