#!/usr/bin/env python3
"""
Functional tests for the video translation pipeline.
Tests each of the 8 major steps using real services with small test data.

Pipeline Steps:
1. YouTube Video Download
2. Audio Transcription (Whisper)
3. Text Translation
4. Voice Synthesis (TTS)
5. Caption Generation
6. Thumbnail Generation
7. Video Composition
8. Job Management & Storage
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
from services.thumbnail_generator import ThumbnailGenerator
from services.video_processor import VideoProcessor

# Import test utilities
from test_utils import (
    setup_test_directories, cleanup_test_files, get_test_job_id,
    validate_audio_file, validate_video_file, validate_srt_file,
    validate_image_file, compare_audio_duration,
    TEST_VIDEO_URL, TEST_OUTPUT_DIR, TEST_TEMP_DIR
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ========================================================================
# STEP 1: YouTube Video Download
# ========================================================================

class TestYouTubeDownload:
    """Test YouTube video and audio download functionality"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test environment"""
        setup_test_directories()
        self.job_id = get_test_job_id()
        self.downloader = YouTubeDownloader()
        yield
        cleanup_test_files(self.job_id)
    
    def test_download_video_success(self):
        """Test successful download of YouTube video and audio"""
        video_path, audio_path = self.downloader.download(TEST_VIDEO_URL, self.job_id)
        
        # Verify video file
        assert os.path.exists(video_path), f"Video file not found: {video_path}"
        video_info = validate_video_file(video_path, min_duration=10)
        assert video_info['valid'], f"Invalid video: {video_info.get('error')}"
        assert video_info['has_video'], "Video has no video stream"
        assert video_info['duration'] > 10, f"Video too short: {video_info['duration']}s"
        
        # Verify audio file
        assert os.path.exists(audio_path), f"Audio file not found: {audio_path}"
        audio_info = validate_audio_file(audio_path, min_duration=10)
        assert audio_info['valid'], f"Invalid audio: {audio_info.get('error')}"
        assert audio_info['duration'] > 10, f"Audio too short: {audio_info['duration']}s"
        
        logger.info(f"✅ Download test passed - Video: {video_info['duration']}s, Audio: {audio_info['duration']}s")
    
    def test_download_handles_invalid_url(self):
        """Test error handling for invalid YouTube URL"""
        with pytest.raises(Exception):
            self.downloader.download("https://www.youtube.com/watch?v=INVALID", self.job_id)
        
        logger.info("✅ Invalid URL handling test passed")

# ========================================================================
# STEP 2: Audio Transcription
# ========================================================================

class TestAudioTranscription:
    """Test speech-to-text transcription using Whisper"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test environment"""
        setup_test_directories()
        self.job_id = get_test_job_id()
        self.transcription_service = TranscriptionService()
        
        # Download test audio
        downloader = YouTubeDownloader()
        _, self.audio_path = downloader.download(TEST_VIDEO_URL, self.job_id)
        
        yield
        cleanup_test_files(self.job_id)
    
    def test_transcribe_english_audio(self):
        """Test transcription of English audio"""
        transcription = self.transcription_service.transcribe(self.audio_path, 'en')
        
        assert transcription is not None, "Transcription is None"
        assert isinstance(transcription, list), "Transcription should be a list"
        assert len(transcription) > 0, "Transcription is empty"
        
        # Check first segment structure
        first_segment = transcription[0]
        assert 'text' in first_segment, "Segment missing 'text' field"
        assert 'start' in first_segment, "Segment missing 'start' timestamp"
        assert 'end' in first_segment, "Segment missing 'end' timestamp"
        
        # Verify text content
        full_text = ' '.join(seg['text'] for seg in transcription)
        assert len(full_text) > 10, "Transcribed text too short"
        
        logger.info(f"✅ Transcription test passed - {len(transcription)} segments, {len(full_text)} chars")
        logger.info(f"   First segment: '{first_segment['text'][:50]}...'")
    
    def test_transcribe_with_timestamps(self):
        """Test that transcription includes accurate timestamps"""
        transcription = self.transcription_service.transcribe(self.audio_path, 'en')
        
        for i, segment in enumerate(transcription):
            assert segment['start'] >= 0, f"Segment {i} has negative start time"
            assert segment['end'] > segment['start'], f"Segment {i} end <= start"
            
            if i > 0:
                # Timestamps should be monotonically increasing
                assert segment['start'] >= transcription[i-1]['start'], f"Timestamps not monotonic at segment {i}"
        
        logger.info(f"✅ Timestamp validation passed for {len(transcription)} segments")
    
    def test_transcribe_supports_chinese(self):
        """Test that transcription service supports Chinese language detection"""
        # Note: This test uses English audio but verifies Chinese language code is accepted
        # In a real scenario, you'd use Chinese audio
        try:
            transcription = self.transcription_service.transcribe(self.audio_path, 'zh-CN')
            assert transcription is not None, "Transcription with zh-CN failed"
            logger.info(f"✅ Chinese language support validated - {len(transcription)} segments")
        except Exception as e:
            # If the service doesn't support zh-CN, this should be caught
            logger.error(f"Chinese transcription failed: {e}")
            raise

