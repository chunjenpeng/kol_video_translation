#!/usr/bin/env python3
"""
Bidirectional Translation Tests
Tests both en→zh-CN and zh-CN→en translation workflows
"""

import os
import pytest
import logging
from pathlib import Path

# Import services to test
from services.youtube_downloader import YouTubeDownloader
from services.transcription_service import TranscriptionService
from services.translation_service import TranslationService
from services.voice_cloning_service import VoiceCloningService
from services.caption_generator import CaptionGenerator

# Import test utilities
from test_utils import (
    setup_test_directories, cleanup_test_files, get_test_job_id,
    validate_audio_file, TEST_VIDEO_URL
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ========================================================================
# Bidirectional Translation Tests
# ========================================================================

class TestBidirectionalTranslation:
    """Test translation in both directions: en→zh-CN and zh-CN→en"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test environment"""
        setup_test_directories()
        self.job_id = get_test_job_id()
        self.translation_service = TranslationService()
        self.voice_service = VoiceCloningService()
        
        # Download reference audio for voice synthesis
        downloader = YouTubeDownloader()
        _, self.reference_audio = downloader.download(TEST_VIDEO_URL, self.job_id)
        
        yield
        cleanup_test_files(self.job_id)
    
    def test_translate_english_to_chinese(self):
        """Test translation from English to Chinese Simplified"""
        segments = [
            {'text': 'Hello, how are you today?', 'start': 0.0, 'end': 2.0},
            {'text': 'The weather is very nice.', 'start': 2.5, 'end': 4.5},
            {'text': 'I hope you have a great day!', 'start': 5.0, 'end': 7.0}
        ]
        
        translated = self.translation_service.translate(segments, 'en', 'zh-CN')
        
        assert translated is not None, "Translation is None"
        assert isinstance(translated, list), "Translation should be a list"
        assert len(translated) == len(segments), "Translation count mismatch"
        
        # Verify Chinese characters are present
        for i, seg in enumerate(translated):
            assert 'text' in seg, f"Segment {i} missing 'text'"
            assert len(seg['text']) > 0, f"Segment {i} has empty translation"
            # Check for Chinese characters (Unicode range)
            has_chinese = any('\u4e00' <= char <= '\u9fff' for char in seg['text'])
            assert has_chinese, f"Segment {i} doesn't contain Chinese characters: {seg['text']}"
        
        logger.info(f"✅ EN→ZH-CN translation test passed - {len(translated)} segments")
        logger.info(f"   Original: '{segments[0]['text']}'")
        logger.info(f"   Translated: '{translated[0]['text']}'")
    
    def test_translate_chinese_to_english(self):
        """Test translation from Chinese Simplified to English"""
        segments = [
            {'text': '你好，今天过得怎么样？', 'start': 0.0, 'end': 2.0},
            {'text': '天气很好。', 'start': 2.5, 'end': 4.0},
            {'text': '祝你有美好的一天！', 'start': 4.5, 'end': 6.5}
        ]
        
        translated = self.translation_service.translate(segments, 'zh-CN', 'en')
        
        assert translated is not None, "Translation is None"
        assert isinstance(translated, list), "Translation should be a list"
        assert len(translated) == len(segments), "Translation count mismatch"
        
        # Verify English text is present
        for i, seg in enumerate(translated):
            assert 'text' in seg, f"Segment {i} missing 'text'"
            assert len(seg['text']) > 0, f"Segment {i} has empty translation"
            # Check for English letters
            has_english = any('a' <= char.lower() <= 'z' for char in seg['text'])
            assert has_english, f"Segment {i} doesn't contain English letters: {seg['text']}"
        
        logger.info(f"✅ ZH-CN→EN translation test passed - {len(translated)} segments")
        logger.info(f"   Original: '{segments[0]['text']}'")
        logger.info(f"   Translated: '{translated[0]['text']}'")
    
    def test_voice_synthesis_english(self):
        """Test voice generation for English text"""
        segments = [
            {'text': 'This is a test in English.', 'start': 0.0, 'end': 2.0}
        ]
        
        output_path = self.voice_service.generate_voice(
            segments, self.reference_audio, 'en', self.job_id + '_en'
        )
        
        assert os.path.exists(output_path), f"English audio not found: {output_path}"
        
        audio_info = validate_audio_file(output_path, min_duration=0.5)
        assert audio_info['valid'], f"Invalid English audio: {audio_info.get('error')}"
        
        logger.info(f"✅ English voice synthesis test passed - {audio_info['duration']}s")
    
    def test_voice_synthesis_chinese(self):
        """Test voice generation for Chinese text using gTTS"""
        segments = [
            {'text': '这是一个中文测试。', 'start': 0.0, 'end': 2.0}
        ]
        
        output_path = self.voice_service.generate_voice(
            segments, self.reference_audio, 'zh-CN', self.job_id + '_zh'
        )
        
        assert os.path.exists(output_path), f"Chinese audio not found: {output_path}"
        
        audio_info = validate_audio_file(output_path, min_duration=0.5)
        assert audio_info['valid'], f"Invalid Chinese audio: {audio_info.get('error')}"
        
        logger.info(f"✅ Chinese voice synthesis test passed - {audio_info['duration']}s")
    
    def test_full_pipeline_english_to_chinese(self):
        """Test complete pipeline: English transcription → Chinese translation → Chinese audio"""
        # Simulate English transcription
        english_segments = [
            {'text': 'Welcome to the test.', 'start': 0.0, 'end': 2.0},
            {'text': 'This tests the full pipeline.', 'start': 2.5, 'end': 4.5}
        ]
        
        # Translate to Chinese
        chinese_segments = self.translation_service.translate(english_segments, 'en', 'zh-CN')
        assert len(chinese_segments) == 2, "Translation failed"
        
        # Generate Chinese audio
        audio_path = self.voice_service.generate_voice(
            chinese_segments, self.reference_audio, 'zh-CN', self.job_id + '_pipeline_zh'
        )
        
        assert os.path.exists(audio_path), "Chinese audio generation failed"
        audio_info = validate_audio_file(audio_path)
        assert audio_info['valid'], "Generated Chinese audio is invalid"
        
        logger.info(f"✅ Full EN→ZH-CN pipeline test passed")
        logger.info(f"   EN: '{english_segments[0]['text']}'")
        logger.info(f"   ZH: '{chinese_segments[0]['text']}'")
        logger.info(f"   Audio: {audio_info['duration']}s")
    
    def test_full_pipeline_chinese_to_english(self):
        """Test complete pipeline: Chinese transcription → English translation → English audio"""
        # Simulate Chinese transcription
        chinese_segments = [
            {'text': '欢迎参加测试。', 'start': 0.0, 'end': 2.0},
            {'text': '这测试完整的流程。', 'start': 2.5, 'end': 4.5}
        ]
        
        # Translate to English
        english_segments = self.translation_service.translate(chinese_segments, 'zh-CN', 'en')
        assert len(english_segments) == 2, "Translation failed"
        
        # Generate English audio
        audio_path = self.voice_service.generate_voice(
            english_segments, self.reference_audio, 'en', self.job_id + '_pipeline_en'
        )
        
        assert os.path.exists(audio_path), "English audio generation failed"
        audio_info = validate_audio_file(audio_path)
        assert audio_info['valid'], "Generated English audio is invalid"
        
        logger.info(f"✅ Full ZH-CN→EN pipeline test passed")
        logger.info(f"   ZH: '{chinese_segments[0]['text']}'")
        logger.info(f"   EN: '{english_segments[0]['text']}'")
        logger.info(f"   Audio: {audio_info['duration']}s")


# ========================================================================
# Test Suite Summary
# ========================================================================

if __name__ == "__main__":
    print("="*60)
    print("Bidirectional Translation Tests")
    print("="*60)
    print("\nTest Coverage:")
    print("  ✓ English → Chinese Simplified translation")
    print("  ✓ Chinese Simplified → English translation")
    print("  ✓ English voice synthesis (gTTS)")
    print("  ✓ Chinese voice synthesis (gTTS)")
    print("  ✓ Full EN→ZH-CN pipeline")
    print("  ✓ Full ZH-CN→EN pipeline")
    print("\nRun with: pytest test_bidirectional_translation.py -v")
    print("="*60)
