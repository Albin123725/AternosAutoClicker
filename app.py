#!/usr/bin/env python3
"""
Flask app with fixed port binding
"""

import os
import sys
import threading
import time
from flask import Flask, jsonify, render_template_string

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

app = Flask(__name__)

# Global state
keeper_thread = None
is_running = False
stats = {
    "status": "stopped",
    "clicks": 0,
    "start_time": None,
    "errors": 0
}

@app.route('/')
def home():
    """Home page"""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>🎮 Aternos 24/7 Keeper</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                margin: 0;
                padding: 20px;
                min-height: 100vh;
            }
            .container {
                max-width: 800px;
                margin: 0 auto;
                background: rgba(255,255,255,0.1);
                padding: 30px;
                border-radius: 20px;
                backdrop-filter: blur(10px);
            }
            h1 { text-align: center; }
            .status {
                background: rgba(255,255,255,0.2);
                padding: 20px;
                border-radius: 10px;
                margin: 20px 0;
            }
            .btn {
                display: inline-block;
                padding: 10px 20px;
                background: #4CAF50;
                color: white;
                text-decoration: none;
                border-radius: 5px;
                margin: 5px;
            }
            .btn.stop { background: #f44336; }
            .online { color: #4CAF50; }
            .offline { color: #f44336; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎮 Aternos 24/7 Server Keeper</h1>
            <div class="status">
                <h3>Status: <span class="{{ 'online' if stats.status == 'running' else 'offline' }}">{{ stats.status|upper }}</span></h3>
                <p>Total Clicks: {{ stats.clicks }}</p>
                <p>Start Time: {{ stats.start_time or 'Not started' }}</p>
                <p>Errors: {{ stats.errors }}</p>
            </div>
            <div>
                <a href="/start" class="btn">🚀 START</a>
                <a href="/stop" class="btn stop">⏹️ STOP</a>
                <a href="/health" class="btn">❤️ HEALTH</a>
                <a href="/logs" class="btn">📋 LOGS</a>
            </div>
            <p style="margin-top: 30px; font-size: 0.9em;">
                This service keeps your Aternos server running 24/7 by clicking the +1 button at 0:59.
            </p>
        </div>
    </body>
    </html>
    """
    return render_template_string(html, stats=stats)

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "Aternos 24/7 Keeper",
        "timestamp": time.time(),
        "keeper_running": is_running
    })

@app.route('/start')
def start_keeper():
    """Start the keeper"""
    global keeper_thread, is_running, stats
    
    if is_running:
        return jsonify({"status": "already_running"})
    
    def run_keeper():
        global is_running, stats
        try:
            from src.aternos_keeper import Aternos24_7Keeper
            keeper = Aternos24_7Keeper()
            is_running = True
            stats["status"] = "running"
            stats["start_time"] = time.strftime("%Y-%m-%d %H:%M:%S")
            
            # Run keeper
            success = keeper.run()
            
            if not success:
                stats["errors"] += 1
                logger.error("Keeper failed")
                
        except Exception as e:
            stats["errors"] += 1
            print(f"Keeper error: {e}")
        finally:
            is_running = False
            stats["status"] = "stopped"
    
    # Start in thread
    keeper_thread = threading.Thread(target=run_keeper, daemon=True)
    keeper_thread.start()
    
    return jsonify({"status": "started", "message": "Keeper started in background"})

@app.route('/stop')
def stop_keeper():
    """Stop the keeper"""
    global is_running
    is_running = False
    return jsonify({"status": "stopping"})

@app.route('/logs')
def show_logs():
    """Show recent logs"""
    try:
        with open('aternos_keeper.log', 'r') as f:
            logs = f.read().split('\n')[-50:]
        return jsonify({"logs": logs})
    except:
        return jsonify({"logs": ["No logs available"]})

if __name__ == "__main__":
    # Auto-start if enabled
    if os.environ.get('AUTO_START', 'true').lower() == 'true':
        print("🚀 Auto-starting keeper...")
        threading.Timer(5, start_keeper).start()
    
    # Start Flask
    port = int(os.environ.get('PORT', 10000))
    print(f"🌐 Starting Flask on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
