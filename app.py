from fastapi import FastAPI, Form, Request, UploadFile, File
from fastapi.responses import FileResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pytube import YouTube
from pydub import AudioSegment
import os
import logging

app = FastAPI()
templates = Jinja2Templates(directory="templates")

app.mount("/static", StaticFiles(directory="static"), name="static")

logging.basicConfig(level=logging.INFO)

def download_youtube_audio(youtube_url: str, output_file_name: str, bitrate: str = "192k"):
    try:
        yt = YouTube(youtube_url)
        video = yt.streams.filter(only_audio=True).first()
        downloaded_file = video.download(filename='temp_audio')
        audio = AudioSegment.from_file(downloaded_file)
        audio.export(output_file_name, format="mp3", bitrate=bitrate)
        os.remove(downloaded_file)
        logging.info(f"Audio downloaded and saved as {output_file_name}")
    except Exception as e:
        logging.error(f"Failed to download audio: {e}")
        raise

def download_youtube_video(youtube_url: str, output_file_name: str, resolution: str = "720p"):
    try:
        yt = YouTube(youtube_url)
        video = yt.streams.filter(progressive=True, file_extension='mp4').get_by_resolution(resolution)
        if not video:
            video = yt.streams.filter(progressive=True, file_extension='mp4').first()
        video.download(filename=output_file_name)
        logging.info(f"Video downloaded and saved as {output_file_name}")
    except Exception as e:
        logging.error(f"Failed to download video: {e}")
        raise

@app.get("/")
async def read_form(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/download")
async def handle_form(url: str = Form(...), mode: str = Form(...), audio_quality: str = Form(None), resolution: str = Form(None)):
    output_file_name = ""
    try:
        if mode == 'audio':
            bitrate = audio_quality.replace('kbps', 'k')
            output_file_name = "output.mp3"
            download_youtube_audio(url, output_file_name, bitrate)
        elif mode == 'video':
            output_file_name = "output.mp4"
            download_youtube_video(url, output_file_name, resolution)
        return FileResponse(output_file_name, media_type='application/octet-stream', filename=output_file_name)
    except Exception as e:
        logging.error(f"Download failed: {e}")
        return JSONResponse(content={"error": "Download failed"}, status_code=500)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)
