#!/usr/bin/env python3
"""
Example usage of the KOL Video Translation API using Python
"""

import requests
import time
import sys

API_BASE_URL = 'http://localhost:8080/api/v1'

def get_languages():
    """Get supported languages"""
    response = requests.get(f'{API_BASE_URL}/languages')
    response.raise_for_status()
    return response.json()['languages']

def start_translation(youtube_url, source_lang, target_lang):
    """Start a video translation job"""
    data = {
        'youtube_url': youtube_url,
        'source_language': source_lang,
        'target_language': target_lang
    }
    
    response = requests.post(f'{API_BASE_URL}/translate', json=data)
    response.raise_for_status()
    return response.json()['job_id']

def get_job_status(job_id):
    """Get the status of a translation job"""
    response = requests.get(f'{API_BASE_URL}/job/{job_id}')
    response.raise_for_status()
    return response.json()

def download_video(job_id, output_file='translated_video.mp4'):
    """Download the translated video"""
    response = requests.get(f'{API_BASE_URL}/download/{job_id}', stream=True)
    response.raise_for_status()
    
    with open(output_file, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    
    return output_file

def poll_until_complete(job_id, poll_interval=3, timeout=3600):
    """Poll job status until completion or timeout"""
    start_time = time.time()
    
    while True:
        # Check timeout
        if time.time() - start_time > timeout:
            raise TimeoutError(f"Job {job_id} did not complete within {timeout} seconds")
        
        # Get status
        status = get_job_status(job_id)
        
        print(f"Status: {status['status']} - Progress: {status['progress']}%")
        
        # Check if completed or failed
        if status['status'] == 'completed':
            return status
        elif status['status'] == 'failed':
            raise RuntimeError(f"Job failed: {status.get('error_message', 'Unknown error')}")
        
        # Wait before next poll
        time.sleep(poll_interval)

def main():
    """Main example function"""
    print("KOL Video Translation - Example Usage")
    print("=" * 50)
    
    # 1. Get supported languages
    print("\n1. Getting supported languages...")
    languages = get_languages()
    print(f"   Found {len(languages)} supported languages:")
    for lang in languages[:5]:  # Show first 5
        print(f"   - {lang['name']} ({lang['code']})")
    print("   ...")
    
    # 2. Example: Start a translation job
    print("\n2. Starting translation job...")
    
    # Use a short example video (replace with actual YouTube URL)
    youtube_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    source_lang = "en"
    target_lang = "es"
    
    print(f"   YouTube URL: {youtube_url}")
    print(f"   Source Language: {source_lang}")
    print(f"   Target Language: {target_lang}")
    
    job_id = start_translation(youtube_url, source_lang, target_lang)
    print(f"   Job ID: {job_id}")
    
    # 3. Poll for completion
    print("\n3. Waiting for job to complete...")
    print("   (This may take several minutes...)")
    
    try:
        final_status = poll_until_complete(job_id)
        print(f"\n   ✓ Job completed successfully!")
        print(f"   Output Video: {final_status.get('output_video_path')}")
        print(f"   Captions: {final_status.get('captions_path')}")
        print(f"   Thumbnail: {final_status.get('thumbnail_path')}")
        
        # 4. Download the result
        print("\n4. Downloading translated video...")
        output_file = download_video(job_id)
        print(f"   ✓ Downloaded to: {output_file}")
        
        print("\n✓ All done!")
        
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()
