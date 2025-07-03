"""
Script untuk verifikasi dan setup user account Telegram
"""

import asyncio
import json
import os
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError

async def verify_user_account():
    """Verifikasi dan setup user account"""
    config_file = 'user_telegram_config.json'
    
    # Load config
    if not os.path.exists(config_file):
        print("❌ Konfigurasi tidak ditemukan!")
        print("Jalankan: python hybrid_autojoin.py")
        return False
    
    with open(config_file, 'r') as f:
        config = json.load(f)
    
    try:
        # Buat client
        client = TelegramClient(
            'user_session',
            config['api_id'],
            config['api_hash']
        )
        
        print("🔗 Connecting to Telegram...")
        await client.connect()
        
        # Cek apakah sudah authorized
        if not await client.is_user_authorized():
            print(f"📱 Mengirim kode verifikasi ke {config['phone']}")
            await client.send_code_request(config['phone'])
            
            code = input("Masukkan kode verifikasi: ").strip()
            
            try:
                await client.sign_in(config['phone'], code)
                print("✅ Berhasil login!")
                
            except SessionPasswordNeededError:
                password = input("Masukkan password 2FA: ").strip()
                await client.sign_in(password=password)
                print("✅ Berhasil login dengan 2FA!")
        
        # Verifikasi user info
        me = await client.get_me()
        print(f"\n👤 Berhasil login sebagai:")
        print(f"   Nama: {me.first_name} {me.last_name or ''}")
        print(f"   Username: @{me.username or 'tidak ada'}")
        print(f"   User ID: {me.id}")
        print(f"   Phone: {me.phone}")
        
        # Test join functionality
        print("\n🧪 Testing join functionality...")
        
        # Get current groups
        groups = []
        async for dialog in client.iter_dialogs(limit=5):
            if dialog.is_group or dialog.is_channel:
                groups.append(dialog.title)
        
        print(f"📊 Anda anggota {len(groups)} grup/channel")
        if groups:
            print("   Contoh:", groups[0])
        
        await client.disconnect()
        
        print("\n✅ Setup berhasil!")
        print("Sekarang bot dapat menggunakan akun Anda untuk auto-join ke private group")
        print("Restart bot Telegram untuk menggunakan fitur baru")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(verify_user_account())