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
    
    # Nilai default dari input Anda
    default_config = {
        'api_id': 15885787,
        'api_hash': '78e30841cd2bcbdd0c894b0da5b787dd',
        'phone': '+6285945213322'
    }
    
    # Mode interaktif dengan nilai default
    use_default = input("Gunakan konfigurasi default? (y/n): ").strip().lower()
    
    if use_default == 'y':
        config = default_config
        print("\n⚠ Menggunakan konfigurasi default:")
        print(f"API ID: {config['api_id']}")
        print(f"API Hash: {config['api_hash'][:4]}... (disembunyikan)")
        print(f"Nomor Telepon: {config['phone']}")
    else:
        config = {
            'api_id': int(input("\nMasukkan API ID (default: 15885787): ") or default_config['api_id']),
            'api_hash': input("Masukkan API Hash (default: 78e308...): ") or default_config['api_hash'],
            'phone': input("Masukkan nomor telepon (default: +6285945213322): ") or default_config['phone']
        }
    
    if not config['api_id'] or not config['api_hash'] or not config['phone']:
        print("❌ Semua field harus diisi!")
        return False
    
    hybrid_autojoin.save_user_config(config)
    hybrid_autojoin.config = config
    print("✅ Konfigurasi disimpan!")
    print("\nSekarang jalankan script untuk verifikasi:")
    print("python verify_user_account.py")
    return True