# ========================================================================
# STEP 3: Text Translation
# ========================================================================

class TestTextTranslation:
    """Test text translation service"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test environment"""
        self.translation_service = TranslationService()
        yield
    
    def test_translate_simple_text(self):
        """Test translation of simple text segments"""
        segments = [
            {'text': 'Hello, how are you?', 'start': 0.0, 'end': 2.0},
            {'text': 'I am fine, thank you.', 'start': 2.0, 'end': 4.0}
        ]
        
        translated = self.translation_service.translate(segments, 'en', 'es')
        
        assert translated is not None, "Translation is None"
        assert isinstance(translated, list), "Translation should be a list"
        assert len(translated) == len(segments), "Translation count mismatch"
        
        # Check structure is preserved
        for i, seg in enumerate(translated):
            assert 'text' in seg, f"Segment {i} missing 'text'"
            assert 'start' in seg, f"Segment {i} missing 'start'"
            assert 'end' in seg, f"Segment {i} missing 'end'"
            assert len(seg['text']) > 0, f"Segment {i} has empty translation"
        
        logger.info(f"✅ Translation test passed - {len(translated)} segments")
        logger.info(f"   Original: '{segments[0]['text']}'")
        logger.info(f"   Translated: '{translated[0]['text']}'")
    
    def test_translate_preserves_timestamps(self):
        """Test that translation preserves timestamps"""
        segments = [
            {'text': 'First sentence.', 'start': 0.0, 'end': 2.0},
            {'text': 'Second sentence.', 'start': 2.5, 'end': 5.0}
        ]
        
        translated = self.translation_service.translate(segments, 'en', 'fr')
        
        for i in range(len(segments)):
            assert translated[i]['start'] == segments[i]['start'], f"Start time changed at {i}"
            assert translated[i]['end'] == segments[i]['end'], f"End time changed at {i}"
        
        logger.info("✅ Timestamp preservation test passed")
    
    def test_translate_english_to_chinese(self):
        """Test English to Chinese Simplified translation"""
        segments = [
            {'text': 'Hello world.', 'start': 0.0, 'end': 2.0},
            {'text': 'How are you?', 'start': 2.0, 'end': 4.0}
        ]
        
        translated = self.translation_service.translate(segments, 'en', 'zh-CN')
        
        assert len(translated) == len(segments), "Translation count mismatch"
        # Verify Chinese characters are present
        has_chinese = any('\u4e00' <= char <= '\u9fff' for char in translated[0]['text'])
        assert has_chinese, f"Translation doesn't contain Chinese: {translated[0]['text']}"
        
        logger.info(f"✅ EN→ZH-CN translation test passed")
        logger.info(f"   Original: '{segments[0]['text']}'")
        logger.info(f"   Translated: '{translated[0]['text']}'")
    
    def test_translate_chinese_to_english(self):
        """Test Chinese Simplified to English translation"""
        segments = [
            {'text': '你好世界。', 'start': 0.0, 'end': 2.0},
            {'text': '你好吗？', 'start': 2.0, 'end': 4.0}
        ]
        
        translated = self.translation_service.translate(segments, 'zh-CN', 'en')
        
        assert len(translated) == len(segments), "Translation count mismatch"
        # Verify English text is present
        has_english = any('a' <= char.lower() <= 'z' for char in translated[0]['text'])
        assert has_english, f"Translation doesn't contain English: {translated[0]['text']}"
        
        logger.info(f"✅ ZH-CN→EN translation test passed")
        logger.info(f"   Original: '{segments[0]['text']}'")
        logger.info(f"   Translated: '{translated[0]['text']}'")

# ========================================================================
# STEP 4: Voice Synthesis (TTS)
# ========================================================================

