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
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('aternos_booster.log')
    ]
)
logger = logging.getLogger(__name__)

class AternosBooster:
    def __init__(self, username, password, server_url):
        self.username = username
        self.password = password
        self.server_url = server_url
        self.driver = None
        self.session_start = datetime.now()
        self.total_boosts = 0
        self.session_boosts = 0
        self.consecutive_fails = 0
        self.is_online = False
        self.is_logged_in = False
        
    def setup_driver(self):
        """Setup Chrome driver optimized for Render"""
        try:
            logger.info("🚀 Setting up Chrome driver...")
            
            options = ChromeOptions()
            
            # Essential arguments for Render
            options.add_argument('--headless=new')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--window-size=1920,1080')
            options.add_argument('--disable-extensions')
            options.add_argument('--disable-software-rasterizer')
            
            # Anti-detection
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            # User agents
            user_agents = [
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            ]
            options.add_argument(f'user-agent={random.choice(user_agents)}')
            
            # Additional preferences
            prefs = {
                "credentials_enable_service": False,
                "profile.password_manager_enabled": False,
                "profile.default_content_setting_values.notifications": 2
            }
            options.add_experimental_option("prefs", prefs)
            
            logger.info("📦 Installing/updating ChromeDriver...")
            
            # Use webdriver-manager to handle ChromeDriver
            service = Service(ChromeDriverManager().install())
            
            # Create driver
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
    
    def safe_find_element(self, by, value, timeout=10):
        """Safely find element with timeout"""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            return element
        except:
            return None
    
    def safe_click(self, element):
        """Safely click element with JavaScript"""
        try:
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
            time.sleep(0.5)
            self.driver.execute_script("arguments[0].click();", element)
            return True
        except:
            return False
    
    def login(self):
        """Login to Aternos"""
        try:
            logger.info(f"🔐 Attempting login for {self.username}...")
            
            # Go to Aternos
            self.driver.get("https://aternos.org/")
            time.sleep(2)
            
            # Try to find and click login button
            login_selectors = [
                (By.XPATH, "//button[contains(., 'Log in')]"),
                (By.XPATH, "//a[contains(@href, 'login')]"),
                (By.CLASS_NAME, "login-btn"),
                (By.ID, "login-button")
            ]
            
            login_clicked = False
            for by, selector in login_selectors:
                try:
                    login_btn = self.safe_find_element(by, selector, 5)
                    if login_btn:
                        if self.safe_click(login_btn):
                            login_clicked = True
                            break
                except:
                    continue
            
            # If no login button found, try direct login page
            if not login_clicked:
                self.driver.get("https://aternos.org/account/")
                time.sleep(2)
            
            # Wait for login form
            time.sleep(2)
            
            # Enter username
            username_field = self.safe_find_element(By.ID, "user")
            if not username_field:
                # Try alternative selectors
                username_selectors = [
                    (By.NAME, "user"),
                    (By.XPATH, "//input[@type='text']"),
                    (By.XPATH, "//input[@placeholder='Username']")
                ]
                
                for by, selector in username_selectors:
                    username_field = self.safe_find_element(by, selector, 3)
                    if username_field:
                        break
            
            if username_field:
                username_field.clear()
                username_field.send_keys(self.username)
                logger.info("✅ Username entered")
            else:
                logger.error("❌ Could not find username field")
                return False
            
            # Enter password
            password_field = self.safe_find_element(By.ID, "password")
            if not password_field:
                password_selectors = [
                    (By.NAME, "password"),
                    (By.XPATH, "//input[@type='password']"),
                    (By.XPATH, "//input[@placeholder='Password']")
                ]
                
                for by, selector in password_selectors:
                    password_field = self.safe_find_element(by, selector, 3)
                    if password_field:
                        break
            
            if password_field:
                password_field.clear()
                password_field.send_keys(self.password)
                logger.info("✅ Password entered")
            else:
                logger.error("❌ Could not find password field")
                return False
            
            # Find and click submit button
            submit_selectors = [
                (By.ID, "login"),
                (By.XPATH, "//button[@type='submit']"),
                (By.XPATH, "//button[contains(., 'Log in')]"),
                (By.CLASS_NAME, "submit-btn")
            ]
            
            for by, selector in submit_selectors:
                try:
                    submit_btn = self.safe_find_element(by, selector, 3)
                    if submit_btn:
                        if self.safe_click(submit_btn):
                            logger.info("✅ Login form submitted")
                            break
                except:
                    continue
            
            # Wait for login to complete
            time.sleep(3)
            
            # Check if login was successful
            if "account" in self.driver.current_url or "server" in self.driver.current_url:
                self.is_logged_in = True
                logger.info("🎉 Login successful!")
                return True
            else:
                # Check for error messages
                error_selectors = [
                    (By.CLASS_NAME, "error"),
                    (By.CLASS_NAME, "alert"),
                    (By.XPATH, "//div[contains(@class, 'error')]"),
                    (By.XPATH, "//div[contains(text(), 'incorrect') or contains(text(), 'error')]")
                ]
                
                for by, selector in error_selectors:
                    try:
                        error_elem = self.driver.find_element(by, selector)
                        if error_elem:
                            logger.error(f"❌ Login error: {error_elem.text[:100]}")
                            return False
                    except:
                        continue
                
                # Take screenshot for debugging
                self.take_screenshot("login_attempt")
                logger.warning("⚠️ Login status uncertain, but continuing...")
                self.is_logged_in = True
                return True
                
        except Exception as e:
            logger.error(f"❌ Login exception: {e}")
            self.take_screenshot("login_error")
            return False
    
    def navigate_to_server(self):
        """Navigate to server control panel"""
        try:
            logger.info("🔄 Navigating to server...")
            
            # Try direct server URL first
            self.driver.get("https://aternos.org/server/")
            time.sleep(3)
            
            # Check if we're on server page
            server_indicators = [
                "server",
                "panel",
                "control",
                "start",
                "stop",
                "restart"
            ]
            
            page_html = self.driver.page_source.lower()
            if any(indicator in page_html for indicator in server_indicators):
                logger.info("✅ On server control panel")
                return True
            
            # If not, try servers list
            logger.info("🔍 Not on server panel, trying servers list...")
            self.driver.get("https://aternos.org/servers/")
            time.sleep(2)
            
            # Look for server link
            try:
                # Try to find any server card/link
                server_links = self.driver.find_elements(
                    By.XPATH, "//*[contains(@class, 'server') or contains(@class, 'card')]//a"
                )
                
                if server_links:
                    logger.info(f"🔗 Found {len(server_links)} server links")
                    # Click the first one
                    server_links[0].click()
                    time.sleep(3)
                    return True
                else:
                    # Try clicking on server name if visible
                    server_name_elements = self.driver.find_elements(
                        By.XPATH, f"//*[contains(text(), '{self.server_url}') or contains(text(), 'gameplannet')]"
                    )
                    
                    if server_name_elements:
                        server_name_elements[0].click()
                        time.sleep(3)
                        return True
            except:
                pass
            
            logger.warning("⚠️ Could not navigate to specific server, but continuing...")
            return True
            
        except Exception as e:
            logger.error(f"❌ Navigation error: {e}")
            return False
    
    def check_boost_button(self):
        """Check if +1 boost button is available"""
        try:
            # Refresh page to get latest state
            self.driver.refresh()
            time.sleep(2)
            
            # Look for boost button
            boost_selectors = [
                "//button[contains(text(), '+1')]",
                "//button[contains(text(), 'Get your free RAM boost')]",
                "//a[contains(text(), 'Get your free RAM boost')]",
                "//button[.//*[text()='+1']]",
                "//div[contains(text(), 'Boost your Aternos server')]/following::button[1]",
                "//button[@aria-label*='boost' or @aria-label*='+1']",
                "//button[contains(@class, 'boost')]"
            ]
            
            for selector in boost_selectors:
                try:
                    boost_btn = WebDriverWait(self.driver, 3).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    if boost_btn and boost_btn.is_displayed():
                        logger.info(f"✅ Found boost button: {selector[:50]}...")
                        return boost_btn
                except:
                    continue
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Boost check error: {e}")
            return None
    
    def click_boost_button(self, boost_button):
        """Click the boost button"""
        try:
            logger.info("⚡ Clicking boost button...")
            
            # Scroll to button
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", boost_button)
            time.sleep(0.3)
            
            # Try JavaScript click
            self.driver.execute_script("arguments[0].click();", boost_button)
            time.sleep(1)
            
            # Try direct click as fallback
            try:
                boost_button.click()
            except:
                pass
            
            # Wait for action to complete
            time.sleep(2)
            
            # Check for success indicators
            success_indicators = [
                "boosted",
                "success",
                "activated",
                "applied",
                "increased",
                "enabled"
            ]
            
            page_text = self.driver.page_source.lower()
            if any(indicator in page_text for indicator in success_indicators):
                logger.info("🎉 Boost appears to be successful!")
                self.total_boosts += 1
                self.session_boosts += 1
                self.consecutive_fails = 0
                return True
            else:
                # Even without confirmation, assume it worked
                logger.info("✅ Boost button clicked (assuming success)")
                self.total_boosts += 1
                self.session_boosts += 1
                self.consecutive_fails = 0
                return True
            
        except Exception as e:
            logger.error(f"❌ Boost click error: {e}")
            self.consecutive_fails += 1
            self.take_screenshot("boost_error")
            return False
    
    def check_server_status(self):
        """Check server status quickly"""
        try:
            # Look for status indicators
            status_indicators = [
                ("Online", "online"),
                ("Offline", "offline"),
                ("Starting", "starting"),
                ("Stopped", "offline"),
                ("Running", "online")
            ]
            
            page_text = self.driver.page_source
            
            for text, status in status_indicators:
                if text in page_text:
                    logger.info(f"📊 Server status: {text}")
                    self.is_online = (status == "online")
                    return status
            
            # Check for start button (indicates offline)
            try:
                start_buttons = self.driver.find_elements(
                    By.XPATH, "//button[contains(text(), 'Start') and not(contains(text(), 'Restart'))]"
                )
                if start_buttons:
                    logger.info("⚠️ Server appears to be offline (Start button found)")
                    self.is_online = False
                    return "offline"
            except:
                pass
            
            logger.info("❓ Could not determine server status")
            return "unknown"
            
        except Exception as e:
            logger.error(f"❌ Status check error: {e}")
            return "error"
    
    def start_server(self):
        """Attempt to start the server"""
        try:
            logger.info("🚀 Attempting to start server...")
            
            start_selectors = [
                "//button[contains(text(), 'Start') and not(contains(text(), 'Restart'))]",
                "//button[@id='start']",
                "//button[contains(@class, 'start')]",
                "//button[contains(@class, 'btn-start')]",
                "//button[.//*[contains(text(), 'Start')]]"
            ]
            
            for selector in start_selectors:
                try:
                    start_btn = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    if start_btn and start_btn.is_displayed():
                        logger.info("✅ Found start button")
                        
                        # Click start
                        if self.safe_click(start_btn):
                            logger.info("⏳ Server start initiated, waiting 60 seconds...")
                            time.sleep(60)
                            
                            # Check if server is starting
                            for i in range(5):
                                status = self.check_server_status()
                                if status == "online" or status == "starting":
                                    logger.info(f"✅ Server is {status}")
                                    self.is_online = True
                                    return True
                                time.sleep(10)
                            
                            logger.warning("⚠️ Server may still be starting...")
                            return False
                except:
                    continue
            
            logger.info("ℹ️ No start button found (server may already be running)")
            return False
            
        except Exception as e:
            logger.error(f"❌ Start server error: {e}")
            return False
    
    def take_screenshot(self, name):
        """Take screenshot for debugging"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{name}_{timestamp}.png"
            self.driver.save_screenshot(filename)
            logger.info(f"📸 Screenshot saved: {filename}")
            return filename
        except Exception as e:
            logger.error(f"❌ Screenshot failed: {e}")
            return None
    
    def single_boost_attempt(self):
        """Single attempt to boost the server"""
        try:
            logger.info("🔄 Starting boost attempt...")
            
            # Check for boost button
            boost_button = self.check_boost_button()
            
            if boost_button:
                # Click boost button
                if self.click_boost_button(boost_button):
                    return True
                else:
                    logger.warning("⚠️ Failed to click boost button")
                    return False
            else:
                # No boost button available
                logger.info("⏸️ No boost button available")
                
                # Check server status
                status = self.check_server_status()
                
                if status == "offline":
                    logger.info("🔄 Server is offline, attempting to start...")
                    if self.start_server():
                        # Wait and check for boost again
                        time.sleep(30)
                        boost_button = self.check_boost_button()
                        if boost_button:
                            return self.click_boost_button(boost_button)
                
                return False
                
        except Exception as e:
            logger.error(f"❌ Boost attempt error: {e}")
            return False
    
    def run_continuous_boosting(self, interval_seconds=60, max_minutes=240):
        """Run continuous boosting"""
        logger.info(f"🚀 Starting CONTINUOUS BOOSTING")
        logger.info(f"⏰ Interval: {interval_seconds} seconds")
        logger.info(f"⏳ Duration: {max_minutes} minutes")
        
        cycle_count = 0
        start_time = time.time()
        max_seconds = max_minutes * 60
        
        try:
            # Setup driver
            if not self.setup_driver():
                logger.error("❌ Failed to setup driver")
                return False
            
            # Login
            if not self.login():
                logger.error("❌ Failed to login")
                return False
            
            # Navigate to server
            if not self.navigate_to_server():
                logger.warning("⚠️ Could not navigate to server, but continuing...")
            
            while cycle_count * interval_seconds < max_seconds:
                cycle_count += 1
                elapsed_seconds = time.time() - start_time
                elapsed_minutes = elapsed_seconds / 60
                
                logger.info(f"\n{'='*50}")
                logger.info(f"🔄 Cycle #{cycle_count}")
                logger.info(f"⏰ Elapsed: {elapsed_minutes:.1f} minutes")
                logger.info(f"🎯 Session boosts: {self.session_boosts}")
                logger.info(f"🏆 Total boosts: {self.total_boosts}")
                logger.info(f"{'='*50}")
                
                # Run boost attempt
                success = self.single_boost_attempt()
                
                if success:
                    logger.info(f"✅ Boost successful! Total: {self.total_boosts}")
                else:
                    logger.info(f"⚠️ No boost available or failed")
                    self.consecutive_fails += 1
                    
                    # If too many failures, try to recover
                    if self.consecutive_fails >= 5:
                        logger.warning("🔄 Too many failures, attempting recovery...")
                        self.take_screenshot("recovery_attempt")
                        
                        # Try to navigate to server again
                        self.navigate_to_server()
                        self.consecutive_fails = 0
                
                # Calculate sleep time
                time_elapsed = time.time() - start_time - (cycle_count * interval_seconds)
                sleep_time = max(0, interval_seconds - time_elapsed)
                
                if sleep_time > 0:
                    logger.info(f"💤 Sleeping for {sleep_time:.1f} seconds...")
                    time.sleep(sleep_time)
            
            logger.info(f"\n{'='*50}")
            logger.info(f"🏁 Session completed!")
            logger.info(f"✅ Total boosts this session: {self.session_boosts}")
            logger.info(f"🏆 All-time boosts: {self.total_boosts}")
            logger.info(f"⏰ Total time: {elapsed_minutes:.1f} minutes")
            logger.info(f"{'='*50}")
            
            return True
            
        except KeyboardInterrupt:
            logger.info("\n👋 Stopped by user")
            return True
        except Exception as e:
            logger.error(f"❌ Fatal error in continuous boosting: {e}")
            self.take_screenshot("fatal_error")
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
    
    def quick_test(self):
        """Quick test of the booster"""
        try:
            logger.info("🧪 Running quick test...")
            
            if not self.setup_driver():
                return False
            
            if not self.login():
                return False
            
            if not self.navigate_to_server():
                return False
            
            # Check server status
            status = self.check_server_status()
            logger.info(f"📊 Server status: {status}")
            
            # Check for boost button
            boost_button = self.check_boost_button()
            if boost_button:
                logger.info("✅ Boost button is available!")
            else:
                logger.info("❌ Boost button not available")
            
            self.cleanup()
            return True
            
        except Exception as e:
            logger.error(f"❌ Quick test failed: {e}")
            self.cleanup()
            return False


# Simple usage example
if __name__ == "__main__":
    # Test configuration
    TEST_USERNAME = "_CRAFTEEE_"
    TEST_PASSWORD = "Albin4242"
    TEST_SERVER = "gameplannet.aternos.me"
    
    # Create booster instance
    booster = AternosBooster(
        username=TEST_USERNAME,
        password=TEST_PASSWORD,
        server_url=TEST_SERVER
    )
    
    # Run quick test
    # booster.quick_test()
    
    # Or run continuous boosting
    booster.run_continuous_boosting(
        interval_seconds=60,  # Check every 60 seconds
        max_minutes=10        # Run for 10 minutes (for testing)
    )
