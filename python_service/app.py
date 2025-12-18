from flask import Flask, jsonify
from flask_cors import CORS
import os
import redis
import threading
import logging
import time
from dotenv import load_dotenv
from services.video_processor import VideoProcessor

# Load environment variables
load_dotenv()

# Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('Worker')

app = Flask(__name__)
CORS(app)

# Initialize components
redis_host = os.getenv('REDIS_HOST', 'localhost')
redis_port = int(os.getenv('REDIS_PORT', 6379))

# Retry Redis connection
while True:
    try:
        rdb = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
        rdb.ping()
        logger.info("Connected to Redis successfully")
        break
    except redis.ConnectionError:
        logger.error("Failed to connect to Redis, retrying in 5 seconds...")
        time.sleep(5)

video_processor = VideoProcessor()

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    redis_status = 'up'
    try:
        rdb.ping()
    except:
        redis_status = 'down'
        
    return jsonify({
        'status': 'healthy',
        'service': 'python-video-processor-worker',
        'redis': redis_status
    }), 200

def worker_loop():
    """Background worker that pulls jobs from Redis"""
    logger.info("Worker started, listening for jobs...")
    while True:
        try:
            # BLPOP blocks until a job is available (timeout 0 means block indefinitely, but we use 10s to allow graceful shutdown check if needed)
            # Result is a tuple ('jobs_queue', 'job_id')
            item = rdb.blpop('jobs_queue', timeout=10)
            
            if item:
                job_id = item[1]
                logger.info(f"Received job: {job_id}")
                video_processor.process_video(job_id)
            
        except Exception as e:
            logger.error(f"Worker exception: {str(e)}")
            time.sleep(1)

if __name__ == '__main__':
    # Start worker in background thread
    worker_thread = threading.Thread(target=worker_loop, daemon=True)
    worker_thread.start()
    
    # Start Flask server for health checks
    port = int(os.getenv('PORT', 5000))
    # Disable debug mode in production
    debug_mode = os.getenv('DEBUG', 'False').lower() in ('true', '1', 'yes')
    
    logger.info(f"Starting Health Server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
