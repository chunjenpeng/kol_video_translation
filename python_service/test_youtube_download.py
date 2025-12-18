#!/usr/bin/env python3
"""
Functional test for yt-dlp YouTube download capability.
Tests different configurations to bypass bot detection.
"""

import os
import sys
import yt_dlp
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Test video URL - using a short, public domain video
TEST_URL = "https://www.youtube.com/watch?v=jNQXAC9IVRw"  # "Me at the zoo" - first YouTube video

def test_configuration(config_name, ydl_opts):
    """Test a specific yt-dlp configuration"""
    logger.info(f"\n{'='*60}")
    logger.info(f"Testing configuration: {config_name}")
    logger.info(f"{'='*60}")
    
    test_output = f"test_downloads/test_{config_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.makedirs("test_downloads", exist_ok=True)
    
    opts = {
        **ydl_opts,
        'outtmpl': f"{test_output}.%(ext)s",
        'quiet': False,
        'no_warnings': False,
    }
    
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            logger.info(f"Attempting download with {config_name}...")
            info = ydl.extract_info(TEST_URL, download=True)
            
            # Check if file was created
            output_file = f"{test_output}.mp4"
            if os.path.exists(output_file):
                file_size = os.path.getsize(output_file)
                logger.info(f"✅ SUCCESS! Downloaded: {output_file}")
                logger.info(f"   File size: {file_size / 1024 / 1024:.2f} MB")
                logger.info(f"   Video title: {info.get('title', 'N/A')}")
                logger.info(f"   Duration: {info.get('duration', 'N/A')} seconds")
                return True
            else:
                logger.error(f"❌ FAILED: File not created")
                return False
                
    except Exception as e:
        logger.error(f"❌ FAILED with error: {str(e)}")
        return False

def run_all_tests():
    """Run all test configurations"""
    
    results = {}
    
    # Configuration 1: Basic (likely to fail)
    results['basic'] = test_configuration(
        "basic",
        {
            'format': 'best[ext=mp4]/best',
        }
    )
    
    # Configuration 2: With User-Agent
    results['user_agent'] = test_configuration(
        "user_agent",
        {
            'format': 'best[ext=mp4]/best',
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        }
    )
    
    # Configuration 3: Android client (often works better)
    results['android_client'] = test_configuration(
        "android_client",
        {
            'format': 'best[ext=mp4]/best',
            'extractor_args': {
                'youtube': {
                    'player_client': ['android'],
                }
            },
        }
    )
    
    # Configuration 4: iOS client
    results['ios_client'] = test_configuration(
        "ios_client",
        {
            'format': 'best[ext=mp4]/best',
            'extractor_args': {
                'youtube': {
                    'player_client': ['ios'],
                }
            },
        }
    )
    
    # Configuration 5: Multiple clients with user-agent
    results['multi_client'] = test_configuration(
        "multi_client",
        {
            'format': 'best[ext=mp4]/best',
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'extractor_args': {
                'youtube': {
                    'player_client': ['android', 'ios', 'web'],
                }
            },
        }
    )
    
    # Configuration 6: Android with skip options
    results['android_skip'] = test_configuration(
        "android_skip",
        {
            'format': 'best[ext=mp4]/best',
            'extractor_args': {
                'youtube': {
                    'player_client': ['android'],
                    'player_skip': ['webpage'],
                }
            },
        }
    )
    
    # Configuration 7: TV embedded client
    results['tv_embedded'] = test_configuration(
        "tv_embedded",
        {
            'format': 'best[ext=mp4]/best',
            'extractor_args': {
                'youtube': {
                    'player_client': ['tv_embedded'],
                }
            },
        }
    )
    
    # Print summary
    logger.info(f"\n{'='*60}")
    logger.info("TEST SUMMARY")
    logger.info(f"{'='*60}")
    
    success_count = sum(1 for v in results.values() if v)
    total_count = len(results)
    
    for config, success in results.items():
        status = "✅ SUCCESS" if success else "❌ FAILED"
        logger.info(f"{config:20s}: {status}")
    
    logger.info(f"\nTotal: {success_count}/{total_count} configurations successful")
    
    if success_count > 0:
        logger.info("\n🎉 At least one configuration works!")
        logger.info("Successful configurations can be used in the main application.")
    else:
        logger.info("\n⚠️  All configurations failed. This might indicate:")
        logger.info("  - IP-based rate limiting from YouTube")
        logger.info("  - Need for OAuth authentication")
        logger.info("  - Need for browser cookies")
        logger.info("  - Geographic restrictions")
    
    return results

if __name__ == "__main__":
    logger.info("YouTube Download Functional Test")
    logger.info(f"Testing with URL: {TEST_URL}")
    logger.info(f"yt-dlp version: {yt_dlp.version.__version__}")
    
    results = run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if any(results.values()) else 1)
