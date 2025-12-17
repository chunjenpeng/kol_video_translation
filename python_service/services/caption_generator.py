import os
import logging

logger = logging.getLogger(__name__)

class CaptionGenerator:
    """Generate caption files (SRT format)"""
    
    def generate_captions(self, translated_segments, job_id):
        """Generate SRT caption file from translated segments"""
        logger.info(f"Generating captions for {len(translated_segments)} segments")
        
        output_path = f"output/{job_id}_captions.srt"
        
        with open(output_path, 'w', encoding='utf-8') as f:
            for i, segment in enumerate(translated_segments, start=1):
                # Write subtitle index
                f.write(f"{i}\n")
                
                # Write timestamps in SRT format (HH:MM:SS,mmm --> HH:MM:SS,mmm)
                start_time = self._format_timestamp(segment['start'])
                end_time = self._format_timestamp(segment['end'])
                f.write(f"{start_time} --> {end_time}\n")
                
                # Write subtitle text
                f.write(f"{segment['text']}\n")
                
                # Empty line between subtitles
                f.write("\n")
        
        logger.info(f"Captions saved to {output_path}")
        return output_path
    
    def _format_timestamp(self, seconds):
        """Convert seconds to SRT timestamp format (HH:MM:SS,mmm)"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        milliseconds = int((seconds % 1) * 1000)
        
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{milliseconds:03d}"
