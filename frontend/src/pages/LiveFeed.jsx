/**
 * LiveFeed Page — Video upload and webcam processing interface.
 */
import { useState, useEffect, useRef } from 'react';
import { uploadVideo, startWebcam, stopWebcam, getCVStatus } from '../services/api';
import { Upload, Camera, CameraOff, Activity, Loader2, AlertCircle } from 'lucide-react';

export default function LiveFeed() {
  const [status, setStatus] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [message, setMessage] = useState('');
  const fileRef = useRef(null);
  const pollRef = useRef(null);

  useEffect(() => {
    fetchStatus();
    return () => { if (pollRef.current) clearInterval(pollRef.current); };
  }, []);

  const fetchStatus = async () => {
    try {
      const res = await getCVStatus();
      setStatus(res.data);
      if (res.data.is_processing && !pollRef.current) {
        pollRef.current = setInterval(async () => {
          const r = await getCVStatus();
          setStatus(r.data);
          if (!r.data.is_processing) {
            clearInterval(pollRef.current);
            pollRef.current = null;
          }
        }, 2000);
      }
    } catch (err) {
      console.error('Status fetch failed:', err);
    }
  };

  const handleUpload = async () => {
    const file = fileRef.current?.files?.[0];
    if (!file) { setMessage('Please select a video file'); return; }
    setUploading(true);
    setMessage('');
    try {
      const fd = new FormData();
      fd.append('video', file);
      const res = await uploadVideo(fd);
      setMessage(res.data.message || 'Processing started');
      fetchStatus();
    } catch (err) {
      setMessage(err.response?.data?.error || 'Upload failed');
    } finally {
      setUploading(false);
    }
  };

  const handleStartCam = async () => {
    try {
      const res = await startWebcam();
      setMessage(res.data.message);
      fetchStatus();
    } catch (err) {
      setMessage(err.response?.data?.error || 'Failed to start webcam');
    }
  };

  const handleStopCam = async () => {
    try {
      const res = await stopWebcam();
      setMessage(res.data.message);
      if (pollRef.current) { clearInterval(pollRef.current); pollRef.current = null; }
      fetchStatus();
    } catch (err) {
      setMessage('Failed to stop');
    }
  };

  const isProcessing = status?.is_processing;

  return (
    <div className="animate-fade-in">
      <div className="page-header">
        <h1>Live Feed</h1>
        <p>Process video files or live webcam feed for violation detection</p>
      </div>

      {/* Status Card */}
      <div className="glass-card" style={{ marginBottom: 24 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 16 }}>
          <Activity size={20} style={{ color: isProcessing ? 'var(--accent-emerald)' : 'var(--text-muted)' }} />
          <h3>Processing Status</h3>
          <span className={`badge ${isProcessing ? 'paid' : 'pending'}`}>
            {isProcessing ? 'Active' : 'Idle'}
          </span>
        </div>
        {isProcessing && status && (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 16 }}>
            <div style={{ padding: 16, background: 'var(--bg-glass)', borderRadius: 'var(--radius-sm)', textAlign: 'center' }}>
              <div style={{ fontSize: '1.3rem', fontWeight: 700, color: 'var(--accent-indigo)' }}>{status.processed_frames}</div>
              <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Frames Processed</div>
            </div>
            <div style={{ padding: 16, background: 'var(--bg-glass)', borderRadius: 'var(--radius-sm)', textAlign: 'center' }}>
              <div style={{ fontSize: '1.3rem', fontWeight: 700, color: 'var(--accent-rose)' }}>{status.violations_found}</div>
              <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Violations Found</div>
            </div>
            <div style={{ padding: 16, background: 'var(--bg-glass)', borderRadius: 'var(--radius-sm)', textAlign: 'center' }}>
              <div style={{ fontSize: '1.3rem', fontWeight: 700, color: 'var(--accent-cyan)' }}>
                {status.total_frames > 0 ? `${Math.round(status.processed_frames / status.total_frames * 100)}%` : 'Live'}
              </div>
              <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Progress</div>
            </div>
          </div>
        )}
      </div>

      <div className="charts-grid">
        {/* Video Upload */}
        <div className="glass-card">
          <h3 style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 20 }}>
            <Upload size={20} style={{ color: 'var(--accent-indigo)' }} /> Upload Video
          </h3>
          <div style={{
            border: '2px dashed var(--border-color)', borderRadius: 'var(--radius-md)',
            padding: 40, textAlign: 'center', marginBottom: 16,
            transition: 'all var(--transition-normal)',
          }}>
            <Upload size={40} style={{ color: 'var(--text-muted)', marginBottom: 12 }} />
            <p style={{ color: 'var(--text-secondary)', marginBottom: 12 }}>
              Drag & drop a video file or click to browse
            </p>
            <input ref={fileRef} type="file" accept="video/*" style={{ display: 'none' }} id="videoUpload" />
            <label htmlFor="videoUpload" className="btn btn-secondary" style={{ cursor: 'pointer' }}>
              Choose File
            </label>
          </div>
          <button
            className="btn btn-primary"
            onClick={handleUpload}
            disabled={uploading || isProcessing}
            style={{ width: '100%' }}
          >
            {uploading ? <><Loader2 size={16} style={{ animation: 'spin 1s linear infinite' }} /> Uploading...</> : 'Process Video'}
          </button>
        </div>

        {/* Webcam */}
        <div className="glass-card">
          <h3 style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 20 }}>
            <Camera size={20} style={{ color: 'var(--accent-cyan)' }} /> Webcam Feed
          </h3>
          <div style={{
            background: 'var(--bg-glass)', borderRadius: 'var(--radius-md)',
            padding: 40, textAlign: 'center', marginBottom: 16,
            minHeight: 200, display: 'flex', alignItems: 'center', justifyContent: 'center',
          }}>
            {isProcessing && status?.source === 'webcam' ? (
              <div>
                <div style={{
                  width: 80, height: 80, borderRadius: '50%',
                  background: 'rgba(16, 185, 129, 0.1)', border: '2px solid var(--accent-emerald)',
                  display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 16px',
                  animation: 'pulse 2s infinite',
                }}>
                  <Camera size={32} style={{ color: 'var(--accent-emerald)' }} />
                </div>
                <p style={{ color: 'var(--accent-emerald)', fontWeight: 600 }}>Webcam Active</p>
                <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>Processing live feed...</p>
              </div>
            ) : (
              <div>
                <CameraOff size={40} style={{ color: 'var(--text-muted)', marginBottom: 12 }} />
                <p style={{ color: 'var(--text-muted)' }}>Webcam not active</p>
              </div>
            )}
          </div>
          <div style={{ display: 'flex', gap: 12 }}>
            <button
              className="btn btn-primary"
              onClick={handleStartCam}
              disabled={isProcessing}
              style={{ flex: 1 }}
            >
              <Camera size={16} /> Start Webcam
            </button>
            <button
              className="btn btn-secondary"
              onClick={handleStopCam}
              disabled={!isProcessing}
              style={{ flex: 1 }}
            >
              <CameraOff size={16} /> Stop
            </button>
          </div>
        </div>
      </div>

      {/* Message */}
      {message && (
        <div className="glass-card" style={{ marginTop: 20, display: 'flex', alignItems: 'center', gap: 10 }}>
          <AlertCircle size={18} style={{ color: 'var(--accent-amber)' }} />
          <span style={{ fontSize: '0.9rem' }}>{message}</span>
        </div>
      )}

      {/* Info */}
      <div className="glass-card" style={{ marginTop: 20, opacity: 0.7 }}>
        <h3 style={{ fontSize: '0.9rem', marginBottom: 8 }}>How It Works</h3>
        <ol style={{ paddingLeft: 20, fontSize: '0.85rem', color: 'var(--text-secondary)', lineHeight: 2 }}>
          <li>Upload a traffic video or start webcam capture</li>
          <li>YOLOv8 detects vehicles, persons, and traffic lights</li>
          <li>Violation logic checks for helmet and red-light infractions</li>
          <li>OCR extracts vehicle number plates from detected violations</li>
          <li>Violations are automatically stored and appear in the dashboard</li>
        </ol>
      </div>
    </div>
  );
}
