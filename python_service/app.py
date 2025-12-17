from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
import threading
from services.video_processor import VideoProcessor

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Initialize video processor
video_processor = VideoProcessor()

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'python-video-processor'
    }), 200

@app.route('/api/process', methods=['POST'])
def process_video():
    """Process video translation request"""
    data = request.json
    
    # Validate required fields
    required_fields = ['job_id', 'youtube_url', 'source_language', 'target_language']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    # Process video in background thread
    thread = threading.Thread(
        target=video_processor.process_video,
        args=(
            data['job_id'],
            data['youtube_url'],
            data['source_language'],
            data['target_language']
        )
    )
    thread.daemon = True
    thread.start()
    
    return jsonify({
        'status': 'processing',
        'job_id': data['job_id']
    }), 202

if __name__ == '__main__':
    # Ensure output directory exists
    os.makedirs('output', exist_ok=True)
    os.makedirs('temp', exist_ok=True)
    
    port = int(os.getenv('PORT', 5000))
    # Disable debug mode in production for security
    # Debug mode should only be enabled in development with DEBUG=True env var
    debug_mode = os.getenv('DEBUG', 'False').lower() in ('true', '1', 'yes')
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
