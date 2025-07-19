# Slanker 🚀

**Slanker** is a Telegram Mini App that allows users to deploy custom tokens via Clanker SDK with just a few clicks. No CLI, no complex setup - everything happens within Telegram's WebView interface.

## Features

- 🤖 **Telegram Bot Integration**: Simple `/slanker` command to start
- 🌐 **WebApp Interface**: Beautiful, responsive UI with dark/light mode
- 🔒 **Secure**: Private keys stored only in memory, never logged
- ⚡ **Real-time**: Live deployment status with loading spinners
- 📋 **User-friendly**: Copy-to-clipboard functionality, BaseScan links
- 🎯 **Full Automation**: Complete token deployment with one click

## Architecture

```
slanker/
├── bot/                    # Telegram Bot (Python)
│   ├── main.py            # Bot entry point
│   ├── handlers.py        # Command handlers
│   └── requirements.txt   # Python dependencies
├── webapp/                # Mini App Frontend
│   ├── index.html         # Main interface
│   ├── style.css          # Styles (dark/light mode)
│   └── script.js          # Frontend logic
├── api/                   # Backend API (FastAPI)
│   ├── main.py            # API server
│   ├── deploy.py          # Clanker integration
│   └── requirements.txt   # Python dependencies
└── deploy/                # Deployment configs
    ├── render.yaml        # Render deployment
    └── Procfile          # Process file
```

## Quick Start

### 1. Setup Environment

```bash
# Clone and setup
git clone <your-repo>
cd slanker

# Setup environment variables
cp .env.example .env
```

### 2. Configure Environment Variables

```env
# Telegram Bot
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_WEBHOOK_URL=https://your-domain.com/webhook

# Ethereum/Base Network
PRIVATE_KEY=0x...your_private_key_here
RPC_URL=https://mainnet.base.org

# API Configuration
API_SECRET_KEY=your_secret_key_here
CORS_ORIGINS=https://your-domain.com

# Optional: Rate Limiting
RATE_LIMIT_PER_MINUTE=5
```

### 3. Local Development

#### Start the API Server
```bash
cd api
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

#### Start the Bot
```bash
cd bot
pip install -r requirements.txt
python main.py
```

#### Serve WebApp (for testing)
```bash
cd webapp
python -m http.server 8080
```

### 4. Production Deployment

#### Deploy to Render
1. Connect your GitHub repo to Render
2. Create a new Web Service
3. Use the provided `render.yaml` configuration
4. Set environment variables in Render dashboard

#### Setup Telegram Webhook
```bash
curl -X POST "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook" \
     -H "Content-Type: application/json" \
     -d '{"url": "https://your-domain.onrender.com/webhook"}'
```

## Usage

1. **Start the Bot**: Send `/slanker` to your Telegram bot
2. **Open Mini App**: Tap "🚀 Deploy Token" button
3. **Fill Form**: 
   - Token Name
   - Symbol (3-5 characters)
   - Image URI (IPFS link)
   - Initial Market Cap (ETH)
   - Vesting percentage & duration
   - Creator reward percentage
   - Social media URLs
4. **Deploy**: Tap "🎯 Generate & Deploy"
5. **Success**: Get token address, BaseScan link, and copy functionality

## Security Features

- ✅ HTTPS enforcement
- ✅ CORS locked to Telegram WebApp domains
- ✅ Rate limiting (5 deploys per minute per IP)
- ✅ Input validation and sanitization
- ✅ Private keys never stored to disk
- ✅ Memory cleanup after deployment

## API Endpoints

### `POST /deploy`
Deploy a new token via Clanker SDK.

**Request Body:**
```json
{
  "name": "My Token",
  "symbol": "TKN",
  "image": "ipfs://...",
  "initialMarketCap": "10",
  "vestingPercentage": 10,
  "vestingDurationDays": 30,
  "creatorReward": 75,
  "socialMediaUrls": [
    {"platform": "x", "url": "https://twitter.com/mytoken"}
  ]
}
```

**Response:**
```json
{
  "success": true,
  "address": "0x...",
  "basescanUrl": "https://basescan.org/token/0x...",
  "deploymentTime": "2024-01-01T12:00:00Z"
}
```

### `GET /health`
Health check endpoint.

## Environment Setup

### Local Development
1. Install Python 3.9+
2. Install Node.js 18+ (for package management)
3. Setup virtual environment
4. Install dependencies
5. Configure environment variables

### Production Requirements
- Python 3.9+
- HTTPS-enabled domain
- Telegram Bot Token
- Base network RPC access
- Environment variables configured

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

For issues and questions:
- GitHub Issues: [Create an issue](https://github.com/your-repo/slanker/issues)
- Telegram: Contact the bot developer

---

Built with ❤️ using Clanker SDK, Telegram Mini Apps, and FastAPI.