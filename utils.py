"""
Utility functions for the Telegram bot
Contains validation and helper functions with improved invite link handling
"""

import re
import logging
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

def validate_telegram_invite_link(link: str) -> Tuple[bool, Optional[str]]:
    """
    Validate if the provided link is a valid Telegram invite link
    
    Args:
        link (str): The invite link to validate
        
    Returns:
        Tuple[bool, Optional[str]]: (is_valid, error_message)
    """
    if not link or not isinstance(link, str):
        return False, "Link tidak boleh kosong"
    
    # Remove whitespace and common prefixes
    link = link.strip()
    
    # Telegram invite link patterns (updated and more comprehensive)
    patterns = [
        # New format invite links
        r'^https?://t\.me/\+[a-zA-Z0-9_-]+$',
        r'^https?://telegram\.me/\+[a-zA-Z0-9_-]+$',
        
        # Old format invite links
        r'^https?://t\.me/joinchat/[a-zA-Z0-9_-]+$',
        r'^https?://telegram\.me/joinchat/[a-zA-Z0-9_-]+$',
        
        # Username/channel format
        r'^https?://t\.me/[a-zA-Z0-9_][a-zA-Z0-9_]*$',
        r'^https?://telegram\.me/[a-zA-Z0-9_][a-zA-Z0-9_]*$',
        
        # Direct username format (without http)
        r'^@[a-zA-Z0-9_][a-zA-Z0-9_]*$',
        
        # Username only format
        r'^[a-zA-Z0-9_][a-zA-Z0-9_]*$',
    ]
    
    # Check each pattern
    for pattern in patterns:
        if re.match(pattern, link):
            logger.info(f"Valid invite link format detected: {link}")
            return True, None
    
    # Additional validation for edge cases
    if link.startswith('t.me/') or link.startswith('telegram.me/'):
        # Try with https prefix
        return validate_telegram_invite_link(f"https://{link}")
    
    return False, "Format link tidak valid. Gunakan format: https://t.me/+abc123, https://t.me/joinchat/abc123, https://t.me/username, atau @username"

