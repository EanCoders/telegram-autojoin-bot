"""
Bot command handlers for Telegram Auto-Join Bot
Simplified and realistic approach for auto-join functionality
"""

import logging
import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from telegram import Update
    from telegram.ext import ContextTypes
    from telegram.error import TelegramError, BadRequest, Forbidden, TimedOut
except ImportError as e:
    print(f"Error importing telegram: {e}")
    try:
        import telegram
        from telegram.ext import ContextTypes
        from telegram.error import TelegramError, BadRequest, Forbidden, TimedOut
        Update = telegram.Update
    except ImportError as e2:
        print(f"Failed to import telegram: {e2}")
        sys.exit(1)

from utils import validate_telegram_invite_link, extract_invite_hash, log_join_attempt, format_help_message, log_broadcast_attempt
from chat_storage import chat_storage
from auth_system import AuthSystem
from hybrid_autojoin import hybrid_autojoin, setup_hybrid_system, join_with_user_account

logger = logging.getLogger(__name__)

# Initialize authentication system
auth_system = AuthSystem()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command"""
    user = update.effective_user
    logger.info(f"User {user.username}({user.id}) started the bot")
    
    # Check if user is authorized
    if not auth_system.is_authorized(user.id):
        await update.message.reply_text(auth_system.get_unauthorized_message())
        return
    
    welcome_message = f"""
🤖 Selamat datang, {user.first_name}!

Saya adalah bot yang dapat membantu Anda bergabung ke grup/channel Telegram secara otomatis menggunakan invite link.

Cara menggunakan:
Kirim perintah /join diikuti dengan link invite grup/channel.

Contoh: /join https://t.me/+abc123def456

Ketik /help untuk informasi lebih lengkap.
    """
    
    await update.message.reply_text(welcome_message)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /help command"""
    user = update.effective_user
    logger.info(f"User {user.username}({user.id}) requested help")
    
    # Check if user is authorized
    if not auth_system.is_authorized(user.id):
        await update.message.reply_text(auth_system.get_unauthorized_message())
        return
    
    help_text = format_help_message()
    await update.message.reply_text(help_text)

