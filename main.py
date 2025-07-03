#!/usr/bin/env python3
"""
Telegram Bot with Auto-Join Feature
Main entry point for the bot application with enhanced error handling
"""

import logging
import os
import sys
import asyncio
from datetime import datetime

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    # Try importing with explicit path
    from telegram import Update
    from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
    from telegram.error import NetworkError, TimedOut
except ImportError as e:
    print(f"Error importing telegram: {e}")
    print("Installing required packages...")
    import subprocess
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "python-telegram-bot==22.2"])
        from telegram import Update
        from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
        from telegram.error import NetworkError, TimedOut
    except Exception as e2:
        print(f"Failed to install or import telegram: {e2}")
        print("Please install manually: pip install python-telegram-bot==22.2")
        sys.exit(1)

from bot_handlers import start, help_command, join_command, broadcast_command, list_command, handle_message
from config import BOT_TOKEN, setup_logging, get_bot_info

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle errors that occur during bot operation
    
    Args:
        update: The update that caused the error
        context: The context object containing the error
    """
    logger = logging.getLogger(__name__)
    
    # Log the error
    logger.error(f"Exception while handling an update: {context.error}")
    
    # Log update details if available
    if update:
        logger.error(f"Update details: {update}")
    
    # Handle specific error types
    if isinstance(context.error, NetworkError):
        logger.error("Network error occurred - checking connection")
    elif isinstance(context.error, TimedOut):
        logger.error("Request timed out - server may be slow")
    
    # Try to send error message to user if possible
    try:
        if update and hasattr(update, 'effective_chat') and update.effective_chat:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="⚠️ Terjadi kesalahan sistem. Silakan coba lagi dalam beberapa menit.",
                parse_mode='Markdown'
            )
    except Exception as e:
        logger.error(f"Could not send error message to user: {e}")

def main():
    """Main function to run the bot with enhanced error handling"""
    # Setup logging first
    setup_logging()
    logger = logging.getLogger(__name__)
    
    # Log startup information
    logger.info("="*60)
    logger.info("STARTING TELEGRAM AUTO-JOIN BOT")
    logger.info(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("="*60)
    
    # Verify bot token
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN not found! Please set BOT_TOKEN environment variable")
        print("❌ Error: BOT_TOKEN not configured!")
        print("Please set BOT_TOKEN environment variable or edit config.py")
        sys.exit(1)
    
    # Log bot configuration
    bot_info = get_bot_info()
    logger.info(f"Bot configuration: {bot_info}")
    
    try:
        # Create the Application
        logger.info("Creating Telegram application...")
        application = Application.builder().token(BOT_TOKEN).build()
        
        # Add error handler
        application.add_error_handler(error_handler)
        
        # Register command handlers
        logger.info("Registering command handlers...")
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("join", join_command))
        application.add_handler(CommandHandler("bc", broadcast_command))
        application.add_handler(CommandHandler("list", list_command))
        
        # Register message handler for authentication codes
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        
        logger.info("✅ Bot handlers registered successfully")
        
        # Log available commands
        logger.info("Available commands:")
        logger.info("  /start - Start the bot")
        logger.info("  /help - Show help message")
        logger.info("  /join [link] - Join group/channel")
        logger.info("  /bc [message] - Broadcast message")
        logger.info("  /list - List joined chats")
        
        # Run the bot
        logger.info("🚀 Starting bot polling...")
        print("🤖 Telegram Auto-Join Bot is starting...")
        print("✅ Bot is ready and waiting for messages...")
        print("📊 Check logs/ directory for detailed logs")
        print("🛑 Press Ctrl+C to stop the bot")
        print("-" * 50)
        
        # Start polling with enhanced error handling
        application.run_polling(
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=True,  # Clear pending updates on start
        )
        
    except KeyboardInterrupt:
        logger.info("🛑 Bot stopped by user (Ctrl+C)")
        print("\n👋 Bot stopped by user")
    except Exception as e:
        logger.error(f"💥 Critical error during bot startup: {e}")
        print(f"❌ Critical error: {e}")
        print("📋 Check logs/error_*.log for details")
        raise
    finally:
        logger.info("="*60)
        logger.info("TELEGRAM AUTO-JOIN BOT SHUTDOWN")
        logger.info(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("="*60)

if __name__ == '__main__':
    main()
