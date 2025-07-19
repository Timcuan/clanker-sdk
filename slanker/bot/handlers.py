from aiogram import Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from loguru import logger

def setup_handlers(dp: Dispatcher, webapp_url: str):
    """Setup all bot handlers"""
    
    @dp.message(Command("start"))
    async def start_command(message: types.Message):
        """Handle /start command"""
        user = message.from_user
        logger.info(f"User {user.id} ({user.username}) started the bot")
        
        welcome_text = (
            "🚀 <b>Welcome to Slanker!</b>\n\n"
            "Deploy custom tokens on Base using Clanker SDK with just a few clicks!\n\n"
            "✨ <b>Features:</b>\n"
            "• Deploy tokens instantly\n"
            "• Configure vesting & rewards\n"
            "• Beautiful dark/light mode UI\n"
            "• Secure - keys never stored\n"
            "• Copy-to-clipboard support\n\n"
            "📱 Use /slanker to start deploying your token!"
        )
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🚀 Deploy Token", web_app=WebAppInfo(url=webapp_url))],
            [InlineKeyboardButton(text="📖 Help", callback_data="help")]
        ])
        
        await message.answer(welcome_text, reply_markup=keyboard)
    
    @dp.message(Command("slanker"))
    async def slanker_command(message: types.Message):
        """Handle /slanker command - main entry point"""
        user = message.from_user
        logger.info(f"User {user.id} ({user.username}) used /slanker command")
        
        text = (
            "🎯 <b>Ready to Deploy Your Token?</b>\n\n"
            "Tap the button below to open the Slanker Mini App and deploy your custom token "
            "on Base using Clanker SDK.\n\n"
            "🔒 <b>Secure & Fast</b> - Everything happens safely in your browser.\n"
            "⚡ <b>One-Click Deploy</b> - No technical knowledge required.\n"
            "📋 <b>Full Control</b> - Configure every aspect of your token.\n\n"
            "<i>Your private keys are handled securely and never stored.</i>"
        )
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🚀 Deploy Token", web_app=WebAppInfo(url=webapp_url))],
            [
                InlineKeyboardButton(text="ℹ️ About", callback_data="about"),
                InlineKeyboardButton(text="🛡️ Security", callback_data="security")
            ]
        ])
        
        await message.answer(text, reply_markup=keyboard)
    
    @dp.message(Command("help"))
    async def help_command(message: types.Message):
        """Handle /help command"""
        help_text = (
            "🆘 <b>Slanker Help</b>\n\n"
            "<b>Commands:</b>\n"
            "/start - Welcome message and quick start\n"
            "/slanker - Open token deployment interface\n"
            "/help - Show this help message\n"
            "/about - About Slanker\n\n"
            "<b>How to Deploy a Token:</b>\n"
            "1. Use /slanker command\n"
            "2. Tap '🚀 Deploy Token' button\n"
            "3. Fill in your token details:\n"
            "   • Token name & symbol\n"
            "   • IPFS image URL\n"
            "   • Market cap & vesting settings\n"
            "   • Creator rewards & social links\n"
            "4. Tap '🎯 Generate & Deploy'\n"
            "5. Wait for deployment confirmation\n"
            "6. Copy token address & view on BaseScan\n\n"
            "<b>Need Support?</b>\n"
            "Contact the development team for assistance."
        )
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🚀 Deploy Now", web_app=WebAppInfo(url=webapp_url))]
        ])
        
        await message.answer(help_text, reply_markup=keyboard)
    
    @dp.message(Command("about"))
    async def about_command(message: types.Message):
        """Handle /about command"""
        about_text = (
            "ℹ️ <b>About Slanker</b>\n\n"
            "Slanker is a Telegram Mini App that simplifies token deployment on Base "
            "using the powerful Clanker SDK.\n\n"
            "<b>🎯 Mission:</b>\n"
            "Make token deployment accessible to everyone, no technical expertise required.\n\n"
            "<b>🔧 Technology:</b>\n"
            "• Clanker SDK for Base deployment\n"
            "• Telegram Mini Apps for seamless UX\n"
            "• FastAPI for secure backend processing\n"
            "• Advanced security & rate limiting\n\n"
            "<b>🌟 Features:</b>\n"
            "• Instant token deployment\n"
            "• Customizable vesting schedules\n"
            "• Creator reward configuration\n"
            "• Social media integration\n"
            "• Dark/Light mode support\n"
            "• Mobile-optimized interface\n\n"
            "<b>🔗 Links:</b>\n"
            "Built with Clanker SDK: https://github.com/Timcuan/clanker-sdk"
        )
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🚀 Try It Now", web_app=WebAppInfo(url=webapp_url))]
        ])
        
        await message.answer(about_text, reply_markup=keyboard)
    
    @dp.callback_query(lambda c: c.data == "help")
    async def help_callback(callback_query: types.CallbackQuery):
        """Handle help button callback"""
        await help_command(callback_query.message)
        await callback_query.answer()
    
    @dp.callback_query(lambda c: c.data == "about")
    async def about_callback(callback_query: types.CallbackQuery):
        """Handle about button callback"""
        await about_command(callback_query.message)
        await callback_query.answer()
    
    @dp.callback_query(lambda c: c.data == "security")
    async def security_callback(callback_query: types.CallbackQuery):
        """Handle security info callback"""
        security_text = (
            "🛡️ <b>Security Features</b>\n\n"
            "<b>🔒 Private Key Protection:</b>\n"
            "• Keys stored only in memory during deployment\n"
            "• Never logged or saved to disk\n"
            "• Automatic memory cleanup after use\n\n"
            "<b>🌐 Network Security:</b>\n"
            "• HTTPS enforcement for all communications\n"
            "• CORS restricted to Telegram domains\n"
            "• Rate limiting to prevent abuse\n\n"
            "<b>🔍 Input Validation:</b>\n"
            "• All inputs sanitized and validated\n"
            "• Protection against injection attacks\n"
            "• Smart contract interaction safety\n\n"
            "<b>📊 Monitoring:</b>\n"
            "• Comprehensive logging (no sensitive data)\n"
            "• Error tracking and monitoring\n"
            "• Regular security audits\n\n"
            "<i>Your security is our top priority!</i>"
        )
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🚀 Deploy Securely", web_app=WebAppInfo(url=webapp_url))]
        ])
        
        await callback_query.message.edit_text(security_text, reply_markup=keyboard)
        await callback_query.answer()
    
    @dp.message()
    async def unknown_message(message: types.Message):
        """Handle unknown messages"""
        text = (
            "🤔 I don't understand that command.\n\n"
            "Use /slanker to deploy tokens or /help for assistance."
        )
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🚀 Deploy Token", web_app=WebAppInfo(url=webapp_url))],
            [InlineKeyboardButton(text="📖 Help", callback_data="help")]
        ])
        
        await message.answer(text, reply_markup=keyboard)