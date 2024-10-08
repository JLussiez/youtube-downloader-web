# -*- coding: utf-8 -*-
from datetime import datetime
from flask import render_template, request, redirect, url_for, flash, jsonify
from pytube import YouTube
import os
from moviepy.editor import VideoFileClip
from python1 import app

# Dossier de téléchargement par défaut
DOWNLOAD_FOLDER = os.path.join(os.path.expanduser("~"), "Downloads")

@app.route('/')
@app.route('/home')
def home():
    """Renders the home page with the download form."""
    return render_template(
        'index.html',
        title='Home Page',
        year=datetime.now().year,
    )

@app.route('/musics')
def musics():
    """Renders the musics page."""
    return render_template(
        'musics.html',
        title='musics',
        year=datetime.now().year,
        message='Your musics page.'
    )

@app.route('/download', methods=['POST'])
def download():
    """Handles the video download process."""
    video_url = request.form.get('url')
    output_format = request.form.get('format')
    selected_quality = request.form.get('quality')

    if video_url:
        try:
            # Téléchargement et conversion de la vidéo
            download_and_convert_video(video_url, output_format, selected_quality)
            flash(f"Vidéo téléchargée et convertie avec succès en {output_format}.", "success")
        except Exception as e:
            flash(f"Erreur lors du téléchargement : {str(e)}", "danger")

        return redirect(url_for("home"))
    else:
        flash("Veuillez entrer une URL valide.", "warning")
        return redirect(url_for("home"))

@app.route('/qualities', methods=['POST'])
def qualities():
    """Gets available video qualities for a given URL."""
    video_url = request.form.get('url')
    if video_url:
        try:
            qualities = get_available_qualities(video_url)
            return jsonify(qualities=qualities)
        except Exception as e:
            return jsonify(qualities=[], error=str(e))
    return jsonify(qualities=[])

def get_available_qualities(video_url):
    """Returns available video qualities for a given YouTube URL."""
    try:
        youtube_video = YouTube(video_url)
        qualities = [stream.resolution for stream in youtube_video.streams.filter(progressive=True, file_extension='mp4').order_by('resolution')]
        return qualities
    except Exception as e:
        print(f"Erreur lors de la récupération des qualités : {str(e)}")
        return []

def download_and_convert_video(video_url, output_format="mp4", selected_quality=None):
    """Downloads and converts YouTube video based on the selected options."""
    try:
        youtube_video = YouTube(video_url)

        # Sélectionner le flux vidéo en fonction de la qualité choisie
        if selected_quality:
            video_stream = youtube_video.streams.filter(res=selected_quality, progressive=True, file_extension='mp4').first()
        else:
            video_stream = youtube_video.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()

        os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

        # Télécharger la vidéo
        video_stream.download(DOWNLOAD_FOLDER)
        print("Téléchargement terminé.")

        # Conversion en fonction du format souhaité
        if output_format == "mp4":
            print(f"Vidéo disponible à l'emplacement : {DOWNLOAD_FOLDER}")
        elif output_format == "mp3":
            print("Conversion en MP3...")
            video_clip = VideoFileClip(os.path.join(DOWNLOAD_FOLDER, video_stream.default_filename))
            audio_clip = video_clip.audio
            if audio_clip:
                audio_filename = video_stream.default_filename.replace(".mp4", ".mp3")
                audio_clip.write_audiofile(os.path.join(DOWNLOAD_FOLDER, audio_filename))
                audio_clip.close()
                video_clip.close()
                os.remove(os.path.join(DOWNLOAD_FOLDER, video_stream.default_filename))
                print("Conversion terminée.")
    except Exception as e:
        print(f"Erreur lors du téléchargement ou de la conversion : {str(e)}")
