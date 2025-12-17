import os
import logging
import requests
from .youtube_downloader import YouTubeDownloader
from .transcription_service import TranscriptionService
from .translation_service import TranslationService
from .voice_cloning_service import VoiceCloningService
from .caption_generator import CaptionGenerator
from .thumbnail_generator import ThumbnailGenerator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VideoProcessor:
    """Main video processing pipeline"""
    
    def __init__(self):
        self.youtube_downloader = YouTubeDownloader()
        self.transcription_service = TranscriptionService()
        self.translation_service = TranslationService()
        self.voice_cloning_service = VoiceCloningService()
        self.caption_generator = CaptionGenerator()
        self.thumbnail_generator = ThumbnailGenerator()
        self.backend_url = os.getenv('BACKEND_API_URL', 'http://localhost:8080')
    
    def update_job_status(self, job_id, status, progress, error_message='', 
                         output_video_path='', captions_path='', thumbnail_path=''):
        """Update job status in the backend"""
        try:
            url = f"{self.backend_url}/api/v1/job/{job_id}"
            data = {
                'status': status,
                'progress': progress,
                'error_message': error_message,
                'output_video_path': output_video_path,
                'captions_path': captions_path,
                'thumbnail_path': thumbnail_path
            }
            response = requests.put(url, json=data)
            if response.status_code != 200:
                logger.error(f"Failed to update job status: {response.text}")
        except Exception as e:
            logger.error(f"Error updating job status: {str(e)}")
    
    def process_video(self, job_id, youtube_url, source_language, target_language):
        """Process video through the entire pipeline"""
        try:
            logger.info(f"Starting processing for job {job_id}")
            
            # Step 1: Download video from YouTube
            self.update_job_status(job_id, 'downloading', 10)
            video_path, audio_path = self.youtube_downloader.download(youtube_url, job_id)
            logger.info(f"Video downloaded: {video_path}")
            
            # Step 2: Transcribe audio
            self.update_job_status(job_id, 'transcribing', 25)
            transcription = self.transcription_service.transcribe(audio_path, source_language)
            logger.info(f"Transcription completed: {len(transcription)} segments")
            
            # Step 3: Translate transcription
            self.update_job_status(job_id, 'translating', 40)
            translated_text = self.translation_service.translate(
                transcription, source_language, target_language
            )
            logger.info(f"Translation completed")
            
            # Step 4: Generate voice with cloning
            self.update_job_status(job_id, 'generating_voice', 55)
            translated_audio_path = self.voice_cloning_service.generate_voice(
                translated_text, audio_path, target_language, job_id
            )
            logger.info(f"Voice generation completed: {translated_audio_path}")
            
            # Step 5: Generate captions
            self.update_job_status(job_id, 'generating_captions', 70)
            captions_path = self.caption_generator.generate_captions(
                translated_text, job_id
            )
            logger.info(f"Captions generated: {captions_path}")
            
            # Step 6: Generate thumbnail
            self.update_job_status(job_id, 'generating_thumbnail', 80)
            thumbnail_path = self.thumbnail_generator.generate_thumbnail(
                video_path, job_id
            )
            logger.info(f"Thumbnail generated: {thumbnail_path}")
            
            # Step 7: Merge video with new audio and captions
            self.update_job_status(job_id, 'completed', 90)
            output_video_path = self._merge_video_audio(
                video_path, translated_audio_path, captions_path, job_id
            )
            logger.info(f"Final video created: {output_video_path}")
            
            # Step 8: Update job as completed
            self.update_job_status(
                job_id, 'completed', 100, '',
                output_video_path, captions_path, thumbnail_path
            )
            logger.info(f"Job {job_id} completed successfully")
            
        except Exception as e:
            logger.error(f"Error processing job {job_id}: {str(e)}")
            self.update_job_status(job_id, 'failed', 0, str(e))
    
    def _merge_video_audio(self, video_path, audio_path, captions_path, job_id):
        """Merge video with new audio and add captions"""
        from moviepy.editor import VideoFileClip, AudioFileClip
        
        output_path = f"output/{job_id}_final.mp4"
        
        # Load video and new audio
        video = VideoFileClip(video_path)
        new_audio = AudioFileClip(audio_path)
        
        # Set the new audio to the video
        final_video = video.set_audio(new_audio)
        
        # Write the result
        final_video.write_videofile(output_path, codec='libx264', audio_codec='aac')
        
        # Close clips
        video.close()
        new_audio.close()
        final_video.close()
        
        return output_path
