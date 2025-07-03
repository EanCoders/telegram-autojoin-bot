"""
Bot command handlers for Telegram Auto-Join Bot
Contains all command handling logic with improved auto-join functionality
"""

import logging
import sys
import os
import asyncio

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from telegram import Update, Chat
    from telegram.ext import ContextTypes
    from telegram.error import TelegramError, BadRequest, Forbidden, TimedOut, ChatMigrated
except ImportError as e:
    print(f"Error importing telegram: {e}")
    try:
        import telegram
        from telegram.ext import ContextTypes
        from telegram.error import TelegramError, BadRequest, Forbidden, TimedOut, ChatMigrated
        Update = telegram.Update
        Chat = telegram.Chat
    except ImportError as e2:
        print(f"Failed to import telegram: {e2}")
        sys.exit(1)

from utils import validate_telegram_invite_link, extract_invite_hash, log_join_attempt, format_help_message, log_broadcast_attempt
from chat_storage import chat_storage
from auth_system import AuthSystem

logger = logging.getLogger(__name__)

# Initialize authentication system
auth_system = AuthSystem()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle /start command
    
    Args:
        update: Telegram update object
        context: Bot context
    """
    user = update.effective_user
    logger.info(f"User {user.username}({user.id}) started the bot")
    
    # Check if user is authorized
    if not auth_system.is_authorized(user.id):
        await update.message.reply_text(auth_system.get_unauthorized_message())
        return
    
    welcome_message = f"""
🤖 **Selamat datang, {user.first_name}!**

Saya adalah bot yang dapat membantu Anda bergabung ke grup/channel Telegram secara otomatis menggunakan invite link.

**Cara menggunakan:**
Kirim perintah `/join` diikuti dengan link invite grup/channel.

Contoh: `/join https://t.me/+abc123def456`

