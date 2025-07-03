"""
Configuration file for the Telegram bot
Contains bot token and enhanced logging setup
"""

import logging
import os
from datetime import datetime

# Bot token - get from environment variable with fallback
BOT_TOKEN = os.getenv("BOT_TOKEN", "8076072273:AAEp87CvX6ykImJey3r_vWo_iZ4gx_cOj7M")

def setup_logging():
    """Setup enhanced logging configuration"""
    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)
    
    # Configure logging with more detailed format
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    
    # File handler with rotation
    log_filename = f'logs/bot_{datetime.now().strftime("%Y%m%d")}.log'
    file_handler = logging.FileHandler(log_filename, encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter(log_format, date_format))
    
    # Console handler with colored output for development
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter(log_format, date_format))
    
    # Error file handler for critical issues
    error_filename = f'logs/error_{datetime.now().strftime("%Y%m%d")}.log'
    error_handler = logging.FileHandler(error_filename, encoding='utf-8')
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(logging.Formatter(log_format, date_format))
    
    # Root logger configuration
    logging.basicConfig(
        level=logging.INFO,
        handlers=[file_handler, console_handler, error_handler],
        format=log_format,
        datefmt=date_format
    )
    
    # Reduce telegram library verbosity but keep important messages
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("telegram").setLevel(logging.INFO)
    logging.getLogger("telegram.ext").setLevel(logging.INFO)
    
    # Add custom logger for join attempts
    join_logger = logging.getLogger("join_attempts")
    join_handler = logging.FileHandler(f'logs/join_attempts_{datetime.now().strftime("%Y%m%d")}.log', encoding='utf-8')
    join_handler.setLevel(logging.INFO)
    join_handler.setFormatter(logging.Formatter(log_format, date_format))
    join_logger.addHandler(join_handler)
    join_logger.setLevel(logging.INFO)
    
    # Add custom logger for broadcast attempts
    broadcast_logger = logging.getLogger("broadcast_attempts")
    broadcast_handler = logging.FileHandler(f'logs/broadcast_attempts_{datetime.now().strftime("%Y%m%d")}.log', encoding='utf-8')
    broadcast_handler.setLevel(logging.INFO)
    broadcast_handler.setFormatter(logging.Formatter(log_format, date_format))
    broadcast_logger.addHandler(broadcast_handler)
    broadcast_logger.setLevel(logging.INFO)
    
    # Log startup information
    logger = logging.getLogger(__name__)
    logger.info("="*50)
    logger.info("Starting Telegram Auto-Join Bot")
    logger.info(f"Log files: {log_filename}, {error_filename}")
    logger.info(f"Bot token configured: {'Yes' if BOT_TOKEN else 'No'}")
    logger.info("="*50)

def get_bot_info():
    """Get bot configuration information"""
    return {
        'bot_token_configured': bool(BOT_TOKEN),
        'log_directory': 'logs',
        'log_files': [
            f'bot_{datetime.now().strftime("%Y%m%d")}.log',
            f'error_{datetime.now().strftime("%Y%m%d")}.log',
            f'join_attempts_{datetime.now().strftime("%Y%m%d")}.log',
            f'broadcast_attempts_{datetime.now().strftime("%Y%m%d")}.log'
        ]
    }
