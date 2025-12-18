import os
import yt_dlp
import logging

logger = logging.getLogger(__name__)

class YouTubeDownloader:
    """Download videos from YouTube with multiple fallback strategies"""
    
    def __init__(self):
        self.temp_dir = 'temp'
        os.makedirs(self.temp_dir, exist_ok=True)
    
    def download(self, youtube_url, job_id):
        """Download video and audio from YouTube URL with fallback strategies"""
        video_output = f"{self.temp_dir}/{job_id}_video.mp4"
        audio_output = f"{self.temp_dir}/{job_id}_audio.wav"
        
        # Try multiple download strategies in order of reliability
        strategies = [
            self._get_ios_config(),
            self._get_android_tv_config(),
            self._get_web_config(),
            self._get_basic_config(),
        ]
        
        last_error = None
        for i, strategy_name in enumerate(['ios', 'android_tv', 'web', 'basic']):
            try:
                logger.info(f"Attempting download with {strategy_name} strategy...")
                common_opts = strategies[i]
                
                # Download video
                video_opts = {
                    **common_opts,
                    'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                    'outtmpl': video_output,
                }
                
                with yt_dlp.YoutubeDL(video_opts) as ydl:
                    logger.info(f"Downloading video from {youtube_url}")
                    ydl.download([youtube_url])
                
                # Download audio separately in high quality
                audio_opts = {
                    **common_opts,
                    'format': 'bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'wav',
                    }],
                    'outtmpl': f"{self.temp_dir}/{job_id}_audio",
                }
                
                with yt_dlp.YoutubeDL(audio_opts) as ydl:
                    logger.info(f"Downloading audio from {youtube_url}")
                    ydl.download([youtube_url])
                
                logger.info(f"✅ Download successful with {strategy_name} strategy")
                return video_output, audio_output
                
            except Exception as e:
                last_error = e
                logger.warning(f"⚠️ {strategy_name} strategy failed: {str(e)}")
                # Clean up partial downloads
                for file in [video_output, audio_output]:
                    if os.path.exists(file):
                        os.remove(file)
                continue
        
        # If all strategies failed, raise the last error
        error_msg = f"All download strategies failed. Last error: {str(last_error)}"
        logger.error(f"❌ {error_msg}")
        raise Exception(error_msg)
    
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
