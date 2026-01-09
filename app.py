"""
Document Summarizer - Flask API
Main application entry point.
"""

import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

from parsers import parse_text, parse_uploaded_file
from summarizers import get_summarizer
from storage import save_summary, get_summary, list_summaries, delete_summary, export_summary

app = Flask(__name__, static_folder='static')
CORS(app)

# Configuration
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH


@app.route('/')
def index():
    """Serve the main web interface."""
    return send_from_directory('static', 'index.html')


@app.route('/api/summarize', methods=['POST'])
def summarize():
    """
    Summarize text or uploaded document.
    
    Accepts:
        - JSON with 'text' field
        - Form data with 'file' upload
    
    Query params:
        - mode: 'local' or 'online'
        - length: 'short', 'medium', or 'long'
        - api_key: API key for online mode
        - save: 'true' to save the summary
    """
    try:
        # Get parameters
        mode = request.args.get('mode', 'local')
        length = request.args.get('length', 'medium')
        api_key = request.args.get('api_key', '')
        should_save = request.args.get('save', 'false').lower() == 'true'
        
        # Get text from request
        text = None
        filename = 'pasted_text'
        file_type = 'text'
        
        if request.is_json:
            data = request.get_json()
            text = data.get('text', '')
            filename = data.get('filename', 'pasted_text')
        elif 'file' in request.files:
            file = request.files['file']
            if file.filename:
                filename = file.filename
                text, file_type = parse_uploaded_file(file, filename)
        elif 'text' in request.form:
            text = request.form.get('text', '')
            filename = request.form.get('filename', 'pasted_text')
        
        if not text or not text.strip():
            return jsonify({'error': 'No text provided'}), 400
        
        # Get summarizer
        summarizer = get_summarizer(mode, api_key if mode == 'online' else None)
        
        # Generate summary and key points
        summary = summarizer.summarize(text, length)
        key_points = summarizer.extract_key_points(text)
        
        result = {
            'summary': summary,
            'key_points': key_points,
            'mode': mode,
            'length': length,
            'filename': filename,
            'file_type': file_type,
            'original_length': len(text),
            'summary_length': len(summary)
        }
        
        # Save if requested
        if should_save:
            summary_id = save_summary(
                filename=filename,
                original_text=text,
                summary=summary,
                key_points=key_points,
                mode=mode,
                length=length,
                file_type=file_type
            )
            result['saved_id'] = summary_id
        
        return jsonify(result)
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Summarization failed: {str(e)}'}), 500


@app.route('/api/summaries', methods=['GET'])
def get_summaries():
    """List all saved summaries."""
    try:
        summaries = list_summaries()
        return jsonify({'summaries': summaries})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/summaries/<int:summary_id>', methods=['GET'])
def get_summary_by_id(summary_id):
    """Get a specific summary by ID."""
    try:
        summary = get_summary(summary_id)
        if summary:
            return jsonify(summary)
        return jsonify({'error': 'Summary not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/summaries/<int:summary_id>', methods=['DELETE'])
def delete_summary_by_id(summary_id):
    """Delete a summary by ID."""
    try:
        if delete_summary(summary_id):
            return jsonify({'success': True})
        return jsonify({'error': 'Summary not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/summaries/<int:summary_id>/export', methods=['GET'])
def export_summary_by_id(summary_id):
    """Export a summary in text or JSON format."""
    try:
        format = request.args.get('format', 'txt')
        content = export_summary(summary_id, format)
        
        if content:
            return content, 200, {'Content-Type': 'text/plain' if format == 'txt' else 'application/json'}
        return jsonify({'error': 'Summary not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({'status': 'ok', 'version': '1.0.0'})


if __name__ == '__main__':
    # Ensure static directory exists
    os.makedirs('static', exist_ok=True)
    
    print("🚀 Document Summarizer starting...")
    print("📄 Open http://localhost:5000 in your browser")
    
    app.run(debug=True, port=5000)
