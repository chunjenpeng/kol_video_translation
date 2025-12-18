#!/usr/bin/env python3
"""
Test utilities for video translation pipeline functional tests.
Provides helper functions for creating test data, validating outputs, and cleanup.
"""

import os
import subprocess
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Test constants
TEST_VIDEO_URL = "https://www.youtube.com/watch?v=jNQXAC9IVRw"  # "Me at the zoo" - 19 seconds
TEST_OUTPUT_DIR = "test_output"
TEST_TEMP_DIR = "test_temp"

def setup_test_directories():
    """Create test output and temp directories"""
    os.makedirs(TEST_OUTPUT_DIR, exist_ok=True)
    os.makedirs(TEST_TEMP_DIR, exist_ok=True)
    logger.info(f"Test directories created: {TEST_OUTPUT_DIR}, {TEST_TEMP_DIR}")

def cleanup_test_files(job_id=None):
    """Remove test artifacts for a specific job or all test files"""
    import shutil
    
    if job_id:
        # Clean specific job files
        patterns = [
            f"{TEST_OUTPUT_DIR}/{job_id}*",
            f"{TEST_TEMP_DIR}/{job_id}*",
            f"temp/{job_id}*",
            f"output/{job_id}*",
        ]
        for pattern in patterns:
            for file in Path().glob(pattern):
                if file.is_file():
                    file.unlink()
                    logger.debug(f"Deleted: {file}")
    else:
        # Clean all test directories
        for dir_path in [TEST_OUTPUT_DIR, TEST_TEMP_DIR]:
            if os.path.exists(dir_path):
                shutil.rmtree(dir_path)
                logger.info(f"Cleaned directory: {dir_path}")

