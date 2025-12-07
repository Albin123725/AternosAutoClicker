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
            background: rgba(255, 255, 255
