"""
Chat storage module for Telegram Auto-Join Bot
Manages storage and retrieval of chat IDs where bot is a member
"""

import json
import os
import logging
from typing import List, Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

STORAGE_FILE = "chat_storage.json"

class ChatStorage:
    """Simple file-based chat storage"""
    
    def __init__(self):
        self.storage_file = STORAGE_FILE
        self._ensure_storage_file()
    
    def _ensure_storage_file(self):
        """Ensure storage file exists"""
        if not os.path.exists(self.storage_file):
            self._save_data({"chats": {}})
    
    def _load_data(self) -> Dict:
        """Load data from storage file"""
        try:
            with open(self.storage_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"Error loading storage file: {e}")
            return {"chats": {}}
    
    def _save_data(self, data: Dict):
        """Save data to storage file"""
        try:
            with open(self.storage_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving storage file: {e}")
    
    def add_chat(self, chat_id: int, chat_title: str, chat_type: str, invite_link: str = None):
        """
        Add a chat to storage
        
        Args:
            chat_id (int): Chat ID
            chat_title (str): Chat title
            chat_type (str): Chat type (group, supergroup, channel)
            invite_link (str, optional): Original invite link used to join
        """
        data = self._load_data()
        
        chat_info = {
            "title": chat_title,
            "type": chat_type,
            "invite_link": invite_link,
            "joined_at": datetime.now().isoformat(),
            "last_broadcast": None
        }
        
        data["chats"][str(chat_id)] = chat_info
        self._save_data(data)
        
        logger.info(f"Added chat to storage: {chat_title} ({chat_id})")
    
    def remove_chat(self, chat_id: int):
        """
        Remove a chat from storage
        
        Args:
            chat_id (int): Chat ID to remove
        """
        data = self._load_data()
        
        if str(chat_id) in data["chats"]:
            chat_info = data["chats"][str(chat_id)]
            del data["chats"][str(chat_id)]
            self._save_data(data)
            logger.info(f"Removed chat from storage: {chat_info.get('title', 'Unknown')} ({chat_id})")
        else:
            logger.warning(f"Chat {chat_id} not found in storage")
    
    def get_all_chats(self) -> List[Dict]:
        """
        Get all stored chats
        
        Returns:
            List[Dict]: List of chat information
        """
        data = self._load_data()
        chats = []
        
        for chat_id, chat_info in data["chats"].items():
            chat_data = {
                "chat_id": int(chat_id),
                "title": chat_info.get("title", "Unknown"),
                "type": chat_info.get("type", "unknown"),
                "invite_link": chat_info.get("invite_link"),
                "joined_at": chat_info.get("joined_at"),
                "last_broadcast": chat_info.get("last_broadcast")
            }
            chats.append(chat_data)
        
        return chats
    
    def get_chat_count(self) -> int:
        """
        Get total number of stored chats
        
        Returns:
            int: Number of chats
        """
        data = self._load_data()
        return len(data["chats"])
    
    def update_last_broadcast(self, chat_id: int):
        """
        Update last broadcast timestamp for a chat
        
        Args:
            chat_id (int): Chat ID
        """
        data = self._load_data()
        
        if str(chat_id) in data["chats"]:
            data["chats"][str(chat_id)]["last_broadcast"] = datetime.now().isoformat()
            self._save_data(data)
    
    def is_chat_stored(self, chat_id: int) -> bool:
        """
        Check if a chat is already stored
        
        Args:
            chat_id (int): Chat ID to check
            
        Returns:
            bool: True if chat is stored
        """
        data = self._load_data()
        return str(chat_id) in data["chats"]

# Global instance
chat_storage = ChatStorage()