def validate_audio_file(file_path, min_duration=0):
    """
    Validate that an audio file exists and is valid.
    
    Args:
        file_path: Path to audio file
        min_duration: Minimum expected duration in seconds
    
    Returns:
        dict with validation results: {'valid': bool, 'duration': float, 'format': str}
    """
    if not os.path.exists(file_path):
        return {'valid': False, 'error': 'File does not exist'}
    
    try:
        # Use ffprobe to get audio info
        cmd = [
            'ffprobe', '-v', 'quiet',
            '-print_format', 'json',
            '-show_format', '-show_streams',
            file_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            return {'valid': False, 'error': 'ffprobe failed'}
        
        import json
        info = json.loads(result.stdout)
        
        duration = float(info.get('format', {}).get('duration', 0))
        audio_streams = [s for s in info.get('streams', []) if s.get('codec_type') == 'audio']
        
        if not audio_streams:
            return {'valid': False, 'error': 'No audio stream found'}
        
        audio_format = audio_streams[0].get('codec_name', 'unknown')
        
        valid = duration >= min_duration
        
        return {
            'valid': valid,
            'duration': duration,
            'format': audio_format,
            'sample_rate': audio_streams[0].get('sample_rate'),
            'channels': audio_streams[0].get('channels')
        }
    
    except Exception as e:
        return {'valid': False, 'error': str(e)}

def validate_video_file(file_path, min_duration=0):
    """
    Validate that a video file exists and is valid.
    
    Args:
        file_path: Path to video file
        min_duration: Minimum expected duration in seconds
    
    Returns:
        dict with validation results
    """
    if not os.path.exists(file_path):
        return {'valid': False, 'error': 'File does not exist'}
    
    try:
        cmd = [
            'ffprobe', '-v', 'quiet',
            '-print_format', 'json',
            '-show_format', '-show_streams',
            file_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            return {'valid': False, 'error': 'ffprobe failed'}
        
        import json
        info = json.loads(result.stdout)
        
        duration = float(info.get('format', {}).get('duration', 0))
        video_streams = [s for s in info.get('streams', []) if s.get('codec_type') == 'video']
        audio_streams = [s for s in info.get('streams', []) if s.get('codec_type') == 'audio']
        
        if not video_streams:
            return {'valid': False, 'error': 'No video stream found'}
        
        valid = duration >= min_duration and len(video_streams) > 0
        
        return {
            'valid': valid,
            'duration': duration,
            'has_video': len(video_streams) > 0,
            'has_audio': len(audio_streams) > 0,
            'video_codec': video_streams[0].get('codec_name') if video_streams else None,
            'resolution': f"{video_streams[0].get('width')}x{video_streams[0].get('height')}" if video_streams else None,
            'fps': eval(video_streams[0].get('r_frame_rate', '0/1')) if video_streams else None
        }
    
    except Exception as e:
        return {'valid': False, 'error': str(e)}

def validate_srt_file(file_path):
    """
    Validate that an SRT subtitle file is properly formatted.
    
    Returns:
        dict with validation results
    """
    if not os.path.exists(file_path):
        return {'valid': False, 'error': 'File does not exist'}
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Basic SRT format validation
        # Should have numbered entries with timestamps
        lines = content.strip().split('\n\n')
        
        if len(lines) == 0:
            return {'valid': False, 'error': 'Empty file'}
        
        # Check first entry format
        first_entry = lines[0].split('\n')
        if len(first_entry) < 3:
            return {'valid': False, 'error': 'Invalid SRT format'}
        
        # First line should be a number
        try:
            int(first_entry[0])
        except ValueError:
            return {'valid': False, 'error': 'First line should be entry number'}
        
        # Second line should contain timestamps
        if '-->' not in first_entry[1]:
            return {'valid': False, 'error': 'Missing timestamp separator'}
        
        return {
            'valid': True,
            'num_entries': len(lines),
            'file_size': len(content)
        }
    
    except Exception as e:
        return {'valid': False, 'error': str(e)}

def validate_image_file(file_path, min_width=0, min_height=0):
    """
    Validate that an image file exists and meets size requirements.
    
    Returns:
        dict with validation results
    """
    if not os.path.exists(file_path):
        return {'valid': False, 'error': 'File does not exist'}
    
    try:
        from PIL import Image
        
        img = Image.open(file_path)
        width, height = img.size
        format_name = img.format
        
        valid = width >= min_width and height >= min_height
        
        return {
            'valid': valid,
            'width': width,
            'height': height,
            'format': format_name,
            'mode': img.mode
        }
    
    except Exception as e:
        return {'valid': False, 'error': str(e)}

def compare_audio_duration(expected, actual, tolerance=0.5):
    """
    Compare two audio durations with tolerance.
    
    Args:
        expected: Expected duration in seconds
        actual: Actual duration in seconds
        tolerance: Acceptable difference in seconds
    
    Returns:
        bool: True if within tolerance
    """
    return abs(expected - actual) <= tolerance

def get_test_job_id():
    """Generate a unique test job ID"""
    import uuid
    return f"test_{uuid.uuid4().hex[:8]}"

def create_minimal_audio(output_path, duration=3, sample_rate=16000):
    """
    Create a minimal audio file for testing using ffmpeg.
    
    Args:
        output_path: Where to save the audio file
        duration: Duration in seconds
        sample_rate: Sample rate (Hz)
    """
    cmd = [
        'ffmpeg', '-f', 'lavfi', '-i',
        f'sine=frequency=440:duration={duration}:sample_rate={sample_rate}',
        '-y', output_path
    ]
    
    subprocess.run(cmd, capture_output=True, check=True)
    logger.info(f"Created test audio: {output_path}")

def create_minimal_video(output_path, duration=5, resolution='640x480'):
    """
    Create a minimal video file for testing using ffmpeg.
    
    Args:
        output_path: Where to save the video file
        duration: Duration in seconds
        resolution: Video resolution (WxH)
    """
    cmd = [
        'ffmpeg', '-f', 'lavfi', '-i',
        f'testsrc=duration={duration}:size={resolution}:rate=30',
        '-f', 'lavfi', '-i',
        f'sine=frequency=440:duration={duration}',
        '-y', output_path
    ]
    
    subprocess.run(cmd, capture_output=True, check=True)
    logger.info(f"Created test video: {output_path}")
