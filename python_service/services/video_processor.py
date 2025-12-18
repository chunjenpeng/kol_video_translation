import os
import logging
import json
import redis
from datetime import datetime
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
        
        # Initialize Redis connection
        redis_host = os.getenv('REDIS_HOST', 'localhost')
        redis_port = int(os.getenv('REDIS_PORT', 6379))
        self.redis = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
    
    def update_job_status(self, job_id, status, progress, error_message='', 
                         output_video_path='', captions_path='', thumbnail_path=''):
        """Update job status in Redis"""
        try:
            job_key = f"job:{job_id}"
            job_data_json = self.redis.get(job_key)
            
            if not job_data_json:
                logger.error(f"Job {job_id} not found in Redis during update")
                return

            job_data = json.loads(job_data_json)
            
            # Update fields
            job_data['status'] = status
            job_data['progress'] = progress
            if error_message:
                job_data['error_message'] = error_message
            if output_video_path:
                job_data['output_video_path'] = output_video_path
            if captions_path:
                job_data['captions_path'] = captions_path
            if thumbnail_path:
                job_data['thumbnail_path'] = thumbnail_path
            
            # Update timestamp
            job_data['updated_at'] = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
            
            # Save back to Redis
            self.redis.set(job_key, json.dumps(job_data))
            
        except Exception as e:
            logger.error(f"Error updating job status for {job_id}: {str(e)}")
    
    def process_video(self, job_id):
        """Process video through the entire pipeline"""
        try:
            logger.info(f"Starting processing for job {job_id}")
            
            # Fetch job details from Redis
            job_key = f"job:{job_id}"
            job_data_json = self.redis.get(job_key)
            if not job_data_json:
                logger.error(f"Job {job_id} not found in Redis")
                return
            
            job_data = json.loads(job_data_json)
            youtube_url = job_data.get('youtube_url')
            source_language = job_data.get('source_language')
            target_language = job_data.get('target_language')
            
            if not all([youtube_url, source_language, target_language]):
                error_msg = "Missing required job parameters (youtube_url, source_language, target_language)"
                logger.error(error_msg)
                self.update_job_status(job_id, 'failed', 0, error_msg)
                return

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
        
        # Use absolute path for shared volume
        output_path = f"/app/output/{job_id}_final.mp4"
        
        # Ensure output directory exists
        os.makedirs("/app/output", exist_ok=True)
        
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
