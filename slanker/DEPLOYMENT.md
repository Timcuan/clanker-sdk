# Slanker Deployment Guide 🚀

This guide covers different deployment options for the Slanker Telegram Mini App.

## Prerequisites

- Python 3.9+
- Node.js 18+
- Telegram Bot Token (from [@BotFather](https://t.me/BotFather))
- Ethereum private key with Base network access
- HTTPS domain (for production)

## Quick Start (Local Development)

1. **Clone and Setup**
   ```bash
   git clone <your-repo-url>
   cd slanker
   cp .env.example .env
   ```

2. **Install Dependencies**
   ```bash
   # Install Node.js dependencies and Clanker SDK
   npm install
   npm run setup
   
   # Install Python dependencies
   npm run install:deps
   ```

3. **Configure Environment**
   Edit `.env` file with your credentials:
   ```env
   TELEGRAM_BOT_TOKEN=your_bot_token_here
   PRIVATE_KEY=0x...your_private_key_here
   API_SECRET_KEY=your_random_secret_key
   ```

4. **Start Services**
   ```bash
   # Terminal 1: API Server
   npm run dev:api
   
   # Terminal 2: Telegram Bot
   npm run dev:bot
   
   # Terminal 3: WebApp
   npm run dev:webapp
   ```

5. **Access**
   - API: http://localhost:8000
   - WebApp: http://localhost:8080
   - Bot: Send `/slanker` to your Telegram bot

## Production Deployment Options

### Option 1: Render (Recommended)

1. **Prepare Repository**
   ```bash
   git add .
   git commit -m "Initial Slanker setup"
   git push origin main
   ```

2. **Deploy to Render**
   - Connect your GitHub repo to Render
   - Use the provided `deploy/render.yaml` configuration
   - Set environment variables in Render dashboard:
     - `TELEGRAM_BOT_TOKEN`
     - `PRIVATE_KEY`
     - `API_SECRET_KEY`
     - `TELEGRAM_WEBHOOK_URL` (will be auto-generated)

3. **Setup Webhook**
   ```bash
   curl -X POST "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook" \
        -H "Content-Type: application/json" \
        -d '{"url": "https://slanker-bot.onrender.com/webhook"}'
   ```

### Option 2: Docker Compose

1. **Build and Run**
   ```bash
   cd deploy
   docker-compose up -d
   ```

2. **Configure Nginx (for WebApp)**
   ```bash
   # Update nginx.conf with your domain
   # Restart containers
   docker-compose restart
   ```

### Option 3: Manual VPS Deployment

1. **Server Setup**
   ```bash
   # Install dependencies
   sudo apt update
   sudo apt install python3.11 python3-pip nodejs npm nginx certbot
   
   # Install PM2 for process management
   npm install -g pm2
   ```

2. **Application Setup**
   ```bash
   # Clone repository
   git clone <your-repo-url> /var/www/slanker
   cd /var/www/slanker
   
   # Install dependencies
   npm install
   npm run setup
   npm run install:deps
   ```

3. **Process Management**
   ```bash
   # Start API with PM2
   pm2 start "uvicorn api.main:app --host 0.0.0.0 --port 8000" --name slanker-api
   
   # Start Bot with PM2
   pm2 start "python bot/main.py" --name slanker-bot
   
   # Save PM2 configuration
   pm2 save
   pm2 startup
   ```

4. **Nginx Configuration**
   ```nginx
   # /etc/nginx/sites-available/slanker
   server {
       listen 80;
       server_name yourdomain.com;
       
       # WebApp
       location / {
           root /var/www/slanker/webapp;
           index index.html;
           try_files $uri $uri/ /index.html;
       }
       
       # API
       location /api/ {
           proxy_pass http://localhost:8000/;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
       
       # Bot Webhook
       location /webhook {
           proxy_pass http://localhost:8001/webhook;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

5. **SSL Certificate**
   ```bash
   sudo certbot --nginx -d yourdomain.com
   ```

## Environment Variables Reference

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `TELEGRAM_BOT_TOKEN` | Bot token from @BotFather | `123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11` |
| `PRIVATE_KEY` | Ethereum private key | `0x1234567890abcdef...` |
| `API_SECRET_KEY` | Random secret for API security | `your-random-secret-key-here` |

### Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `RPC_URL` | Base network RPC endpoint | `https://mainnet.base.org` |
| `CORS_ORIGINS` | Allowed CORS origins | Telegram WebApp domains |
| `RATE_LIMIT_PER_MINUTE` | API rate limit | `5` |
| `LOG_LEVEL` | Logging level | `INFO` |

## Security Checklist

- [ ] ✅ HTTPS enabled for all endpoints
- [ ] ✅ Private keys stored securely (environment variables only)
- [ ] ✅ CORS properly configured
- [ ] ✅ Rate limiting enabled
- [ ] ✅ Input validation implemented
- [ ] ✅ Error handling without sensitive data exposure
- [ ] ✅ Webhook URL uses HTTPS
- [ ] ✅ Bot token never logged or exposed

## Monitoring and Maintenance

### Health Checks

- API: `GET /health`
- Bot: `GET /health`
- WebApp: Check if static files load

### Logs

```bash
# API logs
tail -f logs/api.log

# Bot logs
tail -f logs/bot.log

# PM2 logs (if using PM2)
pm2 logs
```

### Updates

```bash
# Pull latest changes
git pull origin main

# Restart services
pm2 restart all

# Or with Docker
docker-compose restart
```

## Troubleshooting

### Common Issues

1. **Node.js not found**
   ```bash
   # Install Node.js 18+
   curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
   sudo apt-get install -y nodejs
   ```

2. **Clanker SDK import error**
   ```bash
   # Reinstall Clanker SDK
   npm run setup
   ```

3. **Webhook not working**
   ```bash
   # Check webhook status
   curl "https://api.telegram.org/bot<TOKEN>/getWebhookInfo"
   
   # Reset webhook
   curl -X POST "https://api.telegram.org/bot<TOKEN>/deleteWebhook"
   curl -X POST "https://api.telegram.org/bot<TOKEN>/setWebhook" \
        -d "url=https://yourdomain.com/webhook"
   ```

4. **CORS errors**
   - Ensure CORS_ORIGINS includes Telegram WebApp domains
   - Check that API is accessible from WebApp domain

### Support

For issues and questions:
- GitHub Issues: [Create an issue](https://github.com/your-repo/slanker/issues)
- Check logs for detailed error messages
- Verify all environment variables are set correctly

## Performance Tips

1. **Use a CDN** for static WebApp files
2. **Enable gzip compression** in your web server
3. **Monitor resource usage** and scale as needed
4. **Cache static resources** with appropriate headers
5. **Use a load balancer** for high-traffic deployments

---

Built with ❤️ using [Clanker SDK](https://github.com/Timcuan/clanker-sdk)