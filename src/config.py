import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
env_path = Path('.env')
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
else:
    # Try to load from .env.auto
    auto_env = Path('.env.auto')
    if auto_env.exists():
        load_dotenv(dotenv_path=auto_env)

class Config:
    # Aternos credentials (YOUR TEST ACCOUNT)
    ATERNOS_USERNAME = os.getenv('ATERNOS_USERNAME', '_CRAFTEEE_')
    ATERNOS_PASSWORD = os.getenv('ATERNOS_PASSWORD', 'Albin4242')
    ATERNOS_SERVER = os.getenv('ATERNOS_SERVER', 'gameplannet.aternos.me')
    ATERNOS_PORT = os.getenv('ATERNOS_PORT', '43658')
    
    # Boost settings - 1 MINUTE INTERVALS
    BOOST_INTERVAL = int(os.getenv('BOOST_INTERVAL', '60'))  # 60 seconds = 1 minute
    MAX_ATTEMPTS_PER_SESSION = int(os.getenv('MAX_ATTEMPTS_PER_SESSION', '240'))  # 4 hours
    ENABLE_BOOST = os.getenv('ENABLE_BOOST', 'true').lower() == 'true'
    AUTO_START_SERVER = os.getenv('AUTO_START_SERVER', 'true').lower() == 'true'
    
    # Browser settings
    WEB_DRIVER = os.getenv('WEB_DRIVER', 'chrome').lower()
    HEADLESS = os.getenv('HEADLESS', 'true').lower() == 'true'
    KEEP_BROWSER_OPEN = os.getenv('KEEP_BROWSER_OPEN', 'true').lower() == 'true'
    BROWSER_TIMEOUT = int(os.getenv('BROWSER_TIMEOUT', '30'))
    
    # Render optimization
    IS_RENDER = os.getenv('RENDER', 'false').lower() == 'true'
    RESTART_AFTER_HOURS = int(os.getenv('RESTART_AFTER_HOURS', '4'))
    
    # Debug
    DEBUG = os.getenv('DEBUG', 'false').lower() == 'true'
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    SCREENSHOT_ON_ERROR = os.getenv('SCREENSHOT_ON_ERROR', 'true').lower() == 'true'
    
    # Telegram notifications (optional)
    TELEGRAM_NOTIFICATIONS = os.getenv('TELEGRAM_NOTIFICATIONS', 'false').lower() == 'true'
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
    TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '')
    
    @classmethod
    def validate(cls):
        """Validate configuration"""
        errors = []
        
        if not cls.ATERNOS_USERNAME or cls.ATERNOS_USERNAME == '_CRAFTEEE_':
            errors.append("ATERNOS_USERNAME is not set or using default")
        
        if not cls.ATERNOS_PASSWORD or cls.ATERNOS_PASSWORD == 'Albin4242':
            errors.append("ATERNOS_PASSWORD is not set or using default")
        
        if errors:
            print("⚠️ Configuration warnings:")
            for error in errors:
                print(f"  - {error}")
            print("\nUsing test account credentials...")
        
        return True
    
    @classmethod
    def display(cls):
        """Display current configuration (safe)"""
        print("\n" + "="*60)
        print("🎮 CURRENT CONFIGURATION")
        print("="*60)
        
        config_items = [
            ("Username", cls.ATERNOS_USERNAME),
            ("Password", "***" + cls.ATERNOS_PASSWORD[-3:] if cls.ATERNOS_PASSWORD else "Not set"),
            ("Server", cls.ATERNOS_SERVER),
            ("Port", cls.ATERNOS_PORT),
            ("Boost Interval", f"{cls.BOOST_INTERVAL} seconds"),
            ("Max Session", f"{cls.MAX_ATTEMPTS_PER_SESSION} minutes"),
            ("Headless", cls.HEADLESS),
            ("Auto Start Server", cls.AUTO_START_SERVER),
            ("On Render", cls.IS_RENDER),
        ]
        
        for key, value in config_items:
            print(f"  {key:20} : {value}")
        
        print("="*60 + "\n")
