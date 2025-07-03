# Telegram Auto-Join Bot - Complete Package

## Isi Package:

### Core Bot Files:
- main.py - Entry point bot
- bot_handlers.py - Command handlers
- auth_system.py - Sistem autentikasi  
- chat_storage.py - Penyimpanan chat
- config.py - Konfigurasi bot
- utils.py - Utility functions

### Auto-Join System:
- hybrid_autojoin.py - Sistem hybrid untuk auto-join
- user_autojoin.py - User account automation
- setup_autojoin.py - Setup script untuk user account
- verify_user_account.py - Verifikasi user account

### Dokumentasi:
- replit.md - Dokumentasi lengkap proyek
- AUTOJOIN_SETUP.md - Panduan setup auto-join

### Cara Menjalankan:

1. Install dependencies:
   ```
   pip install python-telegram-bot==22.2 telethon cryptg
   ```

2. Setup bot token:
   - Dapatkan bot token dari @BotFather
   - Set environment variable: BOT_TOKEN=your_token

3. Untuk auto-join private group:
   ```
   python setup_autojoin.py
   ```

4. Jalankan bot:
   ```
   python main.py
   ```

### Fitur:
- ✅ Auto-join private group (dengan user account)
- ✅ Auto-join public channel
- ✅ Broadcast ke semua grup
- ✅ Sistem autentikasi (kode: 0722)
- ✅ Logging lengkap
- ✅ Error handling komprehensif

### Support:
Baca AUTOJOIN_SETUP.md untuk panduan lengkap.