async def join_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /join command - Realistic approach for bot limitations"""
    user = update.effective_user
    user_id = user.id
    username = user.username or user.first_name
    
    logger.info(f"User {username}({user_id}) requested join command")
    logger.info(f"Full message: {update.message.text}")
    
    # Check if user is authorized
    if not auth_system.is_authorized(user_id):
        await update.message.reply_text(auth_system.get_unauthorized_message())
        return
    
    # Get the full message text and extract the link
    message_text = update.message.text
    if len(message_text.split()) < 2:
        await update.message.reply_text(
            "❌ Link invite tidak diberikan!\n\n"
            "Gunakan format: /join [link]\n"
            "Contoh: /join https://t.me/+abc123def456\n\n"
            "Ketik /help untuk informasi lebih lengkap."
        )
        return
    
    # Get the invite link from the message
    invite_link = " ".join(message_text.split()[1:])
    
    # Validate the invite link
    is_valid, error_msg = validate_telegram_invite_link(invite_link)
    
    if not is_valid:
        await update.message.reply_text(
            f"❌ Link tidak valid!\n\n"
            f"Error: {error_msg}\n\n"
            "Pastikan menggunakan format link yang benar:\n"
            "• https://t.me/+abc123\n"
            "• https://t.me/joinchat/abc123"
        )
        log_join_attempt(user_id, username, invite_link, False, error_msg or "Invalid link")
        return
    
    # Send processing message
    processing_msg = await update.message.reply_text(
        "⏳ Sedang memproses...\n\n"
        "Mengecek status grup/channel..."
    )
    
    try:
        # Extract invite hash or username
        invite_hash = extract_invite_hash(invite_link)
        
        # Handle different link types
        if "/joinchat/" in invite_link or "/+" in invite_link:
            # Private group invite link - gunakan user account
            await processing_msg.edit_text(
                "🔄 Mencoba bergabung menggunakan user account...\n\n"
                f"Link: {invite_link}\n"
                f"Hash: {invite_hash}\n\n"
                "⚙️ Menggunakan sistem hybrid untuk auto-join private group..."
            )
            
            # Cek apakah user account sudah setup
            if not hybrid_autojoin.is_user_configured():
                await processing_msg.edit_text(
                    "❌ User Account Belum Dikonfigurasi!\n\n"
                    "Untuk auto-join ke private group, diperlukan setup user account.\n\n"
                    "📋 Cara Setup:\n"
                    "1. Jalankan: python hybrid_autojoin.py\n"
                    "2. Masukkan API ID dan API Hash dari my.telegram.org\n"
                    "3. Verifikasi dengan: python verify_user_account.py\n"
                    "4. Restart bot\n\n"
                    "Setelah setup, bot dapat auto-join ke private group!"
                )
                log_join_attempt(user_id, username, invite_link, False, "User account not configured")
                return
            
            # Setup user account jika belum
            if not await setup_hybrid_system():
                await processing_msg.edit_text(
                    "❌ Gagal setup user account!\n\n"
                    "Kemungkinan masalah:\n"
                    "• Session expired\n"
                    "• API credentials tidak valid\n"
                    "• Akun tidak ter-authorize\n\n"
                    "Jalankan lagi: python verify_user_account.py"
                )
                log_join_attempt(user_id, username, invite_link, False, "Failed to setup user account")
                return
            
            # Join menggunakan user account
            await processing_msg.edit_text(
                "🚀 Bergabung ke private group...\n\n"
                "Menggunakan user account untuk auto-join..."
            )
            
            result = await join_with_user_account(invite_link)
            
            if result['success']:
                group_info = result['group_info']
                await processing_msg.edit_text(
                    "✅ BERHASIL AUTO-JOIN!\n\n"
                    f"Grup: {group_info['title']}\n"
                    f"Type: {group_info['type'].title()}\n"
                    f"ID: {group_info['id']}\n"
                    f"Members: {group_info.get('participants_count', 'N/A')}\n\n"
                    "🎉 Sekarang bot dapat broadcast ke grup ini!\n"
                    f"Total chat tersimpan: {chat_storage.get_chat_count()}"
                )
                log_join_attempt(user_id, username, invite_link, True, "Successfully joined using user account")
            else:
                await processing_msg.edit_text(
                    f"❌ Gagal bergabung!\n\n"
                    f"Error: {result['error']}\n\n"
                    "Kemungkinan penyebab:\n"
                    "• Link invite sudah kedaluwarsa\n"
                    "• Link invite tidak valid\n"
                    "• Sudah menjadi anggota\n"
                    "• Rate limit dari Telegram\n\n"
                    "Coba lagi dengan link yang baru atau tunggu beberapa menit."
                )
                log_join_attempt(user_id, username, invite_link, False, result['error'])
            return
        
        elif invite_hash and not ("/" in invite_hash):
            # Public username format
            try:
                # Try to get chat information
                chat = await context.bot.get_chat(f"@{invite_hash}")
                
                # Check if bot is already a member
                try:
                    member = await context.bot.get_chat_member(chat.id, context.bot.id)
                    if member.status in ['member', 'administrator', 'creator']:
                        # Bot is already a member
                        if not chat_storage.is_chat_stored(chat.id):
                            chat_storage.add_chat(
                                chat_id=chat.id,
                                chat_title=chat.title or f"Chat {chat.id}",
                                chat_type=chat.type,
                                invite_link=invite_link
                            )
                        
                        await processing_msg.edit_text(
                            "✅ Bot sudah menjadi anggota!\n\n"
                            f"Grup/Channel: {chat.title}\n"
                            f"Type: {chat.type.title()}\n"
                            f"ID: {chat.id}\n\n"
                            "✅ Disimpan untuk broadcast!\n"
                            f"Total chat tersimpan: {chat_storage.get_chat_count()}"
                        )
                        log_join_attempt(user_id, username, invite_link, True)
                        return
                    else:
                        # Bot is not a member
                        await processing_msg.edit_text(
                            f"❌ Bot belum menjadi anggota!\n\n"
                            f"Chat: {chat.title}\n"
                            f"Type: {chat.type.title()}\n"
                            f"Username: @{invite_hash}\n\n"
                            "🔧 Untuk public chat/channel:\n"
                            "1. Buka chat tersebut secara manual\n"
                            "2. Tambahkan bot sebagai anggota\n"
                            "3. Atau minta admin untuk menambahkan bot\n\n"
                            "Bot tidak dapat bergabung otomatis ke public chat."
                        )
                        log_join_attempt(user_id, username, invite_link, False, "Bot not a member of public chat")
                        return
                        
                except Exception as member_error:
                    await processing_msg.edit_text(
                        f"⚠️ Tidak dapat mengecek status keanggotaan!\n\n"
                        f"Chat: {chat.title}\n"
                        f"Error: {str(member_error)}\n\n"
                        "Kemungkinan:\n"
                        "1. Bot belum ditambahkan ke grup/channel\n"
                        "2. Grup/channel bersifat restricted\n"
                        "3. Bot tidak memiliki akses\n\n"
                        "Tambahkan bot sebagai anggota biasa dan coba lagi."
                    )
                    log_join_attempt(user_id, username, invite_link, False, f"Cannot check membership: {str(member_error)}")
                    return
                    
            except Exception as chat_error:
                await processing_msg.edit_text(
                    f"❌ Chat tidak ditemukan!\n\n"
                    f"Username: @{invite_hash}\n"
                    f"Error: {str(chat_error)}\n\n"
                    "Kemungkinan penyebab:\n"
                    "• Username salah atau tidak ada\n"
                    "• Chat bersifat private\n"
                    "• Chat telah dihapus\n\n"
                    "Periksa kembali link yang Anda berikan."
                )
                log_join_attempt(user_id, username, invite_link, False, f"Chat not found: {str(chat_error)}")
                return
        
        else:
            # Invalid or unsupported link format
            await processing_msg.edit_text(
                "❌ Format link tidak didukung!\n\n"
                f"Link: {invite_link}\n\n"
                "Format yang didukung:\n"
                "• https://t.me/username (public chat)\n"
                "• https://t.me/+hash (private invite)\n"
                "• https://t.me/joinchat/hash (private invite)\n\n"
                "Periksa kembali format link Anda."
            )
            log_join_attempt(user_id, username, invite_link, False, "Unsupported link format")
            return
            
    except Exception as e:
        logger.error(f"Critical error in join command: {e}")
        try:
            await processing_msg.edit_text(
                "💥 Error sistem!\n\n"
                "Sistem mengalami masalah. Coba lagi nanti."
            )
        except:
            await update.message.reply_text(
                "💥 Error sistem!\n\n"
                "Sistem mengalami masalah. Coba lagi nanti."
            )
        log_join_attempt(user_id, username, invite_link, False, f"System error: {str(e)}")
        return

async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /bc command to broadcast messages to all joined groups/channels"""
    user = update.effective_user
    user_id = user.id
    username = user.username or user.first_name
    
    logger.info(f"User {username}({user_id}) requested broadcast command")
    
    # Check if user is authorized
    if not auth_system.is_authorized(user_id):
        await update.message.reply_text(auth_system.get_unauthorized_message())
        return
    
    # Get broadcast message
    message_text = update.message.text
    if len(message_text.split()) < 2:
        await update.message.reply_text(
            "❌ Pesan broadcast tidak diberikan!\n\n"
            "Gunakan format: /bc [pesan]\n"
            "Contoh: /bc Halo semua! Ini adalah pesan broadcast.\n\n"
            "Ketik /help untuk informasi lebih lengkap."
        )
        return
    
    # Extract broadcast message
    broadcast_message = " ".join(message_text.split()[1:])
    
    # Get all stored chats
    all_chats = chat_storage.get_all_chats()
    
    if not all_chats:
        await update.message.reply_text(
            "❌ Tidak ada chat tersimpan!\n\n"
            "Gunakan /join untuk bergabung ke grup/channel terlebih dahulu.\n"
            "Gunakan /list untuk melihat chat yang tersimpan."
        )
        return
    
    # Send status message
    status_msg = await update.message.reply_text(
        f"📤 Memulai broadcast ke {len(all_chats)} chat...\n\n"
        f"Pesan: {broadcast_message[:50]}{'...' if len(broadcast_message) > 50 else ''}"
    )
    
    success_count = 0
    failed_count = 0
    
    # Broadcast to all chats
    for chat_info in all_chats:
        try:
            await context.bot.send_message(
                chat_id=chat_info['chat_id'],
                text=broadcast_message
            )
            chat_storage.update_last_broadcast(chat_info['chat_id'])
            success_count += 1
            logger.info(f"Broadcast sent to {chat_info['title']} ({chat_info['chat_id']})")
        except Exception as e:
            failed_count += 1
            logger.warning(f"Failed to send broadcast to {chat_info['title']} ({chat_info['chat_id']}): {e}")
    
    # Update status message with results
    await status_msg.edit_text(
        f"📊 Hasil Broadcast:\n\n"
        f"✅ Berhasil: {success_count}\n"
        f"❌ Gagal: {failed_count}\n"
        f"📋 Total: {len(all_chats)}\n\n"
        f"Pesan: {broadcast_message[:100]}{'...' if len(broadcast_message) > 100 else ''}"
    )
    
    log_broadcast_attempt(user_id, username, broadcast_message, success_count, failed_count)

