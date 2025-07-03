# Telegram Auto-Join Bot

## Overview

This is a Python-based Telegram bot that provides auto-join functionality for Telegram groups and channels with a secure authentication system. The bot allows authorized users to automatically join groups using invite links and broadcast messages to all joined channels. It features a hardcoded access code authentication system and file-based storage for simplicity and security.

## System Architecture

The application follows a modular Python architecture with clear separation of concerns:

### Frontend Architecture
- **Command-based Interface**: Users interact through Telegram commands (/start, /help, /join, /bc, /list)
- **Two-step Authentication**: Users must provide access code "0722" before gaining bot access
- **Indonesian Language Support**: All user-facing messages are in Indonesian for localized experience
- **Real-time Feedback**: Immediate responses to user commands with detailed status messages

### Backend Architecture
- **Event-driven Design**: Uses Telegram webhook polling for real-time message processing
- **Modular Handler System**: Separate command handlers for different bot functionalities
- **File-based Storage**: JSON files for persistent data storage without external database dependency
- **Comprehensive Error Handling**: Graceful handling of network issues, API limits, and user errors

## Key Components

### Authentication System (`auth_system.py`)
- **Access Control**: Hardcoded access code "0722" for user verification
- **User Management**: Maintains authorized user list in JSON format (`authorized_users.json`)
- **Session Persistence**: Authorized users remain authenticated across bot restarts
- **Security Features**: Unauthorized access blocked with admin contact information (@OLVOII)

### Bot Command Handlers (`bot_handlers.py`)
- **Start Handler**: Initial bot interaction with authentication check
- **Help Handler**: Comprehensive usage instructions in Indonesian
- **Join Handler**: Processes Telegram invite links and attempts group joining
- **Broadcast Handler**: Mass messaging to all joined groups/channels
- **List Handler**: Display management of joined groups with detailed information
- **Message Handler**: Processes authentication codes and handles unauthorized access attempts

### Chat Storage System (`chat_storage.py`)
- **File-based Storage**: JSON storage for chat information (`chat_storage.json`)
- **Chat Management**: Tracks joined groups/channels with metadata (title, type, invite link)
- **Data Persistence**: Automatic saving and loading of chat data
- **Error Handling**: Graceful handling of file corruption and missing data

### Configuration Management (`config.py`)
- **Environment Configuration**: Bot token management with environment variable support
- **Logging System**: Daily rotating logs with separate files for general logs and errors
- **Directory Management**: Automatic creation of required directories (logs/)

### Utility Functions (`utils.py`)
- **Link Validation**: Comprehensive validation for multiple Telegram invite link formats
- **Pattern Matching**: Supports t.me/+, t.me/joinchat/, telegram.me variants, and username formats
- **Hash Extraction**: Extracts invite hashes from different link formats
- **Logging Utilities**: Structured logging for join attempts and broadcast operations

## Data Flow

1. **User Authentication Flow**:
   - User sends any message to bot
   - Bot checks authorization status
   - If unauthorized, prompts for access code
   - User provides code "0722"
   - Bot verifies and grants access, saves user to authorized list

2. **Join Group Flow**:
   - User sends `/join [invite_link]` command
   - Bot validates invite link format
   - Bot attempts to join group/channel
   - Bot stores successful joins in chat storage
   - Bot provides feedback to user

3. **Broadcast Flow**:
   - User sends `/bc [message]` command
   - Bot retrieves all stored chat IDs
   - Bot sends message to each chat individually
   - Bot reports success/failure statistics

## External Dependencies

### Core Dependencies
- **python-telegram-bot==22.2**: Main Telegram bot framework
- **httpx>=0.27,<0.29**: HTTP client for API requests
- **anyio>=4.9.0**: Async I/O support
- **certifi>=2025.6.15**: SSL certificate verification
- **httpcore>=1.0.9**: HTTP protocol implementation

### System Requirements
- Python 3.7 or higher
- Stable internet connection
- Valid Telegram bot token from @BotFather

## Deployment Strategy

### Local Development
- Direct execution via `python main.py`
- Auto-restart capability with `run_bot.py` script
- File-based configuration and storage for simplicity

### Production Considerations
- Bot token should be provided via environment variables
- Log files rotate daily in `logs/` directory
- JSON storage files (`authorized_users.json`, `chat_storage.json`) require write permissions
- Error logs separated for monitoring critical issues

### Monitoring and Maintenance
- Comprehensive logging system with different log levels
- Daily log rotation for storage management
- Auto-restart script prevents downtime from crashes
- Maximum restart limits prevent infinite crash loops

## Changelog
- July 03, 2025. Initial setup with enhanced auto-join functionality
- July 03, 2025. Fixed missing dependencies and import errors
- July 03, 2025. Improved error handling and logging system
- July 03, 2025. Enhanced auto-join feature with comprehensive invite link support
- July 03, 2025. Implemented hybrid auto-join system using user accounts for private groups
- July 03, 2025. Added Telethon integration for true auto-join functionality
- July 03, 2025. Created setup scripts for user account authentication

## User Preferences

Preferred communication style: Simple, everyday language.