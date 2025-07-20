from flask import Flask, render_template, request, redirect, url_for, flash
import yt_dlp
import os
import sys
import subprocess
import platform
import stat
import requests
import zipfile
import io

app = Flask(__name__)
app.secret_key = "supersecretkey"

DESTINO = "downloads"
FFMPEG_DIR = os.path.join(os.getcwd(), "ffmpeg")

def install_ffmpeg():
    try:
        print("Instalando FFmpeg...")
        system = platform.system()
        
        if system == "Windows":
           
            ffmpeg_url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
            response = requests.get(ffmpeg_url)
            zip_file = zipfile.ZipFile(io.BytesIO(response.content))
            
            
            zip_file.extractall(FFMPEG_DIR)
            
            
            ffmpeg_path = os.path.join(FFMPEG_DIR, "ffmpeg-master-latest-win64-gpl", "bin")
            os.environ["PATH"] += os.pathsep + ffmpeg_path
            
        elif system == "Linux":
            
            subprocess.run(["sudo", "apt", "update"], check=True)
            subprocess.run(["sudo", "apt", "install", "-y", "ffmpeg"], check=True)
            
        elif system == "Darwin":  
            
            subprocess.run(["brew", "install", "ffmpeg"], check=True)
            
        print("FFmpeg instalado correctamente")
        return True
    except Exception as e:
        print(f"Error instalando FFmpeg: {e}")
        return False

def check_ffmpeg():
    try:
        subprocess.run(["ffmpeg", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        return True
    except:
        return install_ffmpeg()

if not os.path.exists(DESTINO):
    os.makedirs(DESTINO)


check_ffmpeg()

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        url = request.form.get("url").strip()
        if not url:
            flash("Por favor, ingresa una URL válida.", "error")
            return redirect(url_for("index"))

        opciones = {
            "format": "bestaudio/best",
            "outtmpl": f"{DESTINO}/%(title)s.%(ext)s",
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }],
            "noplaylist": True,
        }

        try:
            with yt_dlp.YoutubeDL(opciones) as ydl:
                ydl.download([url])
            flash("El audio se ha descargado exitosamente.", "success")
        except Exception as e:
            flash(f"No se pudo descargar el audio: {e}", "error")

        return redirect(url_for("index"))

    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)