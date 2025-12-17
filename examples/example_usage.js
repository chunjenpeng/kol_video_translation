#!/usr/bin/env node
/**
 * Example usage of the KOL Video Translation API using Node.js
 */

const axios = require('axios');

const API_BASE_URL = 'http://localhost:8080/api/v1';

// Get supported languages
async function getLanguages() {
  const response = await axios.get(`${API_BASE_URL}/languages`);
  return response.data.languages;
}

// Start a video translation job
async function startTranslation(youtubeUrl, sourceLang, targetLang) {
  const response = await axios.post(`${API_BASE_URL}/translate`, {
    youtube_url: youtubeUrl,
    source_language: sourceLang,
    target_language: targetLang
  });
  return response.data.job_id;
}

// Get the status of a translation job
async function getJobStatus(jobId) {
  const response = await axios.get(`${API_BASE_URL}/job/${jobId}`);
  return response.data;
}

// Download the translated video
async function downloadVideo(jobId, outputFile = 'translated_video.mp4') {
  const response = await axios.get(`${API_BASE_URL}/download/${jobId}`, {
    responseType: 'stream'
  });
  
  const fs = require('fs');
  const writer = fs.createWriteStream(outputFile);
  
  response.data.pipe(writer);
  
  return new Promise((resolve, reject) => {
    writer.on('finish', () => resolve(outputFile));
    writer.on('error', reject);
  });
}

// Poll job status until completion or timeout
async function pollUntilComplete(jobId, pollInterval = 3000, timeout = 3600000) {
  const startTime = Date.now();
  
  while (true) {
    // Check timeout
    if (Date.now() - startTime > timeout) {
      throw new Error(`Job ${jobId} did not complete within ${timeout/1000} seconds`);
    }
    
    // Get status
    const status = await getJobStatus(jobId);
    
    console.log(`Status: ${status.status} - Progress: ${status.progress}%`);
    
    // Check if completed or failed
    if (status.status === 'completed') {
      return status;
    } else if (status.status === 'failed') {
      throw new Error(`Job failed: ${status.error_message || 'Unknown error'}`);
    }
    
    // Wait before next poll
    await new Promise(resolve => setTimeout(resolve, pollInterval));
  }
}

// Main example function
async function main() {
  console.log('KOL Video Translation - Example Usage');
  console.log('='.repeat(50));
  
  try {
    // 1. Get supported languages
    console.log('\n1. Getting supported languages...');
    const languages = await getLanguages();
    console.log(`   Found ${languages.length} supported languages:`);
    languages.slice(0, 5).forEach(lang => {
      console.log(`   - ${lang.name} (${lang.code})`);
    });
    console.log('   ...');
    
    // 2. Start a translation job
    console.log('\n2. Starting translation job...');
    
    // Use a short example video (replace with actual YouTube URL)
    const youtubeUrl = 'https://www.youtube.com/watch?v=dQw4w9WgXcQ';
    const sourceLang = 'en';
    const targetLang = 'es';
    
    console.log(`   YouTube URL: ${youtubeUrl}`);
    console.log(`   Source Language: ${sourceLang}`);
    console.log(`   Target Language: ${targetLang}`);
    
    const jobId = await startTranslation(youtubeUrl, sourceLang, targetLang);
    console.log(`   Job ID: ${jobId}`);
    
    // 3. Poll for completion
    console.log('\n3. Waiting for job to complete...');
    console.log('   (This may take several minutes...)');
    
    const finalStatus = await pollUntilComplete(jobId);
    console.log('\n   ✓ Job completed successfully!');
    console.log(`   Output Video: ${finalStatus.output_video_path}`);
    console.log(`   Captions: ${finalStatus.captions_path}`);
    console.log(`   Thumbnail: ${finalStatus.thumbnail_path}`);
    
    // 4. Download the result
    console.log('\n4. Downloading translated video...');
    const outputFile = await downloadVideo(jobId);
    console.log(`   ✓ Downloaded to: ${outputFile}`);
    
    console.log('\n✓ All done!');
    
  } catch (error) {
    console.error('\n✗ Error:', error.message);
    process.exit(1);
  }
}

// Run the example if this file is executed directly
if (require.main === module) {
  main();
}

module.exports = {
  getLanguages,
  startTranslation,
  getJobStatus,
  downloadVideo,
  pollUntilComplete
};
