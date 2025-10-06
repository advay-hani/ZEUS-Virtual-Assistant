"""
Core data models for the Zeus Virtual Assistant application.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Any, Optional
import uuid


@dataclass
class Document:
    """Data model for uploaded documents."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    filename: str = ""
    file_path: str = ""
    text_content: str = ""
    chunks: List[str] = field(default_factory=list)
    upload_date: datetime = field(default_factory=datetime.now)
    file_size: int = 0
    
    def __post_init__(self):
        """Validate document data after initialization."""
        if not self.filename:
            raise ValueError("Document filename cannot be empty")
        if not self.file_path:
            raise ValueError("Document file_path cannot be empty")
        if self.file_size < 0:
            raise ValueError("Document file_size cannot be negative")


@dataclass
class ChatMessage:
    """Data model for chat messages between user and Zeus."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    sender: str = ""
    content: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    context_type: str = "general"
    
    def __post_init__(self):
        """Validate chat message data after initialization."""
        if self.sender not in ["user", "zeus"]:
            raise ValueError("ChatMessage sender must be 'user' or 'zeus'")
        if not self.content.strip():
            raise ValueError("ChatMessage content cannot be empty")
        if self.context_type not in ["general", "document", "game"]:
            raise ValueError("ChatMessage context_type must be 'general', 'document', or 'game'")


@dataclass
class GameState:
    """Data model for game state management."""
    game_type: str = ""
    board_state: List[List[Any]] = field(default_factory=list)
    current_player: str = ""
    game_status: str = "active"
    move_history: List[Any] = field(default_factory=list)
    ai_difficulty: str = "medium"
    
    def __post_init__(self):
        """Validate game state data after initialization."""
        valid_games = ["tic-tac-toe", "connect4", "battleship"]
        if self.game_type not in valid_games:
            raise ValueError(f"GameState game_type must be one of {valid_games}")
        
        valid_players = ["user", "ai"]
        if self.current_player and self.current_player not in valid_players:
            raise ValueError("GameState current_player must be 'user' or 'ai'")
        
        valid_statuses = ["active", "ended", "paused"]
        if self.game_status not in valid_statuses:
            raise ValueError(f"GameState game_status must be one of {valid_statuses}")
        
        valid_difficulties = ["easy", "medium", "hard"]
        if self.ai_difficulty not in valid_difficulties:
            raise ValueError(f"GameState ai_difficulty must be one of {valid_difficulties}")