Ketik /help untuk informasi lebih lengkap.
    """
    
    await update.message.reply_text(welcome_message, parse_mode='Markdown')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle /help command
    
    Args:
        update: Telegram update object
        context: Bot context
    """
    user = update.effective_user
    logger.info(f"User {user.username}({user.id}) requested help")
    
    # Check if user is authorized
    if not auth_system.is_authorized(user.id):
        await update.message.reply_text(auth_system.get_unauthorized_message())
        return
    
    help_text = format_help_message()
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def join_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle /join command to join groups/channels with improved auto-join functionality
    
    Args:
        update: Telegram update object
        context: Bot context
    """
    user = update.effective_user
    user_id = user.id
    username = user.username or user.first_name
    
    logger.info(f"User {username}({user_id}) requested join command")
    logger.info(f"Command args: {context.args}")
    logger.info(f"Full message: {update.message.text}")
    
    # Check if user is authorized
    if not auth_system.is_authorized(user_id):
        await update.message.reply_text(auth_system.get_unauthorized_message())
        return
    
    # Get the full message text and extract the link
    message_text = update.message.text
    # Remove the command part to get the link
    if len(message_text.split()) < 2:
        await update.message.reply_text(
            "❌ **Link invite tidak diberikan!**\n\n"
            "Gunakan format: `/join [link]`\n"
            "Contoh: `/join https://t.me/+abc123def456`\n\n"
            "Ketik /help untuk informasi lebih lengkap.",
            parse_mode='Markdown'
        )
        return
    
    # Get the invite link from the message
    invite_link = " ".join(message_text.split()[1:])
    
    # Validate the invite link
    is_valid, error_msg = validate_telegram_invite_link(invite_link)
    
    if not is_valid:
        await update.message.reply_text(
            f"❌ **Link tidak valid!**\n\n"
            f"Error: {error_msg}\n\n"
            "Pastikan menggunakan format link yang benar:\n"
            "• https://t.me/+abc123\n"
            "• https://t.me/joinchat/abc123",
            parse_mode='Markdown'
        )
        log_join_attempt(user_id, username, invite_link, False, error_msg)
        return
    
    # Send processing message
    processing_msg = await update.message.reply_text(
        "⏳ **Sedang memproses...**\n\n"
        "Mencoba bergabung ke grup/channel...",
        parse_mode='Markdown'
    )
    
    try:
        # Try to join the chat using the invite link
        chat = None
        join_successful = False
        
        # First, try to join using the invite link directly
        try:
            logger.info(f"Attempting to join chat using invite link: {invite_link}")
            
            # For invite links with hash, try to get chat info and check membership
            if "/joinchat/" in invite_link or "/+" in invite_link:
                # Extract the invite hash
                invite_hash = extract_invite_hash(invite_link)
                if invite_hash:
                    # Try to get chat info first (Bot cannot auto-join private groups)
                    try:
                        # Bot cannot actually join private groups automatically
                        # This is a Telegram API limitation for bots
                        await processing_msg.edit_text(
                            "⚠️ **Bot Tidak Dapat Auto-Join ke Private Group**\n\n"
                            f"**Link**: `{invite_link}`\n"
                            f"**Hash**: `{invite_hash}`\n\n"
                            "🤖 **Keterbatasan Telegram Bot API:**\n"
                            "• Bot tidak dapat bergabung otomatis ke private group\n"
                            "• Telegram tidak mengizinkan bot join melalui invite link\n"
                            "• Ini adalah batasan keamanan dari Telegram\n\n"
                            "📋 **Cara Manual:**\n"
                            "1. Buka link dan join secara manual\n"
                            "2. Tambahkan bot ke grup sebagai anggota\n"
                            "3. Bot akan otomatis mendeteksi sudah menjadi anggota\n"
                            "4. Gunakan `/list` untuk lihat grup yang sudah diikuti\n\n"
                            "✅ **Bot sudah mencatat link ini untuk referensi**",
                            parse_mode='Markdown'
                        )
                        log_join_attempt(user_id, username, invite_link, False, "Bot cannot auto-join private groups")
                        return
                    except BadRequest as e:
                        error_msg = str(e).lower()
                        if "user is already a participant" in error_msg:
                            # Bot is already a member, get chat info
                            try:
                                # Try different methods to get chat info
                                chat = await context.bot.get_chat(invite_link)
                                join_successful = True
                                logger.info(f"Bot already member of chat: {chat.title} ({chat.id})")
                            except:
                                # If we can't get chat info, try with the hash
                                chat_id = f"@{invite_hash}"
                                try:
                                    chat = await context.bot.get_chat(chat_id)
                                    join_successful = True
                                except:
                                    pass
                        elif "invite link is invalid" in error_msg:
                            await processing_msg.edit_text(
                                "❌ **Link invite tidak valid atau kedaluwarsa!**\n\n"
                                "Kemungkinan penyebab:\n"
                                "• Link invite sudah kedaluwarsa\n"
                                "• Link invite telah dibatalkan\n"
                                "• Format link salah\n\n"
                                "Minta link invite yang baru dari admin grup/channel.",
                                parse_mode='Markdown'
                            )
                            log_join_attempt(user_id, username, invite_link, False, "Invalid invite link")
                            return
                        elif "flood control" in error_msg:
                            await processing_msg.edit_text(
                                "⚠️ **Flood Control - Terlalu Banyak Permintaan!**\n\n"
                                "Telegram membatasi jumlah join dalam waktu singkat.\n"
                                "Tunggu beberapa menit lalu coba lagi.\n\n"
                                "💡 **Tips**: Jangan join terlalu banyak grup dalam waktu bersamaan.",
                                parse_mode='Markdown'
                            )
                            log_join_attempt(user_id, username, invite_link, False, "Flood control")
                            return
                        else:
                            raise e
                    except Forbidden as e:
                        await processing_msg.edit_text(
                            "❌ **Akses Ditolak!**\n\n"
                            "Kemungkinan penyebab:\n"
                            "• Bot diblokir oleh admin grup/channel\n"
                            "• Grup/channel tidak mengizinkan bot\n"
                            "• Bot tidak memiliki izin untuk bergabung\n\n"
                            "Hubungi admin grup/channel untuk mengizinkan bot bergabung.",
                            parse_mode='Markdown'
                        )
                        log_join_attempt(user_id, username, invite_link, False, "Forbidden access")
                        return
                    except TimedOut:
                        await processing_msg.edit_text(
                            "⏱️ **Timeout!**\n\n"
                            "Permintaan membutuhkan waktu terlalu lama.\n"
                            "Coba lagi dalam beberapa menit.\n\n"
                            "Jika masalah berlanjut, periksa koneksi internet Anda.",
                            parse_mode='Markdown'
                        )
                        log_join_attempt(user_id, username, invite_link, False, "Timeout")
                        return
                    except ChatMigrated as e:
                        # Chat has been migrated to a supergroup
                        new_chat_id = e.new_chat_id
                        try:
                            chat = await context.bot.get_chat(new_chat_id)
                            join_successful = True
                            logger.info(f"Chat migrated, got new chat: {chat.title} ({chat.id})")
                        except:
                            await processing_msg.edit_text(
                                "⚠️ **Chat Migrasi Terdeteksi!**\n\n"
                                "Grup telah dimigrasikan ke supergroup.\n"
                                "Coba dengan link invite yang baru.\n\n"
                                "Minta link invite terbaru dari admin grup.",
                                parse_mode='Markdown'
                            )
                            log_join_attempt(user_id, username, invite_link, False, "Chat migrated")
                            return
                else:
                    await processing_msg.edit_text(
                        "❌ **Gagal mengekstrak hash dari link invite!**\n\n"
                        "Pastikan format link benar:\n"
                        "• https://t.me/+abc123\n"
                        "• https://t.me/joinchat/abc123",
                        parse_mode='Markdown'
                    )
                    log_join_attempt(user_id, username, invite_link, False, "Invalid hash extraction")
                    return
            else:
                # For username-based links, try to get chat info first
                username_extracted = invite_link.split('/')[-1]
                if username_extracted.startswith('@'):
                    username_extracted = username_extracted[1:]
                
                try:
                    # Get chat information by username
                    chat = await context.bot.get_chat(f"@{username_extracted}")
                    
                    # Check if bot is already a member
                    try:
                        member = await context.bot.get_chat_member(chat.id, context.bot.id)
                        if member.status in ['member', 'administrator', 'creator']:
                            join_successful = True
                            logger.info(f"Bot already member of public chat: {chat.title} ({chat.id})")
                        else:
                            # Try to join public chat (this usually doesn't work for bots)
                            try:
                                await context.bot.join_chat(f"@{username_extracted}")
                                join_successful = True
                                logger.info(f"Successfully joined public chat: {chat.title} ({chat.id})")
                            except:
                                # Public chats usually require manual addition
                                await processing_msg.edit_text(
                                    f"⚠️ **Public Chat Ditemukan!**\n\n"
                                    f"**Chat**: {chat.title}\n"
                                    f"**Type**: {chat.type.title()}\n"
                                    f"**Username**: @{username_extracted}\n\n"
                                    "🔧 **Untuk public chat/channel:**\n"
                                    "1. Buka chat tersebut secara manual\n"
                                    "2. Tambahkan bot sebagai anggota\n"
                                    "3. Atau minta admin untuk menambahkan bot\n\n"
                                    "Bot tidak dapat bergabung otomatis ke public chat.",
                                    parse_mode='Markdown'
                                )
                                log_join_attempt(user_id, username, invite_link, False, "Public chat requires manual addition")
                                return
                    except:
                        # Error checking membership, try to join anyway
                        try:
                            await context.bot.join_chat(f"@{username_extracted}")
                            join_successful = True
                            logger.info(f"Successfully joined chat: {chat.title} ({chat.id})")
                        except:
                            await processing_msg.edit_text(
                                f"❌ **Gagal bergabung ke chat!**\n\n"
                                f"**Chat**: {chat.title}\n"
                                f"**Username**: @{username_extracted}\n\n"
                                "Bot tidak dapat bergabung otomatis.\n"
                                "Tambahkan bot secara manual ke chat tersebut.",
                                parse_mode='Markdown'
                            )
                            log_join_attempt(user_id, username, invite_link, False, "Cannot join public chat")
                            return
                except:
                    await processing_msg.edit_text(
                        f"❌ **Chat tidak ditemukan!**\n\n"
                        f"Username: @{username_extracted}\n\n"
                        "Kemungkinan penyebab:\n"
                        "• Username salah atau tidak ada\n"
                        "• Chat bersifat private\n"
                        "• Chat telah dihapus\n\n"
                        "Periksa kembali link yang Anda berikan.",
                        parse_mode='Markdown'
                    )
                    log_join_attempt(user_id, username, invite_link, False, "Chat not found")
                    return
        
        except Exception as e:
            logger.error(f"Unexpected error during join attempt: {e}")
            await processing_msg.edit_text(
                f"💥 **Error tidak terduga!**\n\n"
                f"Error: {str(e)}\n\n"
                "Coba lagi dalam beberapa menit.\n"
                "Jika masalah berlanjut, hubungi admin bot.",
                parse_mode='Markdown'
            )
            log_join_attempt(user_id, username, invite_link, False, str(e))
            return
        
        # If we successfully joined or confirmed membership
        if join_successful and chat:
            # Store the chat information if not already stored
            if not chat_storage.is_chat_stored(chat.id):
                chat_storage.add_chat(
                    chat_id=chat.id,
                    chat_title=chat.title or f"Chat {chat.id}",
                    chat_type=chat.type,
                    invite_link=invite_link
                )
            
            success_message = (
                "✅ **Berhasil bergabung ke chat!**\n\n"
                f"**Nama**: {chat.title}\n"
                f"**Type**: {chat.type.title()}\n"
                f"**ID**: `{chat.id}`\n\n"
                "✅ **Chat disimpan untuk broadcast!**\n"
                f"Total chat tersimpan: {chat_storage.get_chat_count()}"
            )
            
            await processing_msg.edit_text(success_message, parse_mode='Markdown')
            log_join_attempt(user_id, username, invite_link, True, "Successfully joined")
            return
        
        # If we reach here, something went wrong
        await processing_msg.edit_text(
            "❌ **Gagal bergabung ke chat!**\n\n"
            "Kemungkinan penyebab:\n"
            "• Link invite tidak valid\n"
            "• Chat tidak mengizinkan bot bergabung\n"
            "• Bot diblokir oleh admin\n\n"
            "Coba dengan link invite yang berbeda atau hubungi admin chat.",
            parse_mode='Markdown'
        )
        log_join_attempt(user_id, username, invite_link, False, "Unknown join failure")
        
    except Exception as e:
        logger.error(f"Critical error in join command: {e}")
        await processing_msg.edit_text(
            f"💥 **Error sistem!**\n\n"
            f"Error: {str(e)}\n\n"
            "Sistem mengalami masalah. Coba lagi nanti.",
            parse_mode='Markdown'
        )
        log_join_attempt(user_id, username, invite_link, False, f"System error: {str(e)}")

async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle /bc command to broadcast messages to all joined groups/channels
    
    Args:
        update: Telegram update object
        context: Bot context
    """
    user = update.effective_user
    user_id = user.id
    username = user.username or user.first_name
    
    logger.info(f"User {username}({user_id}) requested broadcast command")
    
    # Check if user is authorized
    if not auth_system.is_authorized(user_id):
        await update.message.reply_text(auth_system.get_unauthorized_message())
        return
    
    # Get the broadcast message
    message_text = update.message.text
    if len(message_text.split()) < 2:
        await update.message.reply_text(
            "❌ **Pesan broadcast tidak diberikan!**\n\n"
            "Gunakan format: `/bc [pesan]`\n"
            "Contoh: `/bc Halo semua! Ini adalah pesan broadcast.`",
            parse_mode='Markdown'
        )
        return
    
    # Extract the broadcast message
    broadcast_message = " ".join(message_text.split()[1:])
    
    # Get all stored chats
    chats = chat_storage.get_all_chats()
    
    if not chats:
        await update.message.reply_text(
            "❌ **Tidak ada chat untuk broadcast!**\n\n"
            "Gunakan `/join [link]` untuk bergabung ke grup/channel terlebih dahulu.",
            parse_mode='Markdown'
        )
        return
    
    # Send progress message
    progress_msg = await update.message.reply_text(
        f"📡 **Memulai broadcast...**\n\n"
        f"Mengirim pesan ke {len(chats)} chat...",
        parse_mode='Markdown'
    )
    
    success_count = 0
    failed_count = 0
    failed_chats = []
    
    for chat_info in chats:
        try:
            await context.bot.send_message(
                chat_id=chat_info['chat_id'],
                text=broadcast_message,
                parse_mode='Markdown'
            )
            success_count += 1
            chat_storage.update_last_broadcast(chat_info['chat_id'])
            logger.info(f"Broadcast sent to {chat_info['title']} ({chat_info['chat_id']})")
        except Exception as e:
            failed_count += 1
            failed_chats.append({
                'title': chat_info['title'],
                'error': str(e)
            })
            logger.warning(f"Failed to send broadcast to {chat_info['title']} ({chat_info['chat_id']}): {e}")
    
    # Send final report
    report_text = f"📊 **Laporan Broadcast**\n\n"
    report_text += f"✅ **Berhasil**: {success_count} chat\n"
    report_text += f"❌ **Gagal**: {failed_count} chat\n"
    report_text += f"📈 **Total**: {len(chats)} chat\n\n"
    
    if failed_chats:
        report_text += "**Chat yang gagal:**\n"
        for failed_chat in failed_chats[:5]:  # Show max 5 failed chats
            report_text += f"• {failed_chat['title']}\n"
        if len(failed_chats) > 5:
            report_text += f"• ... dan {len(failed_chats) - 5} lainnya\n"
    
    await progress_msg.edit_text(report_text, parse_mode='Markdown')
    log_broadcast_attempt(user_id, username, broadcast_message, success_count, failed_count)

