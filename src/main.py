import time
import logging
import sys
from colorama import init, Fore, Style
from src.aternos_client import AternosBooster
from src.config import Config

# Initialize colorama
init(autoreset=True)

# Configure logging
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format=f'{Fore.CYAN}%(asctime)s{Style.RESET_ALL} - {Fore.GREEN}%(name)s{Style.RESET_ALL} - {Fore.YELLOW}%(levelname)s{Style.RESET_ALL} - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('aternos_booster.log')
    ]
)

logger = logging.getLogger(__name__)

def print_banner():
    """Print awesome banner"""
    banner = f"""
{Fore.MAGENTA}{'='*60}{Style.RESET_ALL}
{Fore.CYAN}╔══════════════════════════════════════════════════════╗{Style.RESET_ALL}
{Fore.CYAN}║                                                      ║{Style.RESET_ALL}
{Fore.CYAN}║  {Fore.YELLOW}🎮  ATORNOS AUTO-BOOSTER v2.0  🚀           {Fore.CYAN}║{Style.RESET_ALL}
{Fore.CYAN}║                                                      ║{Style.RESET_ALL}
{Fore.CYAN}║  {Fore.GREEN}Continuous +1 RAM Boosting Every Minute!     {Fore.CYAN}║{Style.RESET_ALL}
{Fore.CYAN}║                                                      ║{Style.RESET_ALL}
{Fore.CYAN}╚══════════════════════════════════════════════════════╝{Style.RESET_ALL}
{Fore.MAGENTA}{'='*60}{Style.RESET_ALL}
"""
    print(banner)

def main():
    """Main function"""
    print_banner()
    
    # Display configuration
    Config.display()
    
    # Validate config
    if not Config.validate():
        logger.warning("⚠️ Using default/test credentials")
    
    # Ask for confirmation (if not on Render)
    if not Config.IS_RENDER:
        response = input(f"\n{Fore.YELLOW}🚀 Start continuous boosting? (y/n): {Style.RESET_ALL}")
        if response.lower() != 'y':
            print(f"{Fore.RED}❌ Cancelled{Style.RESET_ALL}")
            return
    
    print(f"\n{Fore.GREEN}✅ Starting booster...{Style.RESET_ALL}")
    
    # Run booster
    booster = AternosBooster()
    
    try:
        success = booster.run()
        
        if success:
            print(f"\n{Fore.GREEN}{'='*60}{Style.RESET_ALL}")
            print(f"{Fore.GREEN}✅ Booster completed successfully!{Style.RESET_ALL}")
            print(f"{Fore.GREEN}🎯 Total boosts: {booster.total_boosts}{Style.RESET_ALL}")
            print(f"{Fore.GREEN}{'='*60}{Style.RESET_ALL}")
        else:
            print(f"\n{Fore.RED}{'='*60}{Style.RESET_ALL}")
            print(f"{Fore.RED}❌ Booster encountered errors{Style.RESET_ALL}")
            print(f"{Fore.RED}{'='*60}{Style.RESET_ALL}")
            
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}⚠️ Stopped by user{Style.RESET_ALL}")
    except Exception as e:
        print(f"\n{Fore.RED}❌ Fatal error: {e}{Style.RESET_ALL}")
        sys.exit(1)

if __name__ == "__main__":
    main()
