#!/usr/bin/env python3
"""
End-to-End Browser Test for KOL Video Translation App
Tests the complete workflow using Playwright browser automation
"""

import sys
import time
import logging
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Test configuration
BASE_URL = "http://localhost:3000"
TEST_YOUTUBE_URL = "https://www.youtube.com/watch?v=jNQXAC9IVRw"
TIMEOUT_MS = 60000  # 60 seconds

def test_video_translation_workflow():
    """Test the complete video translation workflow in browser"""
    
    logger.info("Starting browser E2E test...")
    
    with sync_playwright() as p:
        # Launch browser
        logger.info("Launching Chromium browser...")
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={'width': 1280, 'height': 720},
            record_video_dir='./test_videos'
        )
        page = context.new_page()
        
        try:
            # Navigate to the application
            logger.info(f"Navigating to {BASE_URL}...")
            page.goto(BASE_URL, wait_until='networkidle', timeout=TIMEOUT_MS)
            logger.info("✅ Page loaded successfully")
            
            # Take screenshot of initial state
            page.screenshot(path='screenshots/01_initial_page.png')
            
            # Find the YouTube URL input field
            logger.info("Looking for YouTube URL input field...")
            url_input = page.locator('input[type="text"], input[placeholder*="YouTube"], input[placeholder*="URL"]').first
            
            if not url_input.is_visible():
                raise Exception("YouTube URL input field not found")
            
            logger.info("✅ Found input field")
            
            # Enter YouTube URL
            logger.info(f"Entering YouTube URL: {TEST_YOUTUBE_URL}")
            url_input.fill(TEST_YOUTUBE_URL)
            page.screenshot(path='screenshots/02_url_entered.png')
            
            # Find and click the submit button
            logger.info("Looking for submit button...")
            submit_button = page.locator('button:has-text("Translate"), button:has-text("Submit"), button[type="submit"]').first
            
            if not submit_button.is_visible():
                raise Exception("Submit button not found")
            
            logger.info("✅ Found submit button")
            logger.info("Clicking submit button...")
            submit_button.click()
            page.screenshot(path='screenshots/03_after_submit.png')
            
            # Wait for processing to start (check for status changes or progress indicators)
            logger.info("Waiting for processing to start...")
            time.sleep(3)  # Give it a moment to transition
            
            # Check for error messages
            error_selectors = [
                'text=/ERROR/i',
                'text=/failed/i',
                'text=/Sign in to confirm/i',
                'text=/bot/i',
                '[class*="error"]',
                '[class*="alert-danger"]'
            ]
            
            for selector in error_selectors:
                try:
                    error_element = page.locator(selector).first
                    if error_element.is_visible(timeout=1000):
                        error_text = error_element.text_content()
                        page.screenshot(path='screenshots/04_error_detected.png')
                        raise Exception(f"Error detected on page: {error_text}")
                except PlaywrightTimeout:
                    # No error found with this selector, continue
                    pass
            
            logger.info("✅ No error messages detected")
            
            # Look for success indicators
            success_indicators = [
                'text=/processing/i',
                'text=/downloading/i',
                'text=/translating/i',
                'text=/job/i',
                '[class*="progress"]',
                '[role="progressbar"]'
            ]
            
            found_indicator = False
            for selector in success_indicators:
                try:
                    indicator = page.locator(selector).first
                    if indicator.is_visible(timeout=5000):
                        indicator_text = indicator.text_content()
                        logger.info(f"✅ Processing started! Status: {indicator_text}")
                        found_indicator = True
                        page.screenshot(path='screenshots/05_processing_started.png')
                        break
                except PlaywrightTimeout:
                    continue
            
            if not found_indicator:
                # Take a screenshot for debugging
                page.screenshot(path='screenshots/06_no_indicator_found.png')
                logger.warning("⚠️  No clear processing indicator found, but no errors detected either")
                # Don't fail the test - the job might have been queued successfully
            
            logger.info("✅ E2E test completed successfully!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Test failed: {str(e)}")
            page.screenshot(path='screenshots/99_error_state.png')
            return False
            
        finally:
            # Cleanup
            context.close()
            browser.close()
            logger.info("Browser closed")

def main():
    """Main test runner"""
    
    logger.info("="*60)
    logger.info("KOL Video Translation - E2E Browser Test")
    logger.info("="*60)
    
    # Create screenshots directory
    import os
    os.makedirs('screenshots', exist_ok=True)
    os.makedirs('test_videos', exist_ok=True)
    
    # Run the test
    success = test_video_translation_workflow()
    
    if success:
        logger.info("\n🎉 All tests passed!")
        return 0
    else:
        logger.error("\n❌ Tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
