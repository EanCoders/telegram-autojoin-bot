#!/usr/bin/env python3
"""
Script untuk setup deployment bot ke berbagai platform hosting
"""

import os
import json
import subprocess
import sys

def create_github_repo():
    """Instruksi untuk membuat GitHub repository"""
    print("🐙 SETUP GITHUB REPOSITORY")
    print("=" * 50)
    print("1. Buka https://github.com")
    print("2. Klik 'New Repository'")
    print("3. Nama repository: telegram-autojoin-bot")
    print("4. Set ke Public")
    print("5. Klik 'Create repository'")
    print("6. Upload semua file bot ke repository")
    print("=" * 50)

def railway_setup():
    """Instruksi setup Railway.app"""
    print("\n🚂 DEPLOY KE RAILWAY.APP")
    print("=" * 50)
    print("1. Buka https://railway.app")
    print("2. Klik 'Start a New Project'")
    print("3. Login dengan GitHub")
    print("4. Pilih 'Deploy from GitHub repo'")
    print("5. Pilih repository 'telegram-autojoin-bot'")
    print("6. Tambahkan Environment Variables:")
    print("   - BOT_TOKEN = your_bot_token_here")
    print("   - PYTHONUNBUFFERED = 1")
    print("7. Deploy otomatis akan berjalan")
    print("8. Bot akan online 24/7!")
    print("=" * 50)

def render_setup():
    """Instruksi setup Render.com"""
    print("\n🎨 DEPLOY KE RENDER.COM")
    print("=" * 50)
    print("1. Buka https://render.com")
    print("2. Klik 'New +' -> 'Web Service'")
    print("3. Connect GitHub repository")
    print("4. Pilih repository 'telegram-autojoin-bot'")
    print("5. Settings:")
    print("   - Name: telegram-autojoin-bot")
    print("   - Environment: Python 3")
    print("   - Build Command: pip install -r requirements.txt")
    print("   - Start Command: python main.py")
    print("6. Environment Variables:")
    print("   - BOT_TOKEN = your_bot_token_here")
    print("   - PYTHONUNBUFFERED = 1")
    print("7. Deploy!")
    print("=" * 50)

def heroku_setup():
    """Instruksi setup Heroku"""
    print("\n🔮 DEPLOY KE HEROKU")
    print("=" * 50)
    print("1. Buka https://heroku.com")
    print("2. Buat akun dan login")
    print("3. Klik 'New' -> 'Create new app'")
    print("4. Nama app: telegram-autojoin-bot")
    print("5. Deploy tab -> Connect GitHub")
    print("6. Pilih repository")
    print("7. Settings -> Config Vars:")
    print("   - BOT_TOKEN = your_bot_token_here")
    print("8. Enable automatic deploys")
    print("9. Manual deploy untuk pertama kali")
    print("=" * 50)

def create_deployment_files():
    """Buat file yang dibutuhkan untuk deployment"""
    print("\n📁 MEMBUAT FILE DEPLOYMENT")
    print("=" * 50)
    
    # Cek file yang sudah ada
    files_created = []
    
    # Procfile untuk Heroku
    if not os.path.exists('Procfile'):
        with open('Procfile', 'w') as f:
            f.write('web: python main.py\n')
        files_created.append('Procfile')
    
    # railway.json untuk Railway
    if not os.path.exists('railway.json'):
        railway_config = {
            "$schema": "https://railway.app/railway.schema.json",
            "build": {"builder": "NIXPACKS"},
            "deploy": {
                "startCommand": "python main.py",
                "restartPolicyType": "ON_FAILURE",
                "restartPolicyMaxRetries": 10
            }
        }
        with open('railway.json', 'w') as f:
            json.dump(railway_config, f, indent=2)
        files_created.append('railway.json')
    
    # render.yaml untuk Render
    if not os.path.exists('render.yaml'):
        render_config = """services:
  - type: web
    name: telegram-autojoin-bot
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: python main.py
    envVars:
      - key: PYTHONUNBUFFERED
        value: 1
      - key: BOT_TOKEN
        sync: false
"""
        with open('render.yaml', 'w') as f:
            f.write(render_config)
        files_created.append('render.yaml')
    
    # runtime.txt untuk platform yang membutuhkan
    if not os.path.exists('runtime.txt'):
        with open('runtime.txt', 'w') as f:
            f.write('python-3.11.0\n')
        files_created.append('runtime.txt')
    
    if files_created:
        print("✅ File deployment berhasil dibuat:")
        for file in files_created:
            print(f"   - {file}")
    else:
        print("✅ Semua file deployment sudah ada")
    
    print("=" * 50)

def main():
    """Main menu untuk deployment setup"""
    print("🚀 TELEGRAM BOT DEPLOYMENT SETUP")
    print("=" * 50)
    print("Pilih platform hosting untuk bot Telegram:")
    print("1. Railway.app (Recommended - Mudah & Gratis)")
    print("2. Render.com (Alternatif Bagus)")
    print("3. Heroku (Klasik tapi Terbatas)")
    print("4. Setup GitHub Repository")
    print("5. Buat semua file deployment")
    print("6. Keluar")
    print("=" * 50)
    
    while True:
        choice = input("\nPilih opsi (1-6): ").strip()
        
        if choice == '1':
            create_deployment_files()
            railway_setup()
        elif choice == '2':
            create_deployment_files()
            render_setup()
        elif choice == '3':
            create_deployment_files()
            heroku_setup()
        elif choice == '4':
            create_github_repo()
        elif choice == '5':
            create_deployment_files()
        elif choice == '6':
            print("👋 Selamat deploy!")
            break
        else:
            print("❌ Pilihan tidak valid!")

if __name__ == "__main__":
    main()