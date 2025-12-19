import React, { useState, useEffect } from 'react';
import axios from 'axios';
import VideoForm from './components/VideoForm';
import JobStatus from './components/JobStatus';
import ErrorMessage from './components/ErrorMessage';
import './App.css';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8080/api/v1';

function App() {
  const [jobId, setJobId] = useState(null);
  const [jobStatus, setJobStatus] = useState(null);
  const [languages, setLanguages] = useState([]);
  const [error, setError] = useState(null);

  // Fetch supported languages on mount
  useEffect(() => {
    fetchLanguages();
  }, []);

  // Poll job status if we have a jobId
  useEffect(() => {
    if (jobId) {
      const interval = setInterval(() => {
        fetchJobStatus(jobId);
      }, 3000); // Poll every 3 seconds

      return () => clearInterval(interval);
    }
  }, [jobId]);

  const fetchLanguages = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/languages`);
      setLanguages(response.data.languages);
    } catch (err) {
      console.error('Error fetching languages:', err);
      setError('Failed to fetch supported languages');
    }
  };

  const fetchJobStatus = async (id) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/job/${id}`);
      setJobStatus(response.data);

      // Stop polling if job is completed or failed
      if (response.data.status === 'completed' || response.data.status === 'failed') {
        setJobId(null);
      }
    } catch (err) {
      console.error('Error fetching job status:', err);
    }
  };

  const handleSubmit = async (youtubeUrl, sourceLanguage, targetLanguage) => {
    setError(null);
    setJobStatus(null);

    try {
      const response = await axios.post(`${API_BASE_URL}/translate`, {
        youtube_url: youtubeUrl,
        source_language: sourceLanguage,
        target_language: targetLanguage,
      });

      setJobId(response.data.job_id);
      setJobStatus({
        id: response.data.job_id,
        status: response.data.status,
        progress: 0,
      });
    } catch (err) {
      console.error('Error submitting translation job:', err);
      const errorMsg = err.response?.data?.error || 'Failed to submit translation job';
      const details = err.response?.data?.details;
      setError(details ? `${errorMsg}: ${details}` : errorMsg);
    }
  };

  const handleNewTranslation = () => {
    setJobId(null);
    setJobStatus(null);
    setError(null);
  };

  return (
    <div className="App">
      <div className="container">
        <header className="header">
          <h1>🎥 KOL Video Translation</h1>
          <p>Translate YouTube videos with AI-powered voice cloning</p>
        </header>

        <ErrorMessage message={error} onDismiss={() => setError(null)} />

        {!jobStatus ? (
          <VideoForm
            languages={languages}
            onSubmit={handleSubmit}
          />
        ) : (
          <JobStatus
            jobStatus={jobStatus}
            onNewTranslation={handleNewTranslation}
            apiBaseUrl={API_BASE_URL}
          />
        )}

        <footer className="footer">
          <p>Powered by OpenAI Whisper, Coqui TTS, and Google Translate</p>
        </footer>
      </div>
    </div>
  );
}

export default App;
