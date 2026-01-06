"""Flask web application for Mi Scale data extractor."""

import asyncio
import threading
import queue
import json
from datetime import datetime
from typing import Optional, Dict, Any
from flask import Flask, jsonify, request, send_from_directory, Response, stream_with_context
from flask_cors import CORS

from config import (
    SCALE_MAC, AGE, HEIGHT_CM, GENDER,
    STABLE_READINGS_REQUIRED, WEIGHT_TOLERANCE, MIN_STABLE_DURATION_SECONDS
)
from database import init_database, get_all_measurements, get_recent_measurements
from extractor import MiScaleDataExtractor


extractor_thread: Optional[threading.Thread] = None
extractor_instance: Optional[MiScaleDataExtractor] = None
extractor_loop: Optional[asyncio.AbstractEventLoop] = None
status_queue: queue.Queue = queue.Queue(maxsize=100)
current_status: Dict[str, Any] = {
    "is_running": False,
    "last_measurement": None,
    "error": None
}

app = Flask(__name__, static_folder='static')
CORS(app)  


def status_callback(message: str, level: str = "info"):
    """Callback function to add status messages to the queue."""
    try:
        status_queue.put_nowait({
            "message": message,
            "level": level,
            "timestamp": datetime.now().isoformat()
        })
    except queue.Full:
        pass  


def run_extractor_in_thread(address: str, age: int, height_cm: float, gender: str):
    """Run the extractor in a separate thread with its own event loop."""
    global extractor_instance, current_status, extractor_loop
    
    def run_async():
        try:
            current_status["is_running"] = True
            current_status["error"] = None
            
            extractor_instance = MiScaleDataExtractor(
                address=address,
                age=age,
                height_cm=height_cm,
                gender=gender,
                status_callback=status_callback
            )
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            extractor_loop = loop

            loop.run_until_complete(extractor_instance.run_extractor())
            
            measurements = get_recent_measurements(limit=1)
            if measurements:
                current_status["last_measurement"] = measurements[0]
            
            current_status["is_running"] = False
            
        except Exception as e:
            current_status["is_running"] = False
            current_status["error"] = str(e)
            status_callback(f"Error in extractor: {e}", "error")
            print(f"Error in extractor: {e}")
        finally:
            if extractor_loop:
                extractor_loop.close()
    
    thread = threading.Thread(target=run_async, daemon=True)
    thread.start()
    return thread


@app.route('/')
def root():
    """Serve the main web UI."""
    return send_from_directory('static', 'index.html')


@app.route('/static/<path:path>')
def serve_static(path):
    """Serve static files."""
    return send_from_directory('static', path)


@app.route('/api/start', methods=['POST'])
def start_measurement():
    """Start a measurement session."""
    global extractor_thread, current_status, status_queue
    
    try:
        if extractor_thread and not extractor_thread.is_alive():
            current_status["is_running"] = False
            current_status["error"] = None
        
        if current_status.get("is_running", False):
            return jsonify({"error": "Measurement already in progress"}), 400
        
        while not status_queue.empty():
            try:
                status_queue.get_nowait()
            except queue.Empty:
                break
        
        data = request.get_json(silent=True) or {}
        address = data.get('address') or request.args.get('address')
        age = data.get('age') or request.args.get('age', type=int)
        height_cm = data.get('height_cm') or request.args.get('height_cm', type=float)
        gender = data.get('gender') or request.args.get('gender')
        
        scale_address = address or SCALE_MAC
        user_age = age or AGE
        user_height = height_cm or HEIGHT_CM
        user_gender = gender or GENDER
        
        if not scale_address:
            return jsonify({"error": "Scale MAC address is required"}), 400
        if not user_age or user_age <= 0:
            return jsonify({"error": "Valid age is required"}), 400
        if not user_height or user_height <= 0:
            return jsonify({"error": "Valid height is required"}), 400
        if not user_gender or user_gender.lower() not in ['male', 'female']:
            return jsonify({"error": "Valid gender (male/female) is required"}), 400
        
        # Stop any existing thread if it's still running
        if extractor_thread and extractor_thread.is_alive():
            if extractor_instance:
                extractor_instance.is_running = False
            if extractor_loop and not extractor_loop.is_closed():
                try:
                    extractor_loop.call_soon_threadsafe(extractor_loop.stop)
                except Exception:
                    pass
        
        extractor_thread = run_extractor_in_thread(scale_address, user_age, user_height, user_gender)
        
        return jsonify({"message": "Measurement started", "status": "running"})
    except Exception as e:
        print(f"Error in start_measurement: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Failed to start measurement: {str(e)}"}), 500


@app.route('/api/stop', methods=['POST'])
def stop_measurement():
    """Stop the current measurement session."""
    global extractor_instance, extractor_thread, current_status
    
    if not current_status["is_running"]:
        return jsonify({"error": "No measurement in progress"}), 400
    
    if extractor_instance:
        extractor_instance.is_running = False
    
    if extractor_loop and not extractor_loop.is_closed():
        extractor_loop.call_soon_threadsafe(extractor_loop.stop)
    
    current_status["is_running"] = False
    
    return jsonify({"message": "Measurement stopped"})


@app.route('/api/status', methods=['GET'])
def get_status():
    """Get the current status of the extractor."""
    last_measurement = current_status.get("last_measurement")
    
    response = {
        "is_running": current_status["is_running"],
        "last_measurement": last_measurement,
        "error": current_status.get("error")
    }
    
    return jsonify(response)


@app.route('/api/measurements', methods=['GET'])
def get_measurements():
    """Get all measurements or recent measurements."""
    limit = request.args.get('limit', type=int)
    
    if limit:
        measurements = get_recent_measurements(limit=limit)
    else:
        measurements = get_all_measurements()
    
    return jsonify(measurements)


@app.route('/api/config', methods=['GET'])
def get_config():
    """Get current configuration."""
    config = {
        "scale_mac": SCALE_MAC,
        "age": AGE,
        "height_cm": HEIGHT_CM,
        "gender": GENDER,
        "stable_readings_required": STABLE_READINGS_REQUIRED,
        "weight_tolerance": WEIGHT_TOLERANCE,
        "min_stable_duration_seconds": MIN_STABLE_DURATION_SECONDS
    }
    
    return jsonify(config)


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint for Kubernetes."""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    })


@app.route('/api/status/stream')
def stream_status():
    """Server-Sent Events endpoint for real-time status updates."""
    def generate():
        while True:
            try:
                status = status_queue.get(timeout=1.0)
                yield f"data: {json.dumps(status)}\n\n"
            except queue.Empty:
                yield ": keepalive\n\n"
    
    return Response(
        stream_with_context(generate()),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no',
            'Connection': 'keep-alive'
        }
    )


init_database()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=False)
