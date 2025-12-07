import time
import logging
import random
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from src.config import Config

# Configure logging
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AternosBooster:
    def __init__(self):
        self.driver = None
        self.session_start = datetime.now()
        self.total_boosts = 0
        self.session_boosts = 0
        self.consecutive_fails = 0
        self.is_online = False
        
    def setup_driver(self):
        """Setup Chrome driver with optimal settings"""
        options = ChromeOptions()
        
        if Config.HEADLESS:
            options.add_argument('--headless=new')
        
        # Essential arguments
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        
        # Anti-bot detection
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # User agent
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        ]
        options.add_argument(f'--user-agent={random.choice(user_agents)}')
        
        try:
            if Config.IS_RENDER:
                # Render-specific setup
                options.binary_location = '/usr/bin/google-chrome'
                options.add_argument('--disable-setuid-sandbox')
                service = Service(executable_path='/usr/bin/chromedriver')
            else:
                # Local setup
                service = Service(ChromeDriverManager().install())
            
            self.driver = webdriver.Chrome(service=service, options=options)
            
            # Execute CDP commands to prevent detection
            self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {
                "userAgent": options.arguments[-1].split('=')[1]
            })
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            logger.info("✅ Chrome driver initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to setup driver: {e}")
            return False
    
    def login(self):
        """Login to Aternos"""
        try:
            logger.info("🔐 Attempting login...")
            self.driver.get("https://aternos.org/")
            time.sleep(2)
            
            # Click login button
            try:
                login_btn = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Log in')]"))
                )
                login_btn.click()
                time.sleep(1)
            except:
                # Try direct login page
                self.driver.get("https://aternos.org/account/")
                time.sleep(2)
            
            # Enter credentials
            user_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "user"))
            )
            user_field.clear()
            user_field.send_keys(Config.ATERNOS_USERNAME)
            
            pass_field = self.driver.find_element(By.ID, "password")
            pass_field.clear()
            pass_field.send_keys(Config.ATERNOS_PASSWORD)
            
            # Submit
            submit_btn = self.driver.find_element(By.ID, "login")
            submit_btn.click()
            
            # Wait for login
            time.sleep(3)
            
            # Check login success
            if "account" in self.driver.current_url or "server" in self.driver.current_url:
                logger.info("✅ Login successful!")
                return True
            else:
                # Check for error
                try:
                    error_msg = self.driver.find_element(By.CLASS_NAME, "error").text
                    logger.error(f"❌ Login error: {error_msg}")
                except:
                    logger.error("❌ Login failed - unknown error")
                return False
                
        except Exception as e:
            logger.error(f"❌ Login exception: {e}")
            if Config.SCREENSHOT_ON_ERROR:
                self.take_screenshot("login_error")
            return False
    
    def navigate_to_server(self):
        """Navigate to server control panel"""
        try:
            # Try direct server URL
            server_url = f"https://aternos.org/server/"
            self.driver.get(server_url)
            time.sleep(3)
            
            # Look for server panel
            selectors = [
                "//div[contains(@class, 'server')]",
                "//div[contains(text(), 'gameplannet')]",
                "//div[contains(@id, 'server')]"
            ]
            
            for selector in selectors:
                try:
                    if self.driver.find_elements(By.XPATH, selector):
                        logger.info("✅ Found server control panel")
                        return True
                except:
                    continue
            
            # Try servers list
            self.driver.get("https://aternos.org/servers/")
            time.sleep(2)
            
            # Click on server if found
            try:
                server_link = self.driver.find_element(
                    By.XPATH, f"//*[contains(text(), '{Config.ATERNOS_SERVER}')]"
                )
                server_link.click()
                time.sleep(3)
                return True
            except:
                pass
            
            logger.warning("⚠️ Could not find server control panel")
            return False
            
        except Exception as e:
            logger.error(f"❌ Navigation error: {e}")
            return False
    
    def check_server_status(self):
        """Check if server is online"""
        try:
            status_selectors = [
                "//div[contains(text(), 'Online')]",
                "//div[contains(text(), 'OFFLINE') or contains(text(), 'Offline')]",
                "//div[contains(@class, 'status-online')]",
                "//div[contains(@class, 'status-offline')]"
            ]
            
            for selector in status_selectors:
                try:
                    status_elem = self.driver.find_element(By.XPATH, selector)
                    status_text = status_elem.text.lower()
                    
                    if 'online' in status_text:
                        logger.info("✅ Server is ONLINE")
                        self.is_online = True
                        return 'online'
                    elif 'offline' in status_text:
                        logger.info("⚠️ Server is OFFLINE")
                        self.is_online = False
                        return 'offline'
                except:
                    continue
            
            # Check for start button (indicates offline)
            try:
                start_btn = self.driver.find_element(
                    By.XPATH, "//button[contains(text(), 'Start') and not(contains(text(), 'Restart'))]"
                )
                if start_btn:
                    logger.info("⚠️ Server is OFFLINE (Start button found)")
                    self.is_online = False
                    return 'offline'
            except:
                pass
            
            logger.info("ℹ️ Could not determine server status")
            return 'unknown'
            
        except Exception as e:
            logger.error(f"❌ Status check error: {e}")
            return 'error'
    
    def start_server(self):
        """Start the server if offline"""
        try:
            logger.info("🚀 Attempting to start server...")
            
            start_selectors = [
                "//button[contains(text(), 'Start') and not(contains(text(), 'Restart'))]",
                "//button[@id='start']",
                "//button[contains(@class, 'btn-start')]"
            ]
            
            for selector in start_selectors:
                try:
                    start_btn = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    if start_btn and start_btn.is_displayed():
                        logger.info("✅ Found start button, clicking...")
                        start_btn.click()
                        
                        # Wait for server to start
                        logger.info("⏳ Waiting for server to start (60 seconds)...")
                        time.sleep(60)
                        
                        # Check if starting/online
                        for i in range(10):
                            status = self.check_server_status()
                            if status == 'online':
                                logger.info("🎉 Server started successfully!")
                                self.is_online = True
                                return True
                            time.sleep(10)
                        
                        logger.warning("⚠️ Server may still be starting...")
                        return False
                except:
                    continue
            
            logger.info("ℹ️ No start button found (server may already be online)")
            return False
            
        except Exception as e:
            logger.error(f"❌ Start server error: {e}")
            return False
    
    def find_boost_button(self):
        """Find the +1 RAM boost button"""
        try:
            # Refresh page to check for new boost
            self.driver.refresh()
            time.sleep(2)
            
            # Look for boost button
            boost_selectors = [
                "//button[text()='+1']",
                "//button[contains(text(), '+1')]",
                "//button[contains(text(), 'Get your free RAM boost')]",
                "//a[contains(text(), 'Get your free RAM boost')]",
                "//button[.//*[text()='+1']]",
                "//div[contains(text(), 'Boost your Aternos server')]/following::button[1]"
            ]
            
            for selector in boost_selectors:
                try:
                    boost_btn = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    if boost_btn and boost_btn.is_displayed():
                        logger.info(f"✅ Found boost button: {selector}")
                        return boost_btn
                except:
                    continue
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Boost button search error: {e}")
            return None
    
    def click_boost(self, boost_button):
        """Click the boost button"""
        try:
            logger.info("⚡ Clicking boost button...")
            
            # Scroll to button
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", boost_button)
            time.sleep(0.5)
            
            # Try JavaScript click first
            self.driver.execute_script("arguments[0].click();", boost_button)
            time.sleep(2)
            
            # Check for success
            success_indicators = [
                "//*[contains(text(), 'boosted')]",
                "//*[contains(text(), 'success')]",
                "//*[contains(text(), 'activated')]",
                "//*[contains(text(), '+1') and contains(@class, 'active')]"
            ]
            
            for indicator in success_indicators:
                try:
                    if self.driver.find_elements(By.XPATH, indicator):
                        logger.info("🎉 Boost activated successfully!")
                        self.total_boosts += 1
                        self.session_boosts += 1
                        self.consecutive_fails = 0
                        
                        # Send notification
                        self.send_notification(f"Boost #{self.total_boosts} activated!")
                        return True
                except:
                    continue
            
            # Even if no success message, assume it worked
            logger.info("✅ Boost button clicked (assuming success)")
            self.total_boosts += 1
            self.session_boosts += 1
            self.consecutive_fails = 0
            return True
            
        except Exception as e:
            logger.error(f"❌ Boost click error: {e}")
            self.consecutive_fails += 1
            if Config.SCREENSHOT_ON_ERROR:
                self.take_screenshot("boost_error")
            return False
    
    def boost_cycle(self):
        """Single boost attempt cycle"""
        try:
            # Check boost button
            boost_button = self.find_boost_button()
            
            if boost_button:
                # Click boost
                if self.click_boost(boost_button):
                    return True
                else:
                    logger.warning("⚠️ Failed to click boost button")
                    return False
            else:
                # Check if server is online
                status = self.check_server_status()
                
                if status == 'offline' and Config.AUTO_START_SERVER:
                    logger.info("🔄 Server offline, attempting to start...")
                    if self.start_server():
                        # Wait and retry boost
                        time.sleep(30)
                        boost_button = self.find_boost_button()
                        if boost_button:
                            return self.click_boost(boost_button)
                
                logger.info("⏸️ No boost available at this time")
                return False
                
        except Exception as e:
            logger.error(f"❌ Boost cycle error: {e}")
            return False
    
    def continuous_boosting(self):
        """Continuous boosting every 1 minute"""
        logger.info("🚀 Starting CONTINUOUS BOOSTING mode")
        logger.info(f"⏰ Interval: {Config.BOOST_INTERVAL} seconds")
        logger.info(f"⏳ Duration: {Config.MAX_ATTEMPTS_PER_SESSION} minutes")
        
        cycle_count = 0
        start_time = time.time()
        
        while cycle_count < Config.MAX_ATTEMPTS_PER_SESSION:
            cycle_count += 1
            elapsed_minutes = (time.time() - start_time) / 60
            
            logger.info(f"\n{'='*50}")
            logger.info(f"🔄 Cycle #{cycle_count}")
            logger.info(f"⏰ Elapsed: {elapsed_minutes:.1f} minutes")
            logger.info(f"🎯 Session boosts: {self.session_boosts}")
            logger.info(f"🏆 Total boosts: {self.total_boosts}")
            logger.info(f"{'='*50}")
            
            # Run boost cycle
            success = self.boost_cycle()
            
            if success:
                logger.info(f"✅ Boost successful! Total: {self.total_boosts}")
            else:
                logger.info(f"⚠️ No boost available or failed")
            
            # Check if we should restart (Render memory management)
            if Config.IS_RENDER and elapsed_minutes > (Config.RESTART_AFTER_HOURS * 60):
                logger.info(f"🔄 Restarting after {Config.RESTART_AFTER_HOURS} hours...")
                break
            
            # Wait for next cycle
            logger.info(f"⏳ Next check in {Config.BOOST_INTERVAL} seconds...")
            time.sleep(Config.BOOST_INTERVAL)
        
        logger.info(f"\n{'='*50}")
        logger.info(f"🏁 Session completed!")
        logger.info(f"✅ Total boosts this session: {self.session_boosts}")
        logger.info(f"🏆 All-time boosts: {self.total_boosts}")
        logger.info(f"⏰ Total time: {elapsed_minutes:.1f} minutes")
        logger.info(f"{'='*50}")
    
    def send_notification(self, message):
        """Send Telegram notification (optional)"""
        if Config.TELEGRAM_NOTIFICATIONS and Config.TELEGRAM_BOT_TOKEN:
            try:
                import requests
                url = f"https://api.telegram.org/bot{Config.TELEGRAM_BOT_TOKEN}/sendMessage"
                text = f"🎮 Aternos Booster\n{message}\nServer: {Config.ATERNOS_SERVER}"
                
                requests.post(url, json={
                    "chat_id": Config.TELEGRAM_CHAT_ID,
                    "text": text,
                    "parse_mode": "HTML"
                }, timeout=5)
            except:
                pass
    
    def take_screenshot(self, name):
        """Take screenshot for debugging"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"error_{name}_{timestamp}.png"
            self.driver.save_screenshot(filename)
            logger.info(f"📸 Screenshot saved: {filename}")
        except:
            pass
    
    def run(self):
        """Main run method"""
        try:
            # Setup driver
            if not self.setup_driver():
                return False
            
            # Login
            if not self.login():
                return False
            
            # Navigate to server
            if not self.navigate_to_server():
                return False
            
            # Start continuous boosting
            self.continuous_boosting()
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Fatal error in main run: {e}")
            return False
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Cleanup resources"""
        try:
            if self.driver:
                self.driver.quit()
                logger.info("✅ Browser closed")
        except:
            pass
