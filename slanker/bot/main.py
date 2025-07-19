import asyncio
import os
import logging
from typing import Optional

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
from aiohttp.web_app import Application
from dotenv import load_dotenv
from loguru import logger

from handlers import setup_handlers

# Load environment variables
load_dotenv()

# Configuration
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
WEBHOOK_URL = os.getenv("TELEGRAM_WEBHOOK_URL")
WEBAPP_URL = os.getenv("WEBAPP_URL", "https://your-domain.com/webapp")
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))

if not BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN environment variable is required")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger.add("logs/bot.log", rotation="1 day", level="INFO")

# Initialize bot and dispatcher
bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()

async def on_startup(app: Application) -> None:
    """Called on application startup"""
    logger.info("Bot is starting up...")
    
    if WEBHOOK_URL:
        logger.info(f"Setting webhook URL: {WEBHOOK_URL}")
        await bot.set_webhook(
            url=f"{WEBHOOK_URL}/webhook",
            drop_pending_updates=True
        )
    else:
        logger.info("No webhook URL provided, running in polling mode")

async def on_shutdown(app: Application) -> None:
    """Called on application shutdown"""
    logger.info("Bot is shutting down...")
    await bot.delete_webhook()
    await bot.session.close()

def create_app() -> Application:
    """Create and configure the web application"""
    app = web.Application()
    
    # Setup startup and shutdown handlers
    app.on_startup.append(on_startup)
    app.on_cleanup.append(on_shutdown)
    
    # Setup bot handlers
    setup_handlers(dp, WEBAPP_URL)
    
    # Setup webhook handler
    webhook_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot
    )
    webhook_handler.register(app, path="/webhook")
    
    # Health check endpoint
    async def health_check(request):
        return web.json_response({"status": "healthy", "service": "slanker-bot"})
    
    app.router.add_get("/health", health_check)
    
    return app

async def main():
    """Main function to run the bot"""
    try:
        if WEBHOOK_URL:
            # Run with webhook (production)
            app = create_app()
            setup_application(app, dp, bot=bot)
            
            logger.info(f"Starting webhook server on {API_HOST}:{API_PORT}")
            web.run_app(app, host=API_HOST, port=API_PORT)
        else:
            # Run with polling (development)
            logger.info("Starting bot in polling mode...")
            setup_handlers(dp, WEBAPP_URL)
            
            await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Error starting bot: {e}")
        raise
    finally:
        await bot.session.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot crashed: {e}")
        raise