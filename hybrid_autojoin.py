"""
Hybrid Auto-Join System: Menggabungkan Bot dan User Account
Solusi untuk auto-join yang sesungguhnya bekerja
"""

import asyncio
import logging
import json
import os
from typing import List, Dict, Optional
from telethon import TelegramClient
from telethon.tl.functions.messages import ImportChatInviteRequest
from telethon.errors import UserAlreadyParticipantError, FloodWaitError
from telethon.errors import InviteHashExpiredError, InviteHashInvalidError
from utils import extract_invite_hash, validate_telegram_invite_link
from chat_storage import chat_storage
import re

logger = logging.getLogger(__name__)

class HybridAutoJoin:
    """
    Sistem hybrid yang menggunakan user account untuk auto-join
    dan bot untuk management
    """
    
    def __init__(self):
        self.user_client = None
        self.config = self.load_user_config()
        self.session_file = 'user_session'
        
    def load_user_config(self) -> Dict:
        """Load konfigurasi user account"""
        config_file = 'user_telegram_config.json'
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {}
    
    def save_user_config(self, config: Dict):
        """Simpan konfigurasi user account"""
        config_file = 'user_telegram_config.json'
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
    
    def is_user_configured(self) -> bool:
        """Cek apakah user account sudah dikonfigurasi"""
        return (self.config.get('api_id') and 
                self.config.get('api_hash') and 
                self.config.get('phone'))
    
    async def setup_user_account(self) -> bool:
        """Setup user account untuk auto-join"""
        try:
            if not self.is_user_configured():
                return False
                
            # Buat client
            self.user_client = TelegramClient(
                self.session_file,
                self.config['api_id'],
                self.config['api_hash']
            )
            
            await self.user_client.connect()
            
            # Cek apakah sudah authorized
            if not await self.user_client.is_user_authorized():
                logger.error("User account not authorized")
                return False
            
            # Verifikasi user info
            me = await self.user_client.get_me()
            logger.info(f"User account ready: {me.first_name} (@{me.username})")
            return True
            
        except Exception as e:
            logger.error(f"Error setting up user account: {e}")
            return False
    
    async def join_group_with_user(self, invite_link: str) -> Dict:
        """Join group menggunakan user account"""
        result = {
            'success': False,
            'link': invite_link,
            'error': None,
            'group_info': None
        }
        
        try:
            # Ekstrak hash dari invite link
            invite_hash = extract_invite_hash(invite_link)
            if not invite_hash:
                result['error'] = "Format invite link tidak valid"
                return result
            
            logger.info(f"User account attempting to join: {invite_hash}")
            
            # Join menggunakan user account
            try:
                updates = await self.user_client(ImportChatInviteRequest(invite_hash))
                
                # Ambil info group
                chat = None
                if hasattr(updates, 'chats') and updates.chats:
                    chat = updates.chats[0]
                
                if chat:
                    result['success'] = True
                    result['group_info'] = {
                        'id': chat.id,
                        'title': chat.title,
                        'type': 'supergroup' if hasattr(chat, 'megagroup') else 'group',
                        'participants_count': getattr(chat, 'participants_count', 0),
                        'username': getattr(chat, 'username', None)
                    }
                    
                    # Simpan ke chat storage
                    if not chat_storage.is_chat_stored(chat.id):
                        chat_storage.add_chat(
                            chat_id=chat.id,
                            chat_title=chat.title,
                            chat_type=result['group_info']['type'],
                            invite_link=invite_link
                        )
                    
                    logger.info(f"Successfully joined: {chat.title} (ID: {chat.id})")
                    
            except UserAlreadyParticipantError:
                result['error'] = "Sudah menjadi anggota group"
                logger.info(f"Already a member: {invite_link}")
                
            except InviteHashExpiredError:
                result['error'] = "Link invite sudah kedaluwarsa"
                logger.warning(f"Invite expired: {invite_link}")
                
            except InviteHashInvalidError:
                result['error'] = "Link invite tidak valid"
                logger.warning(f"Invalid invite: {invite_link}")
                
            except FloodWaitError as e:
                result['error'] = f"Rate limit, tunggu {e.seconds} detik"
                logger.warning(f"Rate limited for {e.seconds} seconds")
                
        except Exception as e:
            result['error'] = str(e)
            logger.error(f"Error joining group: {e}")
        
        return result
    
    async def close(self):
        """Tutup user client"""
        if self.user_client:
            await self.user_client.disconnect()

# Global instance
hybrid_autojoin = HybridAutoJoin()

async def setup_hybrid_system():
    """Setup sistem hybrid"""
    return await hybrid_autojoin.setup_user_account()

async def join_with_user_account(invite_link: str) -> Dict:
    """Join group menggunakan user account"""
    return await hybrid_autojoin.join_group_with_user(invite_link)

# Fungsi untuk setup initial
def setup_user_credentials():
    """Setup kredensial user account"""
    print("\n🔧 SETUP USER ACCOUNT UNTUK AUTO-JOIN")
    print("=" * 50)
    print("Untuk fitur auto-join ke private group, diperlukan:")
    print("1. API ID dan API Hash dari https://my.telegram.org")
    print("2. Nomor telepon Anda")
    print("3. Verifikasi melalui Telegram")
    print("\n📋 Cara mendapatkan API ID dan API Hash:")
    print("1. Buka https://my.telegram.org")
    print("2. Login dengan nomor telepon Anda")
    print("3. Klik 'API Development Tools'")
    print("4. Buat aplikasi baru")
    print("5. Salin API ID dan API Hash")
    print("=" * 50)
    
    api_id = input("\n15885787: ").strip()
    api_hash = input("78e30841cd2bcbdd0c894b0da5b787dd: ").strip()
    phone = input("+6285945213322: ").strip()
    
    if not api_id or not api_hash or not phone:
        print("❌ Semua field harus diisi!")
        return False
    
    config = {
        'api_id': int(api_id),
        'api_hash': api_hash,
        'phone': phone
    }
    
    hybrid_autojoin.save_user_config(config)
    hybrid_autojoin.config = config
    print("✅ Konfigurasi disimpan!")
    print("\nSekarang jalankan script untuk verifikasi:")
    print("python verify_user_account.py")
    return True

if __name__ == "__main__":
    setup_user_credentials()
