# 🎮 Aternos 24/7 Server Keeper

**Keep your Aternos Minecraft server running 24/7 for FREE!**

Automatically clicks the "+1" button at 0:59 to reset the shutdown timer, creating an infinite loop that keeps your server online forever.

## 🚀 Features

- ✅ **24/7 Server Uptime** - Clicks +1 button at 0:59 to reset shutdown timer
- 🛡️ **Stealth Mode** - Human-like behavior to avoid bot detection
- 🔄 **Auto-Recovery** - Restarts on failure, keeps trying
- 📊 **Detailed Logging** - See exactly what's happening
- ☁️ **Render Ready** - Deploys easily to free cloud hosting

## 🎯 How It Works

1. **Server starts** with 5-minute timer
2. **Timer counts down**: 5:00 → 4:00 → 3:00 → 2:00 → 1:00 → **0:59**
3. **+1 button appears** at 0:59
4. **Script clicks it immediately** 
5. **Timer resets to 1:00**
6. **Repeat forever** → Server runs 24/7!

## 🚀 Quick Deploy

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/YOUR_USERNAME/aternos-24-7-keeper)

### One-Click Setup:
1. **Click "Deploy to Render"** button above
2. **Connect your GitHub** account
3. **Everything auto-configures** with your test account
4. **Click "Create Web Service"**
5. **Done!** Your server will stay online 24/7 🎉

## ⚙️ Configuration

### Environment Variables (Auto-Set):
```env
ATERNOS_USERNAME=_CRAFTEEE_       # Your test account
ATERNOS_PASSWORD=Albin4242        # Test account password
ATERNOS_SERVER=gameplannet.aternos.me:43658  # Your server
STEALTH_MODE=true                 # Avoid bot detection
MAX_FAILURES=20                   # Max fails before restart
