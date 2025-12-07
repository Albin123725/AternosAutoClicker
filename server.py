#!/usr/bin/env python3
"""
Simple HTTP server for port binding
"""

import os
import sys
import threading
import time
from http.server import HTTPServer, BaseHTTPRequestHandler

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'OK')
        else:
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            html = b"""
            <html>
            <head><title>Aternos 24/7 Keeper</title></head>
            <body>
                <h1>🎮 Aternos 24/7 Server Keeper</h1>
                <p>Service is running in background</p>
                <p>Check logs for details</p>
            </body>
            </html>
            """
            self.wfile.write(html)
    
    def log_message(self, format, *args):
        pass  # Disable logging

def start_keeper():
    """Start the keeper in background"""
    try:
        from src.aternos_bypass import AternosBypassKeeper
        keeper = AternosBypassKeeper()
        keeper.run()
    except Exception as e:
        print(f"Keeper error: {e}")

def main():
    print("=" * 60)
    print("🎮 Aternos 24/7 Bypass Keeper")
    print("=" * 60)
    
    # Start keeper in background thread
    keeper_thread = threading.Thread(target=start_keeper, daemon=True)
    keeper_thread.start()
    
    # Start HTTP server
    port = int(os.environ.get('PORT', 10000))
    server = HTTPServer(('0.0.0.0', port), HealthHandler)
    
    print(f"🌐 HTTP server starting on port {port}")
    print(f"🚀 Keeper started in background")
    print("=" * 60)
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 Shutting down...")
        server.shutdown()

if __name__ == "__main__":
    main()
