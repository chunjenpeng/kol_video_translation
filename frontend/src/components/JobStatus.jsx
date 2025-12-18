import React from 'react';
import './JobStatus.css';

function JobStatus({ jobStatus, onNewTranslation, apiBaseUrl }) {
  const getStatusText = (status) => {
    const statusMap = {
      pending: 'Pending',
      downloading: 'Downloading video from YouTube',
      transcribing: 'Transcribing audio',
      translating: 'Translating text',
      generating_voice: 'Generating voice with AI',
      generating_captions: 'Generating captions',
      generating_thumbnail: 'Generating thumbnail',
      completed: 'Completed!',
      failed: 'Failed',
    };
    return statusMap[status] || status;
  };

  const getStatusIcon = (status) => {
    if (status === 'completed') return '✅';
    if (status === 'failed') return '❌';
    return '⏳';
  };

  const handleDownload = () => {
    // Use anchor element with download attribute for secure downloads
    const link = document.createElement('a');
    link.href = `${apiBaseUrl}/download/${jobStatus.id}`;
    link.download = `translated_video_${jobStatus.id}.mp4`;
    link.rel = 'noopener noreferrer';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="job-status">
      <div className="status-header">
        <h2>
          {getStatusIcon(jobStatus.status)} {getStatusText(jobStatus.status)}
        </h2>
        <p className="job-id">Job ID: {jobStatus.id}</p>
      </div>

      {jobStatus.status !== 'failed' && jobStatus.status !== 'completed' && (
        <div className="progress-section">
          <div className="progress-bar">
            <div
              className="progress-fill"
              style={{ width: `${jobStatus.progress}%` }}
            >
              <span className="progress-text">{jobStatus.progress}%</span>
            </div>
          </div>
          <p className="progress-label">Processing your video...</p>
        </div>
      )}

      {jobStatus.status === 'failed' && (
        <div className="error-section">
          <p className="error-text">
            {jobStatus.error_message || 'An error occurred during processing'}
          </p>
        </div>
      )}

      {jobStatus.status === 'completed' && (
        <div className="completed-section">
          <div className="success-message">
            <h3>🎉 Your video is ready!</h3>
            <p>The translation has been completed successfully.</p>
          </div>

          <div className="download-section">
            <button className="btn-download" onClick={handleDownload}>
              ⬇️ Download Translated Video
            </button>

            {jobStatus.captions_path && (
              <div className="additional-files">
                <p>Additional files available:</p>
                <ul>
                  <li>📝 Captions (SRT format)</li>
                  <li>🖼️ Thumbnail</li>
                </ul>
              </div>
            )}
          </div>
        </div>
      )}

      <div className="actions">
        <button className="btn-secondary" onClick={onNewTranslation}>
          Translate Another Video
        </button>
      </div>

      {jobStatus.status !== 'completed' && jobStatus.status !== 'failed' && (
        <div className="info-text">
          <p>⏰ This process may take several minutes depending on video length.</p>
          <p>💡 You can leave this page - your job will continue processing.</p>
        </div>
      )}
    </div>
  );
}

export default JobStatus;
