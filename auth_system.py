"""
Authentication system for Telegram Bot
Manages user access control with verification code
"""

import json
import os
from datetime import datetime
from typing import Dict, Set

class AuthSystem:
    """Simple authentication system for bot access"""
    
    def __init__(self, auth_file: str = "authorized_users.json"):
        """
        Initialize authentication system
        
        Args:
            auth_file (str): File to store authorized users
        """
        self.auth_file = auth_file
        self.access_code = "0722"
        self.boss_username = "@OLVOII"
        self.authorized_users: Set[int] = set()
        self._load_authorized_users()
    
    def _load_authorized_users(self):
        """Load authorized users from file"""
        try:
            if os.path.exists(self.auth_file):
                with open(self.auth_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.authorized_users = set(data.get('authorized_users', []))
        except Exception as e:
            print(f"Error loading authorized users: {e}")
            self.authorized_users = set()
    
    def _save_authorized_users(self):
        """Save authorized users to file"""
        try:
            data = {
                'authorized_users': list(self.authorized_users),
                'last_updated': datetime.now().isoformat()
            }
            with open(self.auth_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving authorized users: {e}")
    
    def is_authorized(self, user_id: int) -> bool:
        """
        Check if user is authorized to use the bot
        
        Args:
            user_id (int): Telegram user ID
            
        Returns:
            bool: True if authorized, False otherwise
        """
        return user_id in self.authorized_users
    
    def verify_code(self, user_id: int, code: str) -> bool:
        """
        Verify access code and authorize user if correct
        
        Args:
            user_id (int): Telegram user ID
            code (str): Access code provided by user
            
        Returns:
            bool: True if code is correct, False otherwise
        """
        if code.strip() == self.access_code:
            self.authorized_users.add(user_id)
            self._save_authorized_users()
            return True
        return False
    
    def revoke_access(self, user_id: int):
        """
        Revoke access for a user
        
        Args:
            user_id (int): Telegram user ID
        """
        if user_id in self.authorized_users:
            self.authorized_users.remove(user_id)
            self._save_authorized_users()
    
    def get_unauthorized_message(self) -> str:
        """
        Get message to show unauthorized users
        
        Returns:
            str: Unauthorized access message
        """
        return f"🔒 KODE MINTAK SAMA BOS {self.boss_username}\n\nKirim kode akses untuk menggunakan bot ini."
    
    def get_invalid_code_message(self) -> str:
        """
        Get message for invalid code
        
        Returns:
            str: Invalid code message
        """
        return f"❌ KODE MINTAK SAMA BOS {self.boss_username}"
    
    def get_access_granted_message(self) -> str:
        """
        Get message when access is granted
        
        Returns:
            str: Access granted message
        """
        return "✅ Akses berhasil! Sekarang Anda dapat menggunakan semua fitur bot."
    
    def get_authorized_count(self) -> int:
        """
        Get number of authorized users
        
        Returns:
            int: Number of authorized users
        """
        return len(self.authorized_users)