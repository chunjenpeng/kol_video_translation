import os
import logging
from gtts import gTTS
from TTS.api import TTS
from pydub import AudioSegment

logger = logging.getLogger(__name__)

class VoiceCloningService:
    """Generate voice using gTTS for multilingual support with Coqui TTS as fallback"""
    
    def __init__(self):
        logger.info("Voice cloning service initialized with gTTS")
        # Initialize TTS model with voice cloning capability (for fallback/future use)
        try:
            self.tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")
            self.supports_voice_cloning = True
            logger.info("Coqui TTS model loaded as fallback")
        except Exception as e:
            logger.warning(f"Failed to load XTTS model: {str(e)}")
            self.tts = None
            self.supports_voice_cloning = False
        
        # Language code mapping from our format to gTTS format
        self.gtts_language_map = {
            'zh-CN': 'zh-CN',  # Chinese Simplified
            'zh-TW': 'zh-TW',  # Chinese Traditional
            'en': 'en',        # English
            'es': 'es',        # Spanish
            'fr': 'fr',        # French
            'de': 'de',        # German
            'it': 'it',        # Italian
            'pt': 'pt',        # Portuguese
            'ru': 'ru',        # Russian
            'ja': 'ja',        # Japanese
            'ko': 'ko',        # Korean
            'ar': 'ar',        # Arabic
            'hi': 'hi'         # Hindi
        }
    
    def generate_voice(self, translated_segments, original_audio_path, target_language, job_id):
        """Generate speech from translated text using gTTS"""
        logger.info(f"Generating voice for {len(translated_segments)} segments using gTTS")
        
        output_dir = f"temp/{job_id}_audio_segments"
        os.makedirs(output_dir, exist_ok=True)
        
        # Get the appropriate language code for gTTS
        gtts_lang = self.gtts_language_map.get(target_language, 'en')
        logger.info(f"Using gTTS language: {gtts_lang} for target language: {target_language}")
        
        audio_segments = []
        
        # Generate audio for each segment
        for i, segment in enumerate(translated_segments):
            segment_path = f"{output_dir}/segment_{i}.mp3"
            
            text = segment['text']
            if not text or len(text.strip()) == 0:
                # Add silence for empty segments
                duration = (segment['end'] - segment['start']) * 1000
                audio_segments.append(AudioSegment.silent(duration=duration))
                logger.warning(f"Segment {i} has no text, adding {duration}ms silence")
                continue
            
            try:
                # Generate speech using gTTS
                tts = gTTS(text=text, lang=gtts_lang, slow=False)
                tts.save(segment_path)
                logger.info(f"Generated audio for segment {i}: '{text[:50]}...'")
                
                # Load the generated audio segment
                audio = AudioSegment.from_mp3(segment_path)
                
                # Calculate silence duration between segments (if needed)
                if i > 0:
                    silence_duration = (segment['start'] - translated_segments[i-1]['end']) * 1000
                    if silence_duration > 0:
                        silence = AudioSegment.silent(duration=int(silence_duration))
                        audio_segments.append(silence)
                        logger.debug(f"Added {silence_duration}ms silence before segment {i}")
                
                audio_segments.append(audio)
                
            except Exception as e:
                logger.error(f"Error generating audio for segment {i} with gTTS: {str(e)}")
                # Add silence if generation fails
                duration = (segment['end'] - segment['start']) * 1000
                audio_segments.append(AudioSegment.silent(duration=int(duration)))
        
        # Combine all audio segments
        if audio_segments:
            combined_audio = sum(audio_segments)
            output_path = f"output/{job_id}_translated_audio.wav"
            combined_audio.export(output_path, format="wav")
            logger.info(f"Combined audio saved to {output_path}, total duration: {len(combined_audio)}ms")
            return output_path
        
        raise Exception("No audio segments generated")
