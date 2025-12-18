import os
import logging
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import VideoFileClip

logger = logging.getLogger(__name__)

class ThumbnailGenerator:
    """Generate video thumbnails"""
    
    def generate_thumbnail(self, video_path, job_id):
        """Generate thumbnail from video"""
        logger.info(f"Generating thumbnail from {video_path}")
        
        output_path = f"output/{job_id}_thumbnail.jpg"
        
        try:
            # Extract a frame from the video (at 1 second or middle of video)
            video = VideoFileClip(video_path)
            duration = video.duration
            
            # Get frame at 1 second or middle of video
            frame_time = min(1.0, duration / 2)
            frame = video.get_frame(frame_time)
            
            # Convert to PIL Image
            image = Image.fromarray(frame)
            
            # Resize to standard thumbnail size
            thumbnail_size = (1280, 720)
            image.thumbnail(thumbnail_size, Image.Resampling.LANCZOS)
            
            # Create a new image with the exact size (add black bars if needed)
            final_image = Image.new('RGB', thumbnail_size, (0, 0, 0))
            
            # Center the thumbnail
            x = (thumbnail_size[0] - image.size[0]) // 2
            y = (thumbnail_size[1] - image.size[1]) // 2
            final_image.paste(image, (x, y))
            
            # Save thumbnail
            final_image.save(output_path, 'JPEG', quality=95)
            
            video.close()
            
            logger.info(f"Thumbnail saved to {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error generating thumbnail: {str(e)}")
            
            # Create a simple placeholder thumbnail
            placeholder = Image.new('RGB', (1280, 720), (100, 100, 100))
            draw = ImageDraw.Draw(placeholder)
            
            # Add text
            text = "Video Thumbnail"
            bbox = draw.textbbox((0, 0), text)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            position = ((1280 - text_width) // 2, (720 - text_height) // 2)
            draw.text(position, text, fill=(255, 255, 255))
            
            placeholder.save(output_path, 'JPEG', quality=95)
            
            return output_path
