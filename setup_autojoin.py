"""
Script setup untuk fitur auto-join sesungguhnya
"""

import json
import os
import asyncio
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError

def setup_user_credentials():
    """Setup kredensial user account"""
    print("🔧 SETUP AUTO-JOIN UNTUK PRIVATE GROUP")
    print("=" * 50)
    print("Bot biasa tidak bisa auto-join ke private group.")
    print("Untuk mengatasi ini, diperlukan akun user Telegram Anda.")
    print("\n📋 Yang diperlukan:")
    print("1. API ID dan API Hash dari https://my.telegram.org")
    print("2. Nomor telepon Anda")
    print("3. Kode verifikasi dari Telegram")
    print("\n🔗 Cara mendapatkan API ID dan API Hash:")
    print("1. Buka https://my.telegram.org")
    print("2. Login dengan nomor telepon")
    print("3. Klik 'API Development Tools'")
    print("4. Buat aplikasi baru dengan nama apapun")
    print("5. Salin API ID dan API Hash")
    print("=" * 50)
    
    # Input dari user
    try:
        api_id = input("\nMasukkan API ID: ").strip()
        api_hash = input("Masukkan API Hash: ").strip()
        phone = input("Masukkan nomor telepon (contoh: +6281234567890): ").strip()
        
        if not api_id or not api_hash or not phone:
            print("❌ Semua field harus diisi!")
            return False
        
        # Validasi API ID (harus angka)
        try:
            api_id = int(api_id)
        except ValueError:
            print("❌ API ID harus berupa angka!")
            return False
        
        # Validasi nomor telepon
        if not phone.startswith('+'):
            print("❌ Nomor telepon harus dimulai dengan + (contoh: +6281234567890)")
            return False
        
        config = {
            'api_id': api_id,
            'api_hash': api_hash,
            'phone': phone
        }
        
        return config
        
    except KeyboardInterrupt:
        print("\n❌ Setup dibatalkan!")
        return None

async def verify_and_login(config):
    """Verifikasi dan login ke Telegram"""
    try:
        print("\n🔗 Menghubungkan ke Telegram...")
        
        # Buat client
        client = TelegramClient(
            'user_session',
            config['api_id'],
            config['api_hash']
        )
        
        await client.connect()
        
        # Cek apakah sudah login
        if not await client.is_user_authorized():
            print(f"📱 Mengirim kode verifikasi ke {config['phone']}")
            await client.send_code_request(config['phone'])
            
            # Minta kode verifikasi
            code = input("Masukkan kode verifikasi: ").strip()
            
            try:
                await client.sign_in(config['phone'], code)
                print("✅ Berhasil login!")
                
            except SessionPasswordNeededError:
                password = input("Masukkan password 2FA: ").strip()
                await client.sign_in(password=password)
                print("✅ Berhasil login dengan 2FA!")
        
        # Verifikasi informasi user
        me = await client.get_me()
        print(f"\n👤 Login berhasil sebagai:")
        print(f"   Nama: {me.first_name} {me.last_name or ''}")
        print(f"   Username: @{me.username or 'tidak ada'}")
        print(f"   Phone: {me.phone}")
        
        await client.disconnect()
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def save_config(config):
    """Simpan konfigurasi"""
    with open('user_telegram_config.json', 'w') as f:
        json.dump(config, f, indent=2)

async def main():
    """Main function"""
    print("🚀 SETUP AUTO-JOIN TELEGRAM BOT")
    print("=" * 50)
    
    # Cek apakah sudah ada konfigurasi
    if os.path.exists('user_telegram_config.json'):
        print("⚠️ Konfigurasi sudah ada!")
        choice = input("Apakah ingin setup ulang? (y/n): ").strip().lower()
        if choice != 'y':
            print("Setup dibatalkan.")
            return
    
    # Setup kredensial
    config = setup_user_credentials()
    if not config:
        return
    
    # Verifikasi dan login
    if await verify_and_login(config):
        save_config(config)
        print("\n🎉 SETUP BERHASIL!")
        print("=" * 50)
        print("✅ User account telah dikonfigurasi")
        print("✅ Session telah dibuat")
        print("✅ Bot sekarang dapat auto-join ke private group")
        print("\n📝 Langkah selanjutnya:")
        print("1. Restart bot Telegram")
        print("2. Coba command /join dengan link private group")
        print("3. Bot akan otomatis bergabung menggunakan akun Anda")
        print("=" * 50)
    else:
        print("\n❌ Setup gagal!")
        print("Coba lagi atau periksa kredensial Anda.")

if __name__ == "__main__":
    asyncio.run(main())