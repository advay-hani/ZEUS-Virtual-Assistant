"""
JSON-based persistence utilities for saving and loading application state.
"""
import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

from models.data_models import Document, ChatMessage, GameState


class PersistenceManager:
    """Manages saving and loading application state to/from JSON files."""
    
    def __init__(self, data_dir: str = "data"):
        """Initialize persistence manager with data directory."""
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        # Define file paths for different data types
        self.documents_file = self.data_dir / "documents.json"
        self.chat_history_file = self.data_dir / "chat_history.json"
        self.game_states_file = self.data_dir / "game_states.json"
    
    def _serialize_datetime(self, obj: Any) -> Any:
        """Custom JSON serializer for datetime objects."""
        if isinstance(obj, datetime):
            return obj.isoformat()
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
    
    def _deserialize_datetime(self, date_string: str) -> datetime:
        """Convert ISO format string back to datetime object."""
        return datetime.fromisoformat(date_string)
    
    def save_documents(self, documents: List[Document]) -> bool:
        """Save list of documents to JSON file."""
        try:
            documents_data = []
            for doc in documents:
                doc_dict = {
                    "id": doc.id,
                    "filename": doc.filename,
                    "file_path": doc.file_path,
                    "text_content": doc.text_content,
                    "chunks": doc.chunks,
                    "upload_date": doc.upload_date.isoformat(),
                    "file_size": doc.file_size
                }
                documents_data.append(doc_dict)
            
            with open(self.documents_file, 'w', encoding='utf-8') as f:
                json.dump(documents_data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving documents: {e}")
            return False
    
    def load_documents(self) -> List[Document]:
        """Load documents from JSON file."""
        try:
            if not self.documents_file.exists():
                return []
            
            with open(self.documents_file, 'r', encoding='utf-8') as f:
                documents_data = json.load(f)
            
            documents = []
            for doc_dict in documents_data:
                doc = Document(
                    id=doc_dict["id"],
                    filename=doc_dict["filename"],
                    file_path=doc_dict["file_path"],
                    text_content=doc_dict["text_content"],
                    chunks=doc_dict["chunks"],
                    upload_date=self._deserialize_datetime(doc_dict["upload_date"]),
                    file_size=doc_dict["file_size"]
                )
                documents.append(doc)
            return documents
        except Exception as e:
            print(f"Error loading documents: {e}")
            return []
    
    def save_chat_history(self, messages: List[ChatMessage]) -> bool:
        """Save chat history to JSON file."""
        try:
            messages_data = []
            for msg in messages:
                msg_dict = {
                    "id": msg.id,
                    "sender": msg.sender,
                    "content": msg.content,
                    "timestamp": msg.timestamp.isoformat(),
                    "context_type": msg.context_type
                }
                messages_data.append(msg_dict)
            
            with open(self.chat_history_file, 'w', encoding='utf-8') as f:
                json.dump(messages_data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving chat history: {e}")
            return False
    
    def load_chat_history(self) -> List[ChatMessage]:
        """Load chat history from JSON file."""
        try:
            if not self.chat_history_file.exists():
                return []
            
            with open(self.chat_history_file, 'r', encoding='utf-8') as f:
                messages_data = json.load(f)
            
            messages = []
            for msg_dict in messages_data:
                msg = ChatMessage(
                    id=msg_dict["id"],
                    sender=msg_dict["sender"],
                    content=msg_dict["content"],
                    timestamp=self._deserialize_datetime(msg_dict["timestamp"]),
                    context_type=msg_dict["context_type"]
                )
                messages.append(msg)
            return messages
        except Exception as e:
            print(f"Error loading chat history: {e}")
            return []
    
    def save_game_state(self, game_state: GameState) -> bool:
        """Save current game state to JSON file."""
        try:
            game_data = {
                "game_type": game_state.game_type,
                "board_state": game_state.board_state,
                "current_player": game_state.current_player,
                "game_status": game_state.game_status,
                "move_history": game_state.move_history,
                "ai_difficulty": game_state.ai_difficulty
            }
            
            with open(self.game_states_file, 'w', encoding='utf-8') as f:
                json.dump(game_data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving game state: {e}")
            return False
    
    def load_game_state(self) -> Optional[GameState]:
        """Load game state from JSON file."""
        try:
            if not self.game_states_file.exists():
                return None
            
            with open(self.game_states_file, 'r', encoding='utf-8') as f:
                game_data = json.load(f)
            
            game_state = GameState(
                game_type=game_data["game_type"],
                board_state=game_data["board_state"],
                current_player=game_data["current_player"],
                game_status=game_data["game_status"],
                move_history=game_data["move_history"],
                ai_difficulty=game_data["ai_difficulty"]
            )
            return game_state
        except Exception as e:
            print(f"Error loading game state: {e}")
            return None
    
    def clear_all_data(self) -> bool:
        """Clear all persisted data files."""
        try:
            for file_path in [self.documents_file, self.chat_history_file, self.game_states_file]:
                if file_path.exists():
                    file_path.unlink()
            return True
        except Exception as e:
            print(f"Error clearing data: {e}")
            return False