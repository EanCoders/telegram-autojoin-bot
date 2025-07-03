# 🚀 Setup Auto-Join untuk Private Group

## Masalah yang Diselesaikan

Bot Telegram biasa **tidak bisa** bergabung otomatis ke private group. Ini adalah keterbatasan API Telegram untuk bot. 

**Solusi**: Menggunakan **user account** Anda untuk auto-join, lalu bot mengelola grup yang sudah diikuti.

## Cara Setup (5 Menit)

### 1. Dapatkan API Credentials

1. Buka **https://my.telegram.org**
2. Login dengan nomor telepon Anda
3. Klik **"API Development Tools"**
4. Buat aplikasi baru:
   - App title: `Bot Auto Join`
   - Short name: `autojoin`
   - URL: kosongkan
5. **Salin API ID dan API Hash**

### 2. Jalankan Setup

```bash
python setup_autojoin.py
```

Masukkan:
- API ID (angka)
- API Hash (huruf dan angka)
- Nomor telepon (dengan +, contoh: +6281234567890)
- Kode verifikasi dari Telegram

### 3. Restart Bot

```bash
# Restart bot Telegram
python main.py
```

## Cara Menggunakan

### Auto-Join ke Private Group

```
/join https://t.me/+abc123def456
```

Bot akan:
1. Menggunakan akun Anda untuk bergabung
2. Menyimpan grup untuk broadcast
3. Memberikan konfirmasi berhasil

### Auto-Join ke Public Channel

```
/join https://t.me/namagroup
```

Bot akan:
1. Mengecek apakah sudah menjadi anggota
2. Menyimpan jika sudah bergabung
3. Memberikan instruksi jika belum

## Fitur Lengkap

- ✅ **Auto-join private group** (menggunakan user account)
- ✅ **Auto-join public channel** (deteksi otomatis)
- ✅ **Broadcast ke semua grup** (`/bc pesan`)
- ✅ **List semua grup** (`/list`)
- ✅ **Sistem autentikasi** (kode akses: `0722`)
- ✅ **Logging lengkap** (semua aktivitas tercatat)

## Troubleshooting

### Error: "User account not configured"
```bash
python setup_autojoin.py
```

### Error: "Session expired"
Hapus file `user_session.session` dan jalankan setup lagi.

### Error: "Invalid invite link"
Pastikan format link benar:
- `https://t.me/+abc123` (private group)
- `https://t.me/namagroup` (public channel)

### Bot tidak respond
1. Cek apakah bot token valid
2. Restart bot: `python main.py`
3. Cek log di folder `logs/`

## Keamanan

- **API credentials** disimpan lokal di file `user_telegram_config.json`
- **Session** disimpan di file `user_session.session`
- **Tidak ada data** yang dikirim ke server eksternal
- **Akun Anda** tetap aman dan terkontrol

## Cara Kerja

1. **User Account**: Bergabung ke grup (akun Anda)
2. **Bot**: Mengelola grup yang sudah diikuti
3. **Broadcast**: Bot mengirim pesan ke semua grup
4. **Storage**: Menyimpan daftar grup di file JSON

## File yang Dibuat

- `user_telegram_config.json` - Konfigurasi API
- `user_session.session` - Session Telegram
- `joined_groups.json` - Daftar grup yang diikuti
- `logs/user_autojoin.log` - Log aktivitas

## Catatan Penting

- Setup hanya dilakukan **sekali**
- Akun Anda **tetap aman** dan terkontrol
- Bot akan menggunakan akun Anda hanya untuk bergabung ke grup
- Semua aktivitas tercatat di log untuk transparansi

---

**Selamat menggunakan fitur auto-join yang sesungguhnya bekerja! 🎉**