def extract_invite_hash(link: str) -> Optional[str]:
    """
    Extract invite hash from Telegram invite link
    
    Args:
        link (str): The invite link
        
    Returns:
        Optional[str]: The invite hash or None if not found
    """
    if not link:
        return None
    
    # Pattern to extract hash from different link formats
    patterns = [
        r'https?://t\.me/\+([a-zA-Z0-9_-]+)',
        r'https?://t\.me/joinchat/([a-zA-Z0-9_-]+)',
        r'https?://telegram\.me/joinchat/([a-zA-Z0-9_-]+)',
        r'https?://telegram\.me/\+([a-zA-Z0-9_-]+)',
        r'https?://t\.me/([a-zA-Z0-9_][a-zA-Z0-9_]*)',
        r'https?://telegram\.me/([a-zA-Z0-9_][a-zA-Z0-9_]*)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, link)
        if match:
            hash_value = match.group(1)
            logger.info(f"Extracted hash from link: {hash_value}")
            return hash_value
    
    # Handle direct username formats
    if link.startswith('@'):
        return link[1:]
    
    # Handle plain username
    if re.match(r'^[a-zA-Z0-9_][a-zA-Z0-9_]*$', link):
        return link
    
    logger.warning(f"Could not extract hash from link: {link}")
    return None

def normalize_invite_link(link: str) -> str:
    """
    Normalize invite link to standard format
    
    Args:
        link (str): The invite link to normalize
        
    Returns:
        str: Normalized invite link
    """
    if not link:
        return link
    
    link = link.strip()
    
    # Handle different formats
    if link.startswith('@'):
        return f"https://t.me/{link[1:]}"
    elif re.match(r'^[a-zA-Z0-9_][a-zA-Z0-9_]*$', link):
        return f"https://t.me/{link}"
    elif link.startswith('t.me/'):
        return f"https://{link}"
    elif link.startswith('telegram.me/'):
        return f"https://{link}"
    
    return link

def log_join_attempt(user_id: int, username: str, link: str, success: bool, error_msg: str = None):
    """
    Log join attempt with details
    
    Args:
        user_id (int): User ID who requested the join
        username (str): Username who requested the join
        link (str): The invite link used
        success (bool): Whether the join was successful
        error_msg (str, optional): Error message if join failed
    """
    status = "SUCCESS" if success else "FAILED"
    log_msg = f"JOIN_ATTEMPT - User: {username}({user_id}) - Link: {link} - Status: {status}"
    
    if not success and error_msg:
        log_msg += f" - Error: {error_msg}"
    
    if success:
        logger.info(log_msg)
    else:
        logger.warning(log_msg)

def log_broadcast_attempt(user_id: int, username: str, message: str, success_count: int, failed_count: int, error_msg: str = None):
    """
    Log broadcast attempt with details
    
    Args:
        user_id (int): User ID who requested the broadcast
        username (str): Username who requested the broadcast
        message (str): The broadcast message
        success_count (int): Number of successful sends
        failed_count (int): Number of failed sends
        error_msg (str, optional): Error message if broadcast failed
    """
    total_count = success_count + failed_count
    status = "SUCCESS" if failed_count == 0 else "PARTIAL" if success_count > 0 else "FAILED"
    
    log_msg = f"BROADCAST_ATTEMPT - User: {username}({user_id}) - Message: {message[:50]}{'...' if len(message) > 50 else ''} - Status: {status} - Success: {success_count}/{total_count}"
    
    if error_msg:
        log_msg += f" - Error: {error_msg}"
    
    if status == "SUCCESS":
        logger.info(log_msg)
    elif status == "PARTIAL":
        logger.warning(log_msg)
    else:
        logger.error(log_msg)

def format_help_message() -> str:
    """
    Format help message for the bot
    
    Returns:
        str: Formatted help message
    """
    help_text = """
🤖 **Telegram Auto-Join Bot**

**Perintah yang tersedia:**

/start - Memulai bot dan menampilkan pesan selamat datang
/help - Menampilkan pesan bantuan ini
/join [link] - Bergabung ke grup/channel menggunakan invite link
/bc [teks] - Broadcast pesan ke semua grup/channel
/list - Menampilkan daftar grup/channel yang telah diikuti bot

**Cara menggunakan:**

**1. Bergabung ke grup/channel:**
   `/join https://t.me/+abc123def456`
   `/join https://t.me/joinchat/abc123`
   `/join https://t.me/username`
   `/join @username`

**2. Broadcast pesan:**
   `/bc Halo semua! Ini adalah pesan broadcast.`

**3. Lihat daftar chat:**
   `/list`

**Format link yang didukung:**
- https://t.me/+abc123 (link invite baru)
- https://t.me/joinchat/abc123 (link invite lama)
- https://t.me/username (public chat/channel)
- @username (username langsung)

**Fitur Auto-Join:**
- Bot akan otomatis mencoba bergabung menggunakan invite link
- Jika gagal, bot akan memberikan instruksi manual
- Bot dapat bergabung ke private group dengan invite link
- Public chat mungkin memerlukan penambahan manual

**Catatan Penting:**
- Pastikan invite link valid dan belum kedaluwarsa
- Beberapa grup/channel mungkin memblokir bot
- Bot akan menyimpan semua chat yang berhasil diikuti
- Fitur broadcast mengirim pesan ke semua chat tersimpan
- Gunakan dengan bijak untuk menghindari spam

Jika ada masalah, periksa format link dan pastikan link masih aktif.
    """
    return help_text.strip()

def get_chat_type_emoji(chat_type: str) -> str:
    """
    Get emoji for chat type
    
    Args:
        chat_type (str): The chat type
        
    Returns:
        str: Emoji representing the chat type
    """
    emoji_map = {
        'private': '👤',
        'group': '👥',
        'supergroup': '🏢',
        'channel': '📢'
    }
    return emoji_map.get(chat_type.lower(), '💬')

def format_error_message(error: str, context: str = "") -> str:
    """
    Format error message for user display
    
    Args:
        error (str): The error message
        context (str): Additional context
        
    Returns:
        str: Formatted error message
    """
    error_lower = error.lower()
    
    if "user is already a participant" in error_lower:
        return "✅ Bot sudah menjadi anggota chat ini!"
    elif "invite link is invalid" in error_lower:
        return "❌ Link invite tidak valid atau sudah kedaluwarsa!"
    elif "chat not found" in error_lower:
        return "❌ Chat tidak ditemukan!"
    elif "forbidden" in error_lower:
        return "❌ Akses ditolak! Bot mungkin diblokir oleh admin."
    elif "flood" in error_lower:
        return "⚠️ Terlalu banyak permintaan. Tunggu sebentar lalu coba lagi."
    elif "timeout" in error_lower:
        return "⏱️ Timeout! Coba lagi dalam beberapa menit."
    else:
        return f"❌ Error: {error}"
