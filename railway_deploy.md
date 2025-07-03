# Deploy Bot Telegram ke Railway.app

## Setup Railway.app untuk Bot Telegram

Railway.app adalah platform hosting yang mudah dan gratis untuk deploy bot Telegram dengan fitur always-online.

## Langkah-langkah Deploy:

### 1. Persiapan GitHub Repository

Pertama, upload code bot ke GitHub:

1. Buat akun GitHub di https://github.com
2. Buat repository baru dengan nama "telegram-autojoin-bot"
3. Upload semua file bot ke repository

### 2. Setup Railway.app

1. Buka https://railway.app
2. Klik "Start a New Project"
3. Login dengan GitHub
4. Pilih "Deploy from GitHub repo"
5. Pilih repository "telegram-autojoin-bot"

### 3. Konfigurasi Environment Variables

Di Railway dashboard, tambahkan environment variables:

```
BOT_TOKEN=your_telegram_bot_token_here
PYTHONUNBUFFERED=1
```

### 4. Deploy Otomatis

Railway akan otomatis:
- Detect Python project
- Install dependencies dari requirements.txt
- Deploy aplikasi
- Memberikan URL untuk monitoring

## Konfigurasi File untuk Railway:

### Procfile (sudah disediakan)
```
web: python main.py
```

### railway.json (konfigurasi deploy)
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "python main.py",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

## Keuntungan Railway:

- ✅ **Gratis** untuk usage normal
- ✅ **Always Online** - bot berjalan 24/7
- ✅ **Auto Deploy** - otomatis deploy saat update code
- ✅ **Logs Real-time** - monitor bot langsung
- ✅ **Auto Restart** - restart otomatis jika crash
- ✅ **Custom Domain** - bisa gunakan domain sendiri

## Setup Auto-Join di Railway:

Setelah deploy, untuk setup auto-join:

1. Akses Railway logs/console
2. Buat file konfigurasi user account di dashboard
3. Set environment variables untuk API credentials
4. Restart service

## Monitoring dan Maintenance:

- **Logs**: Lihat aktivitas bot real-time
- **Metrics**: Monitor CPU dan memory usage
- **Restarts**: Auto restart jika bot crash
- **Updates**: Push ke GitHub untuk update otomatis

## Alternative: Render.com

Jika Railway tidak cocok, gunakan Render.com:

1. Buka https://render.com
2. Connect GitHub repository
3. Pilih "Web Service"
4. Set start command: `python main.py`
5. Tambahkan environment variables

## Troubleshooting:

**Bot tidak respond:**
- Cek logs di Railway dashboard
- Pastikan BOT_TOKEN benar
- Cek environment variables

**Deploy failed:**
- Pastikan requirements.txt ada
- Cek syntax error di code
- Lihat build logs untuk error detail

Railway.app adalah pilihan terbaik karena mudah setup, gratis, dan reliable untuk bot Telegram.