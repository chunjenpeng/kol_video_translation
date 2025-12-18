import React, { useState } from 'react';
import './VideoForm.css';

function VideoForm({ languages, onSubmit }) {
  const [youtubeUrl, setYoutubeUrl] = useState('');
  const [sourceLanguage, setSourceLanguage] = useState('en');
  const [targetLanguage, setTargetLanguage] = useState('zh-CN');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();

    // Validate YouTube URL
    if (!youtubeUrl.trim()) {
      alert('Please enter a YouTube URL');
      return;
    }

    // Proper YouTube URL validation to prevent URL injection
    const youtubeRegex = /^(https?:\/\/)?(www\.)?(youtube\.com\/watch\?v=|youtu\.be\/)[a-zA-Z0-9_-]{11}$/;
    if (!youtubeRegex.test(youtubeUrl.trim())) {
      alert('Please enter a valid YouTube URL (e.g., https://www.youtube.com/watch?v=...)');
      return;
    }

    if (sourceLanguage === targetLanguage) {
      alert('Source and target languages must be different');
      return;
    }

    setIsSubmitting(true);
    try {
      await onSubmit(youtubeUrl, sourceLanguage, targetLanguage);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="video-form">
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="youtube-url">YouTube URL</label>
          <input
            type="text"
            id="youtube-url"
            className="form-control"
            placeholder="https://www.youtube.com/watch?v=..."
            value={youtubeUrl}
            onChange={(e) => setYoutubeUrl(e.target.value)}
            disabled={isSubmitting}
            required
          />
        </div>

        <div className="form-row">
          <div className="form-group">
            <label htmlFor="source-language">Source Language</label>
            <select
              id="source-language"
              className="form-control"
              value={sourceLanguage}
              onChange={(e) => setSourceLanguage(e.target.value)}
              disabled={isSubmitting}
              required
            >
              {languages.map((lang) => (
                <option key={lang.code} value={lang.code}>
                  {lang.name}
                </option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="target-language">Target Language</label>
            <select
              id="target-language"
              className="form-control"
              value={targetLanguage}
              onChange={(e) => setTargetLanguage(e.target.value)}
              disabled={isSubmitting}
              required
            >
              {languages.map((lang) => (
                <option key={lang.code} value={lang.code}>
                  {lang.name}
                </option>
              ))}
            </select>
          </div>
        </div>

        <button
          type="submit"
          className="btn-primary"
          disabled={isSubmitting}
        >
          {isSubmitting ? 'Submitting...' : 'Translate Video'}
        </button>
      </form>

      <div className="info-box">
        <h3>ℹ️ How it works</h3>
        <ol>
          <li>Paste a YouTube video URL</li>
          <li>Select the source language (language of the video)</li>
          <li>Select the target language (language you want to translate to)</li>
          <li>Click "Translate Video" and wait for the magic to happen!</li>
        </ol>
        <p className="note">
          The process includes: downloading video, transcribing audio, translating text,
          generating voice with AI, creating captions, and generating thumbnails.
        </p>
      </div>
    </div>
  );
}

export default VideoForm;
