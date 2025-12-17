import os
import logging
from TTS.api import TTS
from pydub import AudioSegment

logger = logging.getLogger(__name__)

class VoiceCloningService:
    """Generate voice with cloning using TTS"""
    
    def __init__(self):
        # Initialize TTS model with voice cloning capability
        logger.info("Loading TTS model...")
        try:
            # Using Coqui TTS with XTTS model for voice cloning
            # Note: This requires TTS>=0.22.0
            self.tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")
            self.supports_voice_cloning = True
            logger.info("TTS model loaded successfully with voice cloning support")
        except Exception as e:
            logger.warning(f"Failed to load XTTS model: {str(e)}, falling back to basic TTS")
            self.tts = TTS("tts_models/en/ljspeech/tacotron2-DDC")
            self.supports_voice_cloning = False
    
    def generate_voice(self, translated_segments, original_audio_path, target_language, job_id):
        """Generate speech from translated text with voice cloning"""
        logger.info(f"Generating voice for {len(translated_segments)} segments")
        
        output_dir = f"temp/{job_id}_audio_segments"
        os.makedirs(output_dir, exist_ok=True)
        
        audio_segments = []
        
        # Generate audio for each segment
        for i, segment in enumerate(translated_segments):
            segment_path = f"{output_dir}/segment_{i}.wav"
            
            try:
                # Generate speech with voice cloning if available
                if self.supports_voice_cloning:
                    self.tts.tts_to_file(
                        text=segment['text'],
                        file_path=segment_path,
                        speaker_wav=original_audio_path,  # Use original voice for cloning
                        language=target_language
                    )
                else:
                    # Fallback to basic TTS without cloning
                    self.tts.tts_to_file(
                        text=segment['text'],
                        file_path=segment_path
                    )
                
                # Load the generated audio segment
                audio = AudioSegment.from_wav(segment_path)
                
                # Calculate silence duration between segments
                if i > 0:
                    silence_duration = (segment['start'] - translated_segments[i-1]['end']) * 1000
                    if silence_duration > 0:
                        silence = AudioSegment.silent(duration=silence_duration)
                        audio_segments.append(silence)
                
                audio_segments.append(audio)
                
            except Exception as e:
                logger.error(f"Error generating audio for segment {i}: {str(e)}")
                # Add silence if generation fails
                duration = (segment['end'] - segment['start']) * 1000
                audio_segments.append(AudioSegment.silent(duration=duration))
        
        # Combine all audio segments
        if audio_segments:
            combined_audio = sum(audio_segments)
            output_path = f"output/{job_id}_translated_audio.wav"
            combined_audio.export(output_path, format="wav")
            logger.info(f"Combined audio saved to {output_path}")
            return output_path
        
        raise Exception("No audio segments generated")