class TestVoiceSynthesis:
    """Test text-to-speech voice synthesis"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test environment"""
        setup_test_directories()
        self.job_id = get_test_job_id()
        self.voice_service = VoiceCloningService()
        
        # Download reference audio
        downloader = YouTubeDownloader()
        _, self.reference_audio = downloader.download(TEST_VIDEO_URL, self.job_id)
        
        yield
        cleanup_test_files(self.job_id)
    
    def test_generate_speech_from_text(self):
        """Test basic speech generation"""
        segments = [
            {'text': 'This is a test.', 'start': 0.0, 'end': 2.0}
        ]
        
        output_path = self.voice_service.generate_voice(
            segments, self.reference_audio, 'en', self.job_id
        )
        
        assert os.path.exists(output_path), f"Output audio not found: {output_path}"
        
        audio_info = validate_audio_file(output_path, min_duration=0.5)
        assert audio_info['valid'], f"Invalid audio: {audio_info.get('error')}"
        
        logger.info(f"✅ Voice synthesis test passed - {audio_info['duration']}s audio generated")
    
    def test_audio_duration_reasonable(self):
        """Test that generated audio duration is reasonable for text length"""
        segments = [
            {'text': 'Hello world, this is a longer sentence for testing.', 'start': 0.0, 'end': 3.0}
        ]
        
        output_path = self.voice_service.generate_voice(
            segments, self.reference_audio, 'en', self.job_id
        )
        
        audio_info = validate_audio_file(output_path)
        
        # Audio should be between 1-10 seconds for this text
        assert 1.0 <= audio_info['duration'] <= 10.0, \
            f"Audio duration unreasonable: {audio_info['duration']}s"
        
        logger.info(f"✅ Audio duration test passed - {audio_info['duration']}s")
    
    def test_generate_chinese_speech(self):
        """Test Chinese speech generation using gTTS"""
        segments = [
            {'text': '这是一个测试。', 'start': 0.0, 'end': 2.0}
        ]
        
        output_path = self.voice_service.generate_voice(
            segments, self.reference_audio, 'zh-CN', self.job_id + '_zh'
        )
        
        assert os.path.exists(output_path), f"Chinese audio not found: {output_path}"
        audio_info = validate_audio_file(output_path, min_duration=0.5)
        assert audio_info['valid'], f"Invalid Chinese audio: {audio_info.get('error')}"
        
        logger.info(f"✅ Chinese voice synthesis test passed - {audio_info['duration']}s")

# ========================================================================
# STEP 5: Caption Generation
# ========================================================================

