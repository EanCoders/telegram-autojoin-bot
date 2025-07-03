"""
Telegram User Account Auto-Join Script
Solusi untuk bergabung ke private group secara otomatis menggunakan user account
"""

import asyncio
import time
import logging
import json
import os
from typing import List, Dict, Optional
from telethon import TelegramClient
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.functions.messages import ImportChatInviteRequest
from telethon.errors import SessionPasswordNeededError, PhoneCodeInvalidError
from telethon.errors import FloodWaitError, UserAlreadyParticipantError
from telethon.errors import InviteHashExpiredError, InviteHashInvalidError
import re

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/user_autojoin.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class UserAutoJoin:
    """
    Kelas untuk auto-join menggunakan user account (bukan bot)
    """
    
    def __init__(self):
        self.client = None
        self.session_file = 'user_session'
        self.config_file = 'user_config.json'
        self.joined_groups_file = 'joined_groups.json'
        self.config = self.load_config()
        
    def load_config(self) -> Dict:
        """Load konfigurasi user"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {}
    
    def save_config(self, config: Dict):
        """Simpan konfigurasi user"""
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
    
    def load_joined_groups(self) -> List[Dict]:
        """Load daftar group yang sudah diikuti"""
        if os.path.exists(self.joined_groups_file):
            try:
                with open(self.joined_groups_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return []
    
    def save_joined_groups(self, groups: List[Dict]):
        """Simpan daftar group yang sudah diikuti"""
        with open(self.joined_groups_file, 'w') as f:
            json.dump(groups, f, indent=2)
    
    def extract_invite_hash(self, invite_link: str) -> Optional[str]:
        """Ekstrak hash dari invite link"""
        # Pattern untuk berbagai format invite link
        patterns = [
            r'https://t\.me/\+([A-Za-z0-9_-]+)',
            r'https://t\.me/joinchat/([A-Za-z0-9_-]+)',
            r'https://telegram\.me/joinchat/([A-Za-z0-9_-]+)',
            r't\.me/\+([A-Za-z0-9_-]+)',
            r'joinchat/([A-Za-z0-9_-]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, invite_link)
            if match:
                return match.group(1)
        return None
    
    async def setup_client(self) -> bool:
        """Setup Telegram client dengan kredensial user"""
        try:
            # Cek apakah sudah ada konfigurasi
            if not self.config.get('api_id') or not self.config.get('api_hash'):
                print("\n🔧 SETUP AKUN TELEGRAM USER")
                print("=" * 50)
                print("Untuk menggunakan fitur auto-join, Anda perlu:")
                print("1. API ID dan API Hash dari https://my.telegram.org")
                print("2. Nomor telepon Anda")
                print("3. Kode verifikasi yang dikirim ke Telegram")
                print("\n📋 Cara mendapatkan API ID dan API Hash:")
                print("1. Buka https://my.telegram.org")
                print("2. Login dengan nomor telepon Anda")
                print("3. Klik 'API Development Tools'")
                print("4. Buat aplikasi baru")
                print("5. Salin API ID dan API Hash")
                print("=" * 50)
                
                api_id = input("\nMasukkan API ID: ").strip()
                api_hash = input("Masukkan API Hash: ").strip()
                phone = input("Masukkan nomor telepon (dengan kode negara, contoh: +6281234567890): ").strip()
                
                if not api_id or not api_hash or not phone:
                    print("❌ Semua field harus diisi!")
                    return False
                
                self.config = {
                    'api_id': int(api_id),
                    'api_hash': api_hash,
                    'phone': phone
                }
                self.save_config(self.config)
            
            # Buat client
            self.client = TelegramClient(
                self.session_file,
                self.config['api_id'],
                self.config['api_hash']
            )
            
            # Connect dan login
            await self.client.connect()
            
            if not await self.client.is_user_authorized():
                print(f"\n📱 Mengirim kode verifikasi ke {self.config['phone']}")
                await self.client.send_code_request(self.config['phone'])
                
                code = input("Masukkan kode verifikasi: ").strip()
                try:
                    await self.client.sign_in(self.config['phone'], code)
                except SessionPasswordNeededError:
                    password = input("Masukkan password 2FA: ").strip()
                    await self.client.sign_in(password=password)
                
                print("✅ Login berhasil!")
            
            # Verifikasi user info
            me = await self.client.get_me()
            print(f"\n👤 Logged in sebagai: {me.first_name} {me.last_name or ''}")
            print(f"📱 Username: @{me.username or 'tidak ada'}")
            print(f"🆔 User ID: {me.id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error setup client: {e}")
            print(f"❌ Error setup: {e}")
            return False
    
    async def join_group(self, invite_link: str) -> Dict:
        """Join ke group menggunakan invite link"""
        result = {
            'success': False,
            'link': invite_link,
            'error': None,
            'group_info': None
        }
        
        try:
            # Ekstrak hash dari invite link
            invite_hash = self.extract_invite_hash(invite_link)
            if not invite_hash:
                result['error'] = "Format invite link tidak valid"
                return result
            
            logger.info(f"Attempting to join group with hash: {invite_hash}")
            
            # Join menggunakan ImportChatInviteRequest
            try:
                updates = await self.client(ImportChatInviteRequest(invite_hash))
                
                # Ambil info group dari hasil
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
                        'joined_at': int(time.time())
                    }
                    
                    logger.info(f"Successfully joined: {chat.title} (ID: {chat.id})")
                    print(f"✅ Berhasil bergabung ke: {chat.title}")
                else:
                    result['success'] = True
                    result['group_info'] = {
                        'id': 'unknown',
                        'title': 'Unknown Group',
                        'type': 'group',
                        'participants_count': 0,
                        'joined_at': int(time.time())
                    }
                    logger.info(f"Joined group but couldn't get info")
                    print(f"✅ Berhasil bergabung ke group")
                    
            except UserAlreadyParticipantError:
                result['error'] = "Sudah menjadi anggota group"
                logger.info(f"Already a member of group: {invite_link}")
                print(f"ℹ️ Sudah menjadi anggota group")
                
            except InviteHashExpiredError:
                result['error'] = "Link invite sudah kedaluwarsa"
                logger.warning(f"Invite link expired: {invite_link}")
                print(f"❌ Link invite sudah kedaluwarsa")
                
            except InviteHashInvalidError:
                result['error'] = "Link invite tidak valid"
                logger.warning(f"Invalid invite link: {invite_link}")
                print(f"❌ Link invite tidak valid")
                
            except FloodWaitError as e:
                result['error'] = f"Rate limit, tunggu {e.seconds} detik"
                logger.warning(f"Rate limited for {e.seconds} seconds")
                print(f"⏳ Rate limit! Tunggu {e.seconds} detik")
                
        except Exception as e:
            result['error'] = str(e)
            logger.error(f"Error joining group {invite_link}: {e}")
            print(f"❌ Error: {e}")
        
        return result
    
    async def join_multiple_groups(self, invite_links: List[str], delay: int = 30) -> List[Dict]:
        """Join ke multiple groups dengan delay"""
        results = []
        joined_groups = self.load_joined_groups()
        
        print(f"\n🚀 Memulai auto-join ke {len(invite_links)} group")
        print(f"⏱️ Delay antar join: {delay} detik")
        print("=" * 50)
        
        for i, link in enumerate(invite_links, 1):
            print(f"\n[{i}/{len(invite_links)}] Processing: {link}")
            
            # Join group
            result = await self.join_group(link)
            results.append(result)
            
            # Simpan jika berhasil
            if result['success'] and result['group_info']:
                # Cek apakah sudah ada di daftar
                existing = next((g for g in joined_groups if g.get('link') == link), None)
                if not existing:
                    group_data = result['group_info'].copy()
                    group_data['link'] = link
                    joined_groups.append(group_data)
                    self.save_joined_groups(joined_groups)
            
            # Delay sebelum join berikutnya
            if i < len(invite_links):
                print(f"⏳ Waiting {delay} seconds before next join...")
                await asyncio.sleep(delay)
        
        return results
    
    async def get_my_groups(self) -> List[Dict]:
        """Dapatkan daftar group yang sudah diikuti"""
        try:
            groups = []
            async for dialog in self.client.iter_dialogs():
                if dialog.is_group or dialog.is_channel:
                    groups.append({
                        'id': dialog.id,
                        'title': dialog.title,
                        'type': 'channel' if dialog.is_channel else 'group',
                        'username': getattr(dialog.entity, 'username', None),
                        'participants_count': getattr(dialog.entity, 'participants_count', 0)
                    })
            return groups
        except Exception as e:
            logger.error(f"Error getting groups: {e}")
            return []
    
    async def close(self):
        """Tutup client"""
        if self.client:
            await self.client.disconnect()

async def main():
    """Main function untuk testing"""
    print("🤖 TELEGRAM USER AUTO-JOIN SCRIPT")
    print("=" * 50)
    
    auto_join = UserAutoJoin()
    
    try:
        # Setup client
        if not await auto_join.setup_client():
            print("❌ Setup failed!")
            return
        
        while True:
            print("\n📋 PILIHAN MENU:")
            print("1. Join single group")
            print("2. Join multiple groups")
            print("3. Lihat groups yang sudah diikuti")
            print("4. Keluar")
            
            choice = input("\nPilih menu (1-4): ").strip()
            
            if choice == '1':
                link = input("Masukkan invite link: ").strip()
                if link:
                    result = await auto_join.join_group(link)
                    if result['success']:
                        print(f"✅ Berhasil join!")
                    else:
                        print(f"❌ Gagal: {result['error']}")
            
            elif choice == '2':
                print("\nMasukkan invite links (satu per baris, ketik 'done' untuk selesai):")
                links = []
                while True:
                    link = input("Link: ").strip()
                    if link.lower() == 'done':
                        break
                    if link:
                        links.append(link)
                
                if links:
                    delay = int(input("Delay antar join (detik, default 30): ") or "30")
                    results = await auto_join.join_multiple_groups(links, delay)
                    
                    success_count = sum(1 for r in results if r['success'])
                    print(f"\n📊 Hasil: {success_count}/{len(results)} berhasil")
            
            elif choice == '3':
                groups = await auto_join.get_my_groups()
                if groups:
                    print(f"\n👥 Anda anggota {len(groups)} grup/channel:")
                    for i, group in enumerate(groups, 1):
                        print(f"{i}. {group['title']} ({group['type']})")
                else:
                    print("❌ Tidak ada grup yang diikuti")
            
            elif choice == '4':
                break
            
            else:
                print("❌ Pilihan tidak valid!")
    
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    
    except Exception as e:
        logger.error(f"Error in main: {e}")
        print(f"❌ Error: {e}")
    
    finally:
        await auto_join.close()

if __name__ == "__main__":
    asyncio.run(main())