import os
import yt_dlp
import logging

logger = logging.getLogger(__name__)

class YouTubeDownloader:
    """Download videos from YouTube"""
    
    def __init__(self):
        self.temp_dir = 'temp'
        os.makedirs(self.temp_dir, exist_ok=True)
    
    def download(self, youtube_url, job_id):
        """Download video and audio from YouTube URL"""
        video_output = f"{self.temp_dir}/{job_id}_video.mp4"
        audio_output = f"{self.temp_dir}/{job_id}_audio.wav"
        
        # Download video
        video_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'outtmpl': video_output,
            'quiet': False,
        }
        
        with yt_dlp.YoutubeDL(video_opts) as ydl:
            logger.info(f"Downloading video from {youtube_url}")
            ydl.download([youtube_url])
        
        # Download audio separately in high quality
        audio_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'wav',
            }],
            'outtmpl': f"{self.temp_dir}/{job_id}_audio",
            'quiet': False,
        }
        
        with yt_dlp.YoutubeDL(audio_opts) as ydl:
            logger.info(f"Downloading audio from {youtube_url}")
            ydl.download([youtube_url])
        
        return video_output, audio_output
