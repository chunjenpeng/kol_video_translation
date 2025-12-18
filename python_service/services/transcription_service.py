import whisper
import logging

logger = logging.getLogger(__name__)

class TranscriptionService:
    """Transcribe audio using OpenAI Whisper"""
    
    def __init__(self):
        # Load Whisper model (base model for faster processing, can use 'large' for better accuracy)
        logger.info("Loading Whisper model...")
        self.model = whisper.load_model("base")
        logger.info("Whisper model loaded successfully")
    
    def transcribe(self, audio_path, language):
        """Transcribe audio file to text"""
        logger.info(f"Transcribing audio: {audio_path}")
        
        # Transcribe using Whisper
        result = self.model.transcribe(
            audio_path,
            language=language,
            task='transcribe',
            verbose=False
        )
        
        # Extract segments with timestamps
        segments = []
        for segment in result['segments']:
            segments.append({
                'start': segment['start'],
                'end': segment['end'],
                'text': segment['text'].strip()
            })
        
        logger.info(f"Transcription completed: {len(segments)} segments")
        return segments
