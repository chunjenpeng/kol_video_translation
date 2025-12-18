# Examples

This directory contains example code showing how to use the KOL Video Translation API.

## Available Examples

### Python Example (`example_usage.py`)

Demonstrates how to use the API with Python and the `requests` library.

**Requirements:**
```bash
pip install requests
```

**Usage:**
```bash
python example_usage.py
```

### Node.js Example (`example_usage.js`)

Demonstrates how to use the API with Node.js and the `axios` library.

**Requirements:**
```bash
npm install axios
```

**Usage:**
```bash
node example_usage.js
```

## What the Examples Do

1. **Get Supported Languages**: Fetch the list of available languages for translation
2. **Start Translation**: Submit a YouTube video for translation
3. **Monitor Progress**: Poll the job status until completion
4. **Download Result**: Download the translated video file

## Customizing the Examples

You can modify the examples to use different:
- YouTube URLs
- Source and target languages
- Polling intervals
- Timeout values

## Example Output

```
KOL Video Translation - Example Usage
==================================================

1. Getting supported languages...
   Found 12 supported languages:
   - English (en)
   - Spanish (es)
   - French (fr)
   - German (de)
   - Italian (it)
   ...

2. Starting translation job...
   YouTube URL: https://www.youtube.com/watch?v=...
   Source Language: en
   Target Language: es
   Job ID: 550e8400-e29b-41d4-a716-446655440000

3. Waiting for job to complete...
   (This may take several minutes...)
   Status: downloading - Progress: 10%
   Status: transcribing - Progress: 25%
   Status: translating - Progress: 40%
   Status: generating_voice - Progress: 55%
   Status: generating_captions - Progress: 70%
   Status: generating_thumbnail - Progress: 80%
   Status: completed - Progress: 100%

   ✓ Job completed successfully!
   Output Video: /app/output/550e8400_final.mp4
   Captions: /app/output/550e8400_captions.srt
   Thumbnail: /app/output/550e8400_thumbnail.jpg

4. Downloading translated video...
   ✓ Downloaded to: translated_video.mp4

✓ All done!
```

## API Integration Tips

1. **Error Handling**: Always wrap API calls in try-catch blocks
2. **Polling Interval**: Use 2-3 seconds between status checks
3. **Timeouts**: Set reasonable timeouts for long-running operations
4. **Validation**: Validate YouTube URLs before submission
5. **Storage**: Consider implementing local caching for results

## More Examples

For more advanced usage patterns, see the API documentation in `API.md`.
