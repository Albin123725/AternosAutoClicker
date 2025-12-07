#!/usr/bin/env python3
"""
Automatic Environment Setup Script
Run this before deployment to auto-configure settings
"""

import os
import sys
import json
from pathlib import Path

def setup_environment():
    """Setup environment variables automatically"""
    print("=" * 60)
    print("🎮 ATORNOS BOOSTER AUTO-SETUP")
    print("=" * 60)
    
    # Default configuration for your test account
    config = {
        "ATERNOS_USERNAME": "_CRAFTEEE_",
        "ATERNOS_PASSWORD": "Albin4242",
        "ATERNOS_SERVER": "gameplannet.aternos.me",
        "ATERNOS_PORT": "43658",
        "BOOST_INTERVAL": "60",
        "MAX_ATTEMPTS_PER_SESSION": "240",
        "WEB_DRIVER": "chrome",
        "HEADLESS": "true",
        "KEEP_BROWSER_OPEN": "true",
        "AUTO_START_SERVER": "true",
        "RENDER": "true"
    }
    
    # Check if running on Render
    if os.environ.get('RENDER', '').lower() == 'true' or 'RENDER' in os.environ:
        print("✅ Detected Render environment")
        config['RENDER'] = 'true'
        config['HEADLESS'] = 'true'
    
    # Create .env file
    env_path = Path('.env')
    with open(env_path, 'w') as f:
        f.write("# Auto-generated environment file\n")
        f.write("# ===============================\n\n")
        for key, value in config.items():
            f.write(f"{key}={value}\n")
    
    print(f"✅ Created {env_path} with {len(config)} variables")
    
    # Also create config.json for backup
    config_path = Path('config.json')
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"✅ Created {config_path} backup")
    
    # Set environment variables
    for key, value in config.items():
        os.environ[key] = value
        print(f"  → {key}: {'*' * len(value) if 'PASSWORD' in key else value}")
    
    print("\n✅ Setup completed successfully!")
    print("🚀 Ready to deploy to Render")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    try:
        setup_environment()
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        sys.exit(1)
