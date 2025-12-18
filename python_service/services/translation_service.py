from deep_translator import GoogleTranslator
import logging

logger = logging.getLogger(__name__)

class TranslationService:
    """Translate text between languages"""
    
    def translate(self, transcription_segments, source_language, target_language):
        """Translate transcription segments to target language"""
        logger.info(f"Translating from {source_language} to {target_language}")
        
        translator = GoogleTranslator(source=source_language, target=target_language)
        
        translated_segments = []
        for segment in transcription_segments:
            try:
                translated_text = translator.translate(segment['text'])
                translated_segments.append({
                    'start': segment['start'],
                    'end': segment['end'],
                    'text': translated_text
                })
            except Exception as e:
                logger.error(f"Error translating segment: {str(e)}")
                # Keep original text if translation fails
                translated_segments.append(segment)
        
        logger.info(f"Translation completed: {len(translated_segments)} segments")
        return translated_segments