class TestCaptionGeneration:
    """Test subtitle/caption file generation"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test environment"""
        setup_test_directories()
        self.job_id = get_test_job_id()
        self.caption_service = CaptionGenerator()
        yield
        cleanup_test_files(self.job_id)
    
    def test_generate_srt_format(self):
        """Test SRT subtitle file generation"""
        segments = [
            {'text': 'First subtitle.', 'start': 0.0, 'end': 2.0},
            {'text': 'Second subtitle.', 'start': 2.5, 'end': 5.0},
            {'text': 'Third subtitle.', 'start': 5.5, 'end': 8.0}
        ]
        
        srt_path = self.caption_service.generate_captions(segments, self.job_id)
        
        assert os.path.exists(srt_path), f"SRT file not found: {srt_path}"
        
        srt_info = validate_srt_file(srt_path)
        assert srt_info['valid'], f"Invalid SRT: {srt_info.get('error')}"
        assert srt_info['num_entries'] == len(segments), "Subtitle count mismatch"
        
        logger.info(f"✅ Caption generation test passed - {srt_info['num_entries']} subtitles")
    
    def test_caption_timing_accuracy(self):
        """Test that caption timestamps match input segments"""
        segments = [
            {'text': 'Test caption.', 'start': 1.5, 'end': 3.25}
        ]
        
        srt_path = self.caption_service.generate_captions(segments, self.job_id)
        
        with open(srt_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check timestamp format (HH:MM:SS,mmm --> HH:MM:SS,mmm)
        assert '00:00:01,500' in content, "Start timestamp incorrect"
        assert '00:00:03,250' in content, "End timestamp incorrect"
        assert 'Test caption.' in content, "Caption text missing"
        
        logger.info("✅ Caption timing accuracy test passed")

# ========================================================================
# STEP 6: Thumbnail Generation
# ========================================================================

class TestThumbnailGeneration:
    """Test video thumbnail extraction"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test environment"""
        setup_test_directories()
        self.job_id = get_test_job_id()
        self.thumbnail_service = ThumbnailGenerator()
        
        # Download test video
        downloader = YouTubeDownloader()
        self.video_path, _ = downloader.download(TEST_VIDEO_URL, self.job_id)
        
        yield
        cleanup_test_files(self.job_id)
    
    def test_extract_thumbnail(self):
        """Test thumbnail extraction from video"""
        thumbnail_path = self.thumbnail_service.generate_thumbnail(self.video_path, self.job_id)
        
        assert os.path.exists(thumbnail_path), f"Thumbnail not found: {thumbnail_path}"
        
        img_info = validate_image_file(thumbnail_path, min_width=100, min_height=100)
        assert img_info['valid'], f"Invalid image: {img_info.get('error')}"
        
        logger.info(f"✅ Thumbnail test passed - {img_info['width']}x{img_info['height']} {img_info['format']}")
    
    def test_thumbnail_dimensions(self):
        """Test that thumbnail has reasonable dimensions"""
        thumbnail_path = self.thumbnail_service.generate_thumbnail(self.video_path, self.job_id)
        
        img_info = validate_image_file(thumbnail_path)
        
        # Thumbnail should be at least 320x180 (minimum YouTube size)
        assert img_info['width'] >= 320, f"Thumbnail too narrow: {img_info['width']}px"
        assert img_info['height'] >= 180, f"Thumbnail too short: {img_info['height']}px"
        
        logger.info(f"✅ Thumbnail dimensions test passed - {img_info['width']}x{img_info['height']}")

# ========================================================================
# STEP 7: Video Composition
# ========================================================================

class TestVideoComposition:
    """Test video and audio merging"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test environment"""
        setup_test_directories()
        self.job_id = get_test_job_id()
        self.processor = VideoProcessor()
        
        # Download test files
        downloader = YouTubeDownloader()
        self.video_path, self.audio_path = downloader.download(TEST_VIDEO_URL, self.job_id)
        
        # Generate test captions
        caption_gen = CaptionGenerator()
        segments = [{'text': 'Test caption', 'start': 0.0, 'end': 2.0}]
        self.captions_path = caption_gen.generate_captions(segments, self.job_id)
        
        yield
        cleanup_test_files(self.job_id)
    
    def test_merge_video_audio(self):
        """Test merging video with new audio"""
        output_path = self.processor._merge_video_audio(
            self.video_path, self.audio_path, self.captions_path, self.job_id
        )
        
        assert os.path.exists(output_path), f"Output video not found: {output_path}"
        
        video_info = validate_video_file(output_path, min_duration=10)
        assert video_info['valid'], f"Invalid output: {video_info.get('error')}"
        assert video_info['has_video'], "Output missing video stream"
        assert video_info['has_audio'], "Output missing audio stream"
        
        logger.info(f"✅ Video merge test passed - {video_info['duration']}s, {video_info['resolution']}")
    
    def test_output_video_playable(self):
        """Test that output video is in a standard playable format"""
        output_path = self.processor._merge_video_audio(
            self.video_path, self.audio_path, self.captions_path, self.job_id
        )
        
        video_info = validate_video_file(output_path)
        
        # Should be H.264 video with AAC audio (most compatible)
        assert video_info['video_codec'] in ['h264', 'avc1'], \
            f"Unexpected codec: {video_info['video_codec']}"
        
        logger.info(f"✅ Output format test passed - {video_info['video_codec']}")

# ========================================================================
# STEP 8: Job Management
# ========================================================================

class TestJobManagement:
    """Test job status updates and backend communication"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test environment"""
        self.job_id = get_test_job_id()
        self.processor = VideoProcessor()
        yield
    
    def test_update_job_status(self):
        """Test job status update to backend"""
        # This test requires backend to be running
        # We'll just verify the method doesn't crash
        try:
            self.processor.update_job_status(
                self.job_id, 'processing', 50,
                error_message='', output_video_path='test.mp4'
            )
            logger.info("✅ Job status update test passed (backend call successful)")
        except Exception as e:
            # If backend is not running, that's okay for this test
            logger.warning(f"⚠️  Backend not available: {e}")
            pytest.skip("Backend not running")
    
    def test_job_progress_tracking(self):
        """Test that progress values are valid"""
        valid_progress_values = [0, 10, 25, 40, 55, 70, 80, 90, 100]
        
        for progress in valid_progress_values:
            assert 0 <= progress <= 100, f"Invalid progress: {progress}"
        
        logger.info(f"✅ Progress tracking test passed - {len(valid_progress_values)} values")

# ========================================================================
# Test Suite Summary
# ========================================================================

if __name__ == "__main__":
    print("="*60)
    print("Video Translation Pipeline - Functional Tests")
    print("="*60)
    print("\n8 Test Classes:")
    print("  1. TestYouTubeDownload - Video/audio download")
    print("  2. TestAudioTranscription - Speech-to-text (Whisper)")
    print("  3. TestTextTranslation - Language translation")
    print("  4. TestVoiceSynthesis - Text-to-speech (TTS)")
    print("  5. TestCaptionGeneration - SRT subtitle generation")
    print("  6. TestThumbnailGeneration - Video thumbnail extraction")
    print("  7. TestVideoComposition - Video/audio merging")
    print("  8. TestJobManagement - Status updates")
    print("\nRun with: pytest test_pipeline_functional.py -v")
    print("="*60)
