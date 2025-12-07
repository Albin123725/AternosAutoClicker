#!/usr/bin/env python3
"""
Aternos 24/7 Server Keeper - Main Entry Point
Deploy this on Render to keep your Aternos server running 24/7!
"""

import os
import sys
import time
from datetime import datetime

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def main():
    print("=" * 60)
    print("🎮 ATORNOS 24/7 SERVER KEEPER")
    print("=" * 60)
    print("🔥 Keeps your Aternos server running 24/7")
    print("🎯 Strategy: Clicks +1 button at 0:59 to reset shutdown timer")
    print("🛡️ Features: Stealth mode to avoid bot detection")
    print("=" * 60)
    
    from src.aternos_keeper import Aternos24_7Keeper
    
    # Create keeper instance
    keeper = Aternos24_7Keeper()
    
    # Run forever (with restart on failure)
    restart_count = 0
    max_restarts = 10
    
    while restart_count < max_restarts:
        restart_count += 1
        
        print(f"\n🔄 Attempt #{restart_count}")
        print(f"⏰ Starting at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Run the keeper
        success = keeper.run()
        
        if success:
            print(f"✅ Keeper completed successfully")
        else:
            print(f"❌ Keeper failed, will restart in 30 seconds...")
            time.sleep(30)
    
    print(f"\n❌ Maximum restarts reached ({max_restarts}), stopping...")
    print("=" * 60)

if __name__ == "__main__":
    main()