async def list_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /list command to show all joined groups/channels"""
    user = update.effective_user
    user_id = user.id
    username = user.username or user.first_name
    
    logger.info(f"User {username}({user_id}) requested list command")
    
    # Check if user is authorized
    if not auth_system.is_authorized(user_id):
        await update.message.reply_text(auth_system.get_unauthorized_message())
        return
    
    # Get all stored chats
    all_chats = chat_storage.get_all_chats()
    
    if not all_chats:
        await update.message.reply_text(
            "📋 Tidak ada chat tersimpan!\n\n"
            "Gunakan /join [link] untuk bergabung ke grup/channel.\n"
            "Contoh: /join https://t.me/+abc123def456"
        )
        return
    
    # Format chat list
    chat_list = "📋 Daftar Chat yang Tersimpan:\n\n"
    
    for i, chat_info in enumerate(all_chats, 1):
        chat_type_emoji = "📢" if chat_info['type'] == 'channel' else "👥"
        chat_list += f"{i}. {chat_type_emoji} {chat_info['title']}\n"
        chat_list += f"   Type: {chat_info['type'].title()}\n"
        chat_list += f"   ID: {chat_info['chat_id']}\n"
        if chat_info.get('last_broadcast'):
            chat_list += f"   Last broadcast: {chat_info['last_broadcast'][:10]}\n"
        chat_list += "\n"
    
    chat_list += f"📊 Total: {len(all_chats)} chat"
    
    # Split message if too long
    if len(chat_list) > 4000:
        # Send in chunks
        chunks = [chat_list[i:i+4000] for i in range(0, len(chat_list), 4000)]
        for chunk in chunks:
            await update.message.reply_text(chunk)
    else:
        await update.message.reply_text(chat_list)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle non-command messages for authentication"""
    user = update.effective_user
    user_id = user.id
    username = user.username or user.first_name
    message_text = update.message.text
    
    logger.info(f"User {username}({user_id}) sent message: {message_text}")
    
    # If user is already authorized, ignore
    if auth_system.is_authorized(user_id):
        await update.message.reply_text(
            "✅ Anda sudah terotorisasi!\n\n"
            "Gunakan /help untuk melihat perintah yang tersedia."
        )
        return
    
    # Check if message is access code
    if auth_system.verify_code(user_id, message_text):
        await update.message.reply_text(auth_system.get_access_granted_message())
        logger.info(f"User {username}({user_id}) authenticated successfully")
    else:
        await update.message.reply_text(auth_system.get_invalid_code_message())
        logger.warning(f"User {username}({user_id}) provided invalid access code: {message_text}")