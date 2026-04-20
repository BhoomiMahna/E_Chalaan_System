"""
CV routes — REST API endpoints for computer vision processing.
Endpoints:
  POST /api/cv/process-video  → Upload and process a video file
  POST /api/cv/start-webcam   → Start webcam processing
  POST /api/cv/stop-webcam    → Stop webcam processing
  GET  /api/cv/status         → Get processing status
  GET  /api/cv/feed           → Server-sent events for real-time detections
"""
import os
import threading
from flask import Blueprint, request, jsonify, Response, current_app
from werkzeug.utils import secure_filename

cv_bp = Blueprint('cv', __name__)

# Global state for video processing
processing_state = {
    'is_processing': False,
    'source': None,
    'total_frames': 0,
    'processed_frames': 0,
    'violations_found': 0,
    'thread': None
}


@cv_bp.route('/api/cv/process-video', methods=['POST'])
def process_video():
    """Upload and process a video file for violations."""
    if processing_state['is_processing']:
        return jsonify({'error': 'Already processing a video'}), 409

    if 'video' not in request.files:
        return jsonify({'error': 'No video file provided'}), 400

    video_file = request.files['video']
    if video_file.filename == '':
        return jsonify({'error': 'Empty filename'}), 400

    # Save uploaded video
    upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
    os.makedirs(upload_folder, exist_ok=True)
    filename = secure_filename(video_file.filename)
    filepath = os.path.join(upload_folder, filename)
    video_file.save(filepath)

    # Start processing in background thread
    from cv_module.video_processor import VideoProcessor
    processor = VideoProcessor(current_app._get_current_object())

    def run_processing():
        processing_state['is_processing'] = True
        processing_state['source'] = filepath
        processing_state['violations_found'] = 0
        try:
            processor.process_video(filepath, processing_state)
        finally:
            processing_state['is_processing'] = False

    thread = threading.Thread(target=run_processing, daemon=True)
    processing_state['thread'] = thread
    thread.start()

    return jsonify({
        'success': True,
        'message': f'Processing started for {filename}',
        'filename': filename
    })


@cv_bp.route('/api/cv/start-webcam', methods=['POST'])
def start_webcam():
    """Start processing from webcam (camera index 0)."""
    if processing_state['is_processing']:
        return jsonify({'error': 'Already processing'}), 409

    from cv_module.video_processor import VideoProcessor
    processor = VideoProcessor(current_app._get_current_object())

    def run_webcam():
        processing_state['is_processing'] = True
        processing_state['source'] = 'webcam'
        processing_state['violations_found'] = 0
        try:
            processor.process_video(0, processing_state)  # 0 = default webcam
        finally:
            processing_state['is_processing'] = False

    thread = threading.Thread(target=run_webcam, daemon=True)
    processing_state['thread'] = thread
    thread.start()

    return jsonify({'success': True, 'message': 'Webcam processing started'})


@cv_bp.route('/api/cv/stop-webcam', methods=['POST'])
def stop_webcam():
    """Stop any active video/webcam processing."""
    processing_state['is_processing'] = False
    return jsonify({'success': True, 'message': 'Processing stopped'})


@cv_bp.route('/api/cv/status', methods=['GET'])
def get_status():
    """Get current processing status."""
    return jsonify({
        'is_processing': processing_state['is_processing'],
        'source': str(processing_state.get('source', '')),
        'total_frames': processing_state.get('total_frames', 0),
        'processed_frames': processing_state.get('processed_frames', 0),
        'violations_found': processing_state.get('violations_found', 0)
    })