async def list_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle /list command to show all joined groups/channels
    
    Args:
        update: Telegram update object
        context: Bot context
    """
    user = update.effective_user
    user_id = user.id
    username = user.username or user.first_name
    
    logger.info(f"User {username}({user_id}) requested list command")
    
    # Check if user is authorized
    if not auth_system.is_authorized(user_id):
        await update.message.reply_text(auth_system.get_unauthorized_message())
        return
    
    # Get all stored chats
    chats = chat_storage.get_all_chats()
    
    if not chats:
        await update.message.reply_text(
            "📋 **Daftar Chat Kosong**\n\n"
            "Bot belum bergabung ke chat manapun.\n"
            "Gunakan `/join [link]` untuk bergabung ke grup/channel.",
            parse_mode='Markdown'
        )
        return
    
    # Create the chat list
    list_text = f"📋 **Daftar Chat Bot** ({len(chats)} chat)\n\n"
    
    for i, chat_info in enumerate(chats, 1):
        chat_type = chat_info['type'].title()
        title = chat_info['title']
        chat_id = chat_info['chat_id']
        
        list_text += f"**{i}. {title}**\n"
        list_text += f"   Type: {chat_type}\n"
        list_text += f"   ID: `{chat_id}`\n"
        
        if chat_info.get('last_broadcast'):
            list_text += f"   Last BC: {chat_info['last_broadcast'][:10]}\n"
        
        list_text += "\n"
        
        # Split message if too long
        if len(list_text) > 3500:
            await update.message.reply_text(list_text, parse_mode='Markdown')
            list_text = f"📋 **Daftar Chat Bot (lanjutan)**\n\n"
    
    if list_text.strip():
        await update.message.reply_text(list_text, parse_mode='Markdown')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle non-command messages for authentication
    
    Args:
        update: Telegram update object
        context: Bot context
    """
    user = update.effective_user
    user_id = user.id
    message_text = update.message.text
    
    # Check if user is already authorized
    if auth_system.is_authorized(user_id):
        await update.message.reply_text(
            "✅ **Anda sudah memiliki akses!**\n\n"
            "Gunakan `/help` untuk melihat semua perintah yang tersedia.",
            parse_mode='Markdown'
        )
        return
    
    # Try to verify the access code
    if auth_system.verify_code(user_id, message_text):
        await update.message.reply_text(auth_system.get_access_granted_message())
        logger.info(f"User {user.username}({user_id}) authenticated successfully")
    else:
        await update.message.reply_text(auth_system.get_invalid_code_message())
        logger.warning(f"User {user.username}({user_id}) failed authentication with code: {message_text}")
