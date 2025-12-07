#!/usr/bin/env python3
"""
Web interface for Render deployment
"""

import os
import sys
import threading
import time
from datetime import datetime
from flask import Flask, jsonify, render_template_string

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

app = Flask(__name__)

# Global state
booster_thread = None
booster_instance = None
is_running = False
stats = {
    "start_time": None,
    "total_boosts": 0,
    "session_boosts": 0,
    "last_boost": None,
    "status": "stopped",
    "next_check": None
}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>🎮 Aternos Auto-Booster</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            margin: 0;
            padding: 20px;
            min-height: 100vh;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        }
        h1 {
            text-align: center;
            margin-bottom: 30px;
            font-size: 2.5em;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
        }
        .status-card {
            background: rgba(255, 255, 255, 0.15);
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 20px;
            transition: transform 0.3s;
        }
        .status-card:hover {
            transform: translateY(-5px);
        }
        .stat-row {
            display: flex;
            justify-content: space-between;
            margin-bottom: 10px;
            padding: 10px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
        }
        .stat-label {
            font-weight: bold;
            color: #ffd700;
        }
        .stat-value {
            font-weight: bold;
        }
        .btn {
            display: inline-block;
            padding: 12px 30px;
            background: linear-gradient(45deg, #ff416c, #ff4b2b);
            color: white;
            text-decoration: none;
            border-radius: 25px;
            font-weight: bold;
            border: none;
            cursor: pointer;
            transition: all 0.3s;
            margin: 10px;
        }
        .btn:hover {
            transform: scale(1.05);
            box-shadow: 0 5px 15px rgba(255, 65, 108, 0.4);
        }
        .btn-start {
            background: linear-gradient(45deg, #00b09b, #96c93d);
        }
        .btn-stop {
            background: linear-gradient(45deg, #ff416c, #ff4b2b);
        }
        .controls {
            text-align: center;
            margin-top: 30px;
        }
        .live-badge {
            display: inline-block;
            padding: 5px 15px;
            background: #ff4757;
            border-radius: 20px;
            font-size: 0.9em;
            animation: pulse 2s infinite;
        }
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }
        .online { color: #00ff00; }
        .offline { color: #ff4757; }
        .warning { color: #ffa502; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎮 Aternos Auto-Booster</h1>
        
        <div class="status-card">
            <h2>📊 Status</h2>
            <div class="stat-row">
                <span class="stat-label">Booster Status:</span>
                <span class="stat-value {% if stats.status == 'running' %}online{% else %}offline{% endif %}">
                    {{ stats.status|upper }}
                    {% if stats.status == 'running' %}<span class="live-badge">LIVE</span>{% endif %}
                </span>
            </div>
            <div class="stat-row">
                <span class="stat-label">Server:</span>
                <span class="stat-value">{{ server_name }}</span>
            </div>
            <div class="stat-row">
                <span class="stat-label">Uptime:</span>
                <span class="stat-value">{{ stats.start_time }}</span>
            </div>
        </div>
        
        <div class="status-card">
            <h2>⚡ Boost Statistics</h2>
            <div class="stat-row">
                <span class="stat-label">Session Boosts:</span>
                <span class="stat-value">{{ stats.session_boosts }}</span>
            </div>
            <div class="stat-row">
                <span class="stat-label">Total Boosts:</span>
                <span class="stat-value">{{ stats.total_boosts }}</span>
            </div>
            <div class="stat-row">
                <span class="stat-label">Last Boost:</span>
                <span class="stat-value">{{ stats.last_boost or 'Never' }}</span>
            </div>
            <div class="stat-row">
                <span class="stat-label">Next Check:</span>
                <span class="stat-value">{{ stats.next_check or 'Not scheduled' }}</span>
            </div>
        </div>
        
        <div class="controls">
            <a href="/start" class="btn btn-start">🚀 START BOOSTING</a>
            <a href="/stop" class="btn btn-stop">⏹️ STOP BOOSTING</a>
            <a href="/boost" class="btn">⚡ MANUAL BOOST</a>
            <a href="/restart" class="btn">🔄 RESTART</a>
        </div>
        
        <div style="text-align: center; margin-top: 30px;">
            <p>Interval: <strong>60 seconds</strong> | Running on: <strong>Render</strong></p>
            <p><a href="/health" style="color: #ffd700;">Health Check</a> | 
               <a href="/logs" style="color: #ffd700;">View Logs</a> | 
               <a href="/config" style="color: #ffd700;">Configuration</a></p>
        </div>
    </div>
    
    <script>
        // Auto-refresh every 30 seconds
        setTimeout(() => {
            window.location.reload();
        }, 30000);
        
        // Update next check time
        function updateNextCheck() {
            const now = new Date();
            const next = new Date(now.getTime() + 60000); // +1 minute
            document.querySelector('.next-check').textContent = 
                next.toLocaleTimeString();
        }
        
        // Initial update
        updateNextCheck();
        setInterval(updateNextCheck, 1000);
    </script>
</body>
</html>
"""

def start_booster():
    """Start the booster in background"""
    global booster_instance, is_running, stats
    
    if is_running:
        return
    
    from src.aternos_client import AternosBooster
    
    is_running = True
    stats["status"] = "running"
    stats["start_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def run():
        try:
            booster = AternosBooster()
            booster.run()
        except Exception as e:
            print(f"Booster error: {e}")
        finally:
            is_running = False
            stats["status"] = "stopped"
    
    # Start in thread
    thread = threading.Thread(target=run, daemon=True)
    thread.start()
    
    return True

@app.route('/')
def home():
    """Main dashboard"""
    from src.config import Config
    
    # Update next check time
    if is_running:
        next_check = datetime.now()
        stats["next_check"] = next_check.strftime("%H:%M:%S")
    
    return render_template_string(HTML_TEMPLATE, 
                                 stats=stats,
                                 server_name=Config.ATERNOS_SERVER,
                                 is_running=is_running)

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "booster": stats["status"],
        "timestamp": datetime.now().isoformat(),
        "boosts": stats["total_boosts"]
    })

@app.route('/start')
def start():
    """Start booster"""
    if start_booster():
        return jsonify({"success": True, "message": "Booster started"})
    return jsonify({"success": False, "message": "Already running"})

@app.route('/stop')
def stop():
    """Stop booster"""
    global is_running
    is_running = False
    return jsonify({"success": True, "message": "Booster stopping"})

@app.route('/boost')
def manual_boost():
    """Manual boost"""
    stats["last_boost"] = datetime.now().strftime("%H:%M:%S")
    stats["total_boosts"] += 1
    stats["session_boosts"] += 1
    return jsonify({
        "success": True,
        "message": "Manual boost recorded",
        "boost_count": stats["total_boosts"]
    })

@app.route('/restart')
def restart():
    """Restart booster"""
    global is_running
    is_running = False
    time.sleep(2)
    start_booster()
    return jsonify({"success": True, "message": "Booster restarted"})

@app.route('/config')
def show_config():
    """Show configuration"""
    from src.config import Config
    
    config_safe = {
        "username": Config.ATERNOS_USERNAME,
        "server": Config.ATERNOS_SERVER,
        "port": Config.ATERNOS_PORT,
        "interval": Config.BOOST_INTERVAL,
        "headless": Config.HEADLESS,
        "on_render": Config.IS_RENDER,
        "max_session": Config.MAX_ATTEMPTS_PER_SESSION
    }
    
    return jsonify(config_safe)

@app.route('/logs')
def show_logs():
    """Show recent logs"""
    try:
        with open('aternos_booster.log', 'r') as f:
            logs = f.read().split('\n')[-50:]  # Last 50 lines
        return jsonify({"logs": logs})
    except:
        return jsonify({"logs": ["No logs available"]})

if __name__ == "__main__":
    # Start booster automatically on Render
    if os.environ.get('RENDER', '').lower() == 'true':
        print("🚀 Starting booster automatically on Render...")
        start_booster()
    
    # Run Flask app
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False)
