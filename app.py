from flask import Flask, request, render_template, send_file
from pytube import YouTube
from pydub import AudioSegment
import os

app = Flask(__name__)

def download_youtube_audio(youtube_url, output_file_name, bitrate="192k"):
    yt = YouTube(youtube_url)
    video = yt.streams.filter(only_audio=True).first()
    downloaded_file = video.download(filename='temp_audio')
    audio = AudioSegment.from_file(downloaded_file)
    audio.export(output_file_name, format="mp3", bitrate=bitrate)
    os.remove(downloaded_file)

def download_youtube_video(youtube_url, output_file_name, resolution="720p"):
    yt = YouTube(youtube_url)
    video = yt.streams.filter(progressive=True, file_extension='mp4').get_by_resolution(resolution)
    if not video:
        video = yt.streams.filter(progressive=True, file_extension='mp4').first()
    video.download(filename=output_file_name)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        youtube_url = request.form['url']
        mode = request.form['mode']
        if mode == 'audio':
            bitrate = request.form['bitrate']
            output_file_name = "output.mp3"
            download_youtube_audio(youtube_url, output_file_name, bitrate)
        elif mode == 'video':
            resolution = request.form['resolution']
            output_file_name = "output.mp4"
            download_youtube_video(youtube_url, output_file_name, resolution)
        return send_file(output_file_name, as_attachment=True)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
