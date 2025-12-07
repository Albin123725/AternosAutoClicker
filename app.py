#!/usr/bin/env python3
"""
Flask app to bind to port and keep service alive
Render requires a web service to bind to a port
"""

import os
import sys
import threading
import time
from flask import Flask, jsonify

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

app = Flask(__name__)

# Global variables
keeper_thread = None
is_running = False
stats = {
    "status": "stopped",
    "total_clicks": 0,
    "start_time": None,
    "last_error": None
}

@app.route('/')
def home():
    """Home page"""
    return jsonify({
        "service": "Aternos 24/7 Server Keeper",
        "status": stats["status"],
        "total_clicks": stats["total_clicks"],
        "uptime": stats["start_time"],
        "endpoints": {
            "health": "/health",
            "start": "/start",
            "stop": "/stop",
            "status": "/status"
        }
    })

@app.route('/health')
def health():
    """Health check endpoint (required by Render)"""
    return jsonify({
        "status": "healthy",
        "service": "running",
        "timestamp": time.time()
    })

@app.route('/start')
def start_keeper():
    """Start the keeper"""
    global keeper_thread, is_running
    
    if is_running:
        return jsonify({"status": "already_running"})
    
    def run_keeper():
        global stats, is_running
        try:
            from src.aternos_keeper import Aternos24_7Keeper
            keeper = Aternos24_7Keeper()
            is_running = True
            stats["status"] = "running"
            stats["start_time"] = time.strftime("%Y-%m-%d %H:%M:%S")
            keeper.run()
        except Exception as e:
            stats["last_error"] = str(e)
            stats["status"] = "error"
        finally:
            is_running = False
            stats["status"] = "stopped"
    
    keeper_thread = threading.Thread(target=run_keeper, daemon=True)
    keeper_thread.start()
    
    return jsonify({"status": "started", "message": "Keeper started in background"})

@app.route('/stop')
def stop_keeper():
    """Stop the keeper"""
    global is_running
    is_running = False
    return jsonify({"status": "stopping", "message": "Keeper will stop after current cycle"})

@app.route('/status')
def get_status():
    """Get current status"""
    return jsonify(stats)

def run_flask():
    """Run Flask app"""
    port = int(os.environ.get('PORT', 10000))
    print(f"🌐 Flask app starting on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)

if __name__ == "__main__":
    # Auto-start keeper if AUTO_START is true
    if os.environ.get('AUTO_START', 'true').lower() == 'true':
        print("🚀 Auto-starting keeper in background...")
        start_keeper()
    
    # Start Flask app
    run_flask()
