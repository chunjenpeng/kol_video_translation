import os
import yt_dlp
import logging
import time

logger = logging.getLogger(__name__)

class YouTubeDownloader:
    """Download videos from YouTube with multiple fallback strategies and retry logic"""
    
    def __init__(self):
        self.temp_dir = 'temp'
        os.makedirs(self.temp_dir, exist_ok=True)
        self.max_retries = 3
        self.retry_delay = 5  # seconds
    
    def download(self, youtube_url, job_id):
        """Download video and audio from YouTube URL with retry logic and fallback strategies"""
        video_output = f"{self.temp_dir}/{job_id}_video.mp4"
        audio_output = f"{self.temp_dir}/{job_id}_audio.wav"
        
        # Try multiple download strategies in order of reliability
        strategies = [
            ('ios', self._get_ios_config()),
            ('android_tv', self._get_android_tv_config()),
            ('web', self._get_web_config()),
            ('basic', self._get_basic_config()),
        ]
        
        last_error = None
        for strategy_name, config in strategies:
            try:
                logger.info(f"Attempting download with {strategy_name} strategy...")
                return self._download_with_retry(youtube_url, job_id, config, strategy_name)
                
            except Exception as e:
                last_error = e
                logger.warning(f"⚠️ {strategy_name} strategy failed: {str(e)}")
                # Clean up partial downloads
                for file in [video_output, audio_output]:
                    if os.path.exists(file):
                        os.remove(file)
                continue
        
        # If all strategies failed, raise detailed error
        error_msg = f"All download strategies failed. Last error: {str(last_error)}"
        logger.error(f"❌ {error_msg}")
        raise Exception(error_msg)
    
    def _download_with_retry(self, youtube_url, job_id, config, strategy_name):
        """Download with exponential backoff retry logic for transient failures"""
        video_output = f"{self.temp_dir}/{job_id}_video.mp4"
        audio_output = f"{self.temp_dir}/{job_id}_audio.wav"
        
        for attempt in range(self.max_retries):
            try:
                # Download video
                video_opts = {
                    **config,
                    'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                    'outtmpl': video_output,
                }
                
                with yt_dlp.YoutubeDL(video_opts) as ydl:
                    logger.info(f"Downloading video from {youtube_url} (attempt {attempt + 1}/{self.max_retries})")
                    ydl.download([youtube_url])
                
                # Download audio separately in high quality
                audio_opts = {
                    **config,
                    'format': 'bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'wav',
                    }],
                    'outtmpl': f"{self.temp_dir}/{job_id}_audio",
                }
                
                with yt_dlp.YoutubeDL(audio_opts) as ydl:
                    logger.info(f"Downloading audio from {youtube_url} (attempt {attempt + 1}/{self.max_retries})")
                    ydl.download([youtube_url])
                
                logger.info(f"✅ Download successful with {strategy_name} strategy")
                return video_output, audio_output
                
            except Exception as e:
                error_str = str(e).lower()
                # Check if it's a transient error (rate limiting, network issues)
                is_transient = any(keyword in error_str for keyword in [
                    'rate limit', 'too many requests', '429', 'timeout',
                    'connection', 'temporary', 'unavailable'
                ])
                
                if is_transient and attempt < self.max_retries - 1:
                    delay = self.retry_delay * (2 ** attempt)  # Exponential backoff
                    logger.warning(f"Transient error detected, retrying in {delay}s: {str(e)}")
                    time.sleep(delay)
                else:
                    raise  # Re-raise for final attempt or non-transient errors
    
    def _get_ios_config(self):
        """iOS client configuration - often works when Android fails"""
        return {
            'quiet': False,
            'no_warnings': False,
            'extractor_args': {
                'youtube': {
                    'player_client': ['ios'],
                    'player_skip': ['webpage'],
                }
            },
        }
    
    def _get_android_tv_config(self):
        """Android TV embedded client - good fallback"""
        return {
            'quiet': False,
            'no_warnings': False,
            'extractor_args': {
                'youtube': {
                    'player_client': ['tv_embedded'],
                }
            },
        }
    
    def _get_web_config(self):
        """Web client with user agent"""
        return {
            'quiet': False,
            'no_warnings': False,
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'extractor_args': {
                'youtube': {
                    'player_client': ['web'],
                }
            },
        }
    
    def _get_basic_config(self):
        """Basic configuration as last resort"""
        return {
            'quiet': False,
            'no_warnings': False,
        }
