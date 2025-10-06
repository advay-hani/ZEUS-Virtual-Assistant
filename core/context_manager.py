"""
Cross-Feature Context Management for Z.E.U.S. Virtual Assistant

This module provides context preservation and intelligent memory management
across chat, documents, and games features.
"""

import json
import logging
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
from enum import Enum

from models.data_models import Document, ChatMessage, GameState


class ContextType(Enum):
    """Types of context that can be managed"""
    GENERAL = "general"
    DOCUMENT = "document"
    GAME = "game"


class ContextPriority(Enum):
    """Priority levels for context preservation"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class ContextItem:
    """Individual context item with metadata"""
    id: str
    context_type: ContextType
    priority: ContextPriority
    data: Dict[str, Any]
    created_at: datetime = field(default_factory=datetime.now)
    last_accessed: datetime = field(default_factory=datetime.now)
    access_count: int = 0
    expires_at: Optional[datetime] = None
    
    def update_access(self):
        """Update access tracking"""
        self.last_accessed = datetime.now()
        self.access_count += 1


@dataclass
class ConversationState:
    """Current conversation state across features"""
    current_mode: ContextType = ContextType.GENERAL
    active_document: Optional[str] = None  # Document ID
    active_game: Optional[str] = None  # Game type
    conversation_history: List[ChatMessage] = field(default_factory=list)
    document_context: Optional[Dict[str, Any]] = None
    game_context: Optional[Dict[str, Any]] = None
    last_updated: datetime = field(default_factory=datetime.now)


class ContextManager:
    """
    Manages context preservation and intelligent memory management
    across different application features.
    """
    
    def __init__(self, data_dir: str = "data", max_memory_mb: int = 50):
        """
        Initialize context manager
        
        Args:
            data_dir: Directory for context persistence
            max_memory_mb: Maximum memory usage for context (MB)
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        self.context_file = self.data_dir / "context_state.json"
        self.max_memory_bytes = max_memory_mb * 1024 * 1024
        
        self.logger = logging.getLogger(__name__)
        
        # Context storage
        self.context_items: Dict[str, ContextItem] = {}
        self.conversation_state = ConversationState()
        
        # Memory management settings
        self.max_conversation_history = 100  # Maximum chat messages to keep
        self.context_expiry_hours = 24  # Hours before context expires
        self.cleanup_threshold = 0.8  # Cleanup when 80% of memory is used
        
        # Load existing context
        self.load_context()
    
    def switch_context(self, new_mode: ContextType, context_data: Optional[Dict[str, Any]] = None) -> bool:
        """
        Switch between different application contexts
        
        Args:
            new_mode: New context mode to switch to
            context_data: Optional context-specific data
            
        Returns:
            bool: True if switch was successful
        """
        try:
            old_mode = self.conversation_state.current_mode
            
            # Save current context before switching
            self._save_current_context()
            
            # Update conversation state
            self.conversation_state.current_mode = new_mode
            self.conversation_state.last_updated = datetime.now()
            
            # Handle mode-specific context switching
            if new_mode == ContextType.DOCUMENT:
                self._switch_to_document_context(context_data)
            elif new_mode == ContextType.GAME:
                self._switch_to_game_context(context_data)
            elif new_mode == ContextType.GENERAL:
                self._switch_to_general_context()
            
            self.logger.info(f"Context switched from {old_mode.value} to {new_mode.value}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error switching context: {e}")
            return False
    
    def add_conversation_message(self, message: ChatMessage) -> bool:
        """
        Add a message to conversation history with context awareness
        
        Args:
            message: Chat message to add
            
        Returns:
            bool: True if message was added successfully
        """
        try:
            # Add to conversation history
            self.conversation_state.conversation_history.append(message)
            
            # Update context based on message content
            self._update_context_from_message(message)
            
            # Manage memory if needed
            self._manage_conversation_memory()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error adding conversation message: {e}")
            return False
    
    def set_document_context(self, document: Document, chunks: List[str]) -> bool:
        """
        Set document context for document-aware conversations
        
        Args:
            document: Document object
            chunks: Document text chunks
            
        Returns:
            bool: True if context was set successfully
        """
        try:
            document_context = {
                'document_id': document.id,
                'filename': document.filename,
                'chunks': chunks,
                'upload_date': document.upload_date.isoformat(),
                'file_size': document.file_size
            }
            
            # Create context item
            context_item = ContextItem(
                id=f"document_{document.id}",
                context_type=ContextType.DOCUMENT,
                priority=ContextPriority.HIGH,
                data=document_context
            )
            
            self.context_items[context_item.id] = context_item
            self.conversation_state.active_document = document.id
            self.conversation_state.document_context = document_context
            
            self.logger.info(f"Document context set for: {document.filename}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error setting document context: {e}")
            return False
    
    def set_game_context(self, game_state: GameState) -> bool:
        """
        Set game context for game-aware interactions
        
        Args:
            game_state: Current game state
            
        Returns:
            bool: True if context was set successfully
        """
        try:
            game_context = {
                'game_type': game_state.game_type,
                'board_state': game_state.board_state,
                'current_player': game_state.current_player,
                'game_status': game_state.game_status,
                'move_history': game_state.move_history,
                'ai_difficulty': game_state.ai_difficulty
            }
            
            # Create context item
            context_item = ContextItem(
                id=f"game_{game_state.game_type}",
                context_type=ContextType.GAME,
                priority=ContextPriority.MEDIUM,
                data=game_context
            )
            
            self.context_items[context_item.id] = context_item
            self.conversation_state.active_game = game_state.game_type
            self.conversation_state.game_context = game_context
            
            self.logger.info(f"Game context set for: {game_state.game_type}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error setting game context: {e}")
            return False
    
    def get_relevant_context(self, query: str, context_type: Optional[ContextType] = None) -> Dict[str, Any]:
        """
        Get relevant context for a query
        
        Args:
            query: User query
            context_type: Specific context type to retrieve (optional)
            
        Returns:
            Dict containing relevant context information
        """
        try:
            relevant_context = {
                'conversation_history': self._get_recent_conversation(),
                'current_mode': self.conversation_state.current_mode.value,
                'document_context': None,
                'game_context': None
            }
            
            # Add document context if available and relevant
            if (self.conversation_state.document_context and 
                (context_type == ContextType.DOCUMENT or self._is_document_query(query))):
                relevant_context['document_context'] = self.conversation_state.document_context
                # Update access tracking
                doc_id = f"document_{self.conversation_state.active_document}"
                if doc_id in self.context_items:
                    self.context_items[doc_id].update_access()
            
            # Add game context if available and relevant
            if (self.conversation_state.game_context and 
                (context_type == ContextType.GAME or self._is_game_query(query))):
                relevant_context['game_context'] = self.conversation_state.game_context
                # Update access tracking
                game_id = f"game_{self.conversation_state.active_game}"
                if game_id in self.context_items:
                    self.context_items[game_id].update_access()
            
            return relevant_context
            
        except Exception as e:
            self.logger.error(f"Error getting relevant context: {e}")
            return {'conversation_history': [], 'current_mode': 'general'}
    
    def clear_context(self, context_type: Optional[ContextType] = None) -> bool:
        """
        Clear specific or all context
        
        Args:
            context_type: Specific context type to clear (None for all)
            
        Returns:
            bool: True if context was cleared successfully
        """
        try:
            if context_type is None:
                # Clear all context
                self.context_items.clear()
                self.conversation_state = ConversationState()
                self.logger.info("All context cleared")
            else:
                # Clear specific context type
                items_to_remove = [
                    item_id for item_id, item in self.context_items.items()
                    if item.context_type == context_type
                ]
                
                for item_id in items_to_remove:
                    del self.context_items[item_id]
                
                # Update conversation state
                if context_type == ContextType.DOCUMENT:
                    self.conversation_state.active_document = None
                    self.conversation_state.document_context = None
                elif context_type == ContextType.GAME:
                    self.conversation_state.active_game = None
                    self.conversation_state.game_context = None
                
                self.logger.info(f"Context cleared for type: {context_type.value}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error clearing context: {e}")
            return False
    
    def get_context_summary(self) -> Dict[str, Any]:
        """
        Get a summary of current context state
        
        Returns:
            Dict containing context summary
        """
        try:
            summary = {
                'current_mode': self.conversation_state.current_mode.value,
                'conversation_messages': len(self.conversation_state.conversation_history),
                'active_document': self.conversation_state.active_document,
                'active_game': self.conversation_state.active_game,
                'context_items': len(self.context_items),
                'memory_usage': self._estimate_memory_usage(),
                'last_updated': self.conversation_state.last_updated.isoformat()
            }
            
            # Add context item details
            context_details = {}
            for item_id, item in self.context_items.items():
                context_details[item_id] = {
                    'type': item.context_type.value,
                    'priority': item.priority.value,
                    'created_at': item.created_at.isoformat(),
                    'last_accessed': item.last_accessed.isoformat(),
                    'access_count': item.access_count
                }
            
            summary['context_details'] = context_details
            return summary
            
        except Exception as e:
            self.logger.error(f"Error getting context summary: {e}")
            return {}
    
    def save_context(self) -> bool:
        """
        Save current context state to disk
        
        Returns:
            bool: True if save was successful
        """
        try:
            # Prepare data for serialization
            context_data = {
                'conversation_state': {
                    'current_mode': self.conversation_state.current_mode.value,
                    'active_document': self.conversation_state.active_document,
                    'active_game': self.conversation_state.active_game,
                    'conversation_history': [
                        {
                            'id': msg.id,
                            'sender': msg.sender,
                            'content': msg.content,
                            'timestamp': msg.timestamp.isoformat(),
                            'context_type': msg.context_type
                        }
                        for msg in self.conversation_state.conversation_history
                    ],
                    'document_context': self.conversation_state.document_context,
                    'game_context': self.conversation_state.game_context,
                    'last_updated': self.conversation_state.last_updated.isoformat()
                },
                'context_items': {}
            }
            
            # Serialize context items
            for item_id, item in self.context_items.items():
                context_data['context_items'][item_id] = {
                    'id': item.id,
                    'context_type': item.context_type.value,
                    'priority': item.priority.value,
                    'data': item.data,
                    'created_at': item.created_at.isoformat(),
                    'last_accessed': item.last_accessed.isoformat(),
                    'access_count': item.access_count,
                    'expires_at': item.expires_at.isoformat() if item.expires_at else None
                }
            
            # Write to file
            with open(self.context_file, 'w', encoding='utf-8') as f:
                json.dump(context_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info("Context saved successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving context: {e}")
            return False
    
    def load_context(self) -> bool:
        """
        Load context state from disk
        
        Returns:
            bool: True if load was successful
        """
        try:
            if not self.context_file.exists():
                self.logger.info("No existing context file found")
                return True
            
            with open(self.context_file, 'r', encoding='utf-8') as f:
                context_data = json.load(f)
            
            # Load conversation state
            conv_state_data = context_data.get('conversation_state', {})
            
            # Reconstruct conversation history
            conversation_history = []
            for msg_data in conv_state_data.get('conversation_history', []):
                message = ChatMessage(
                    id=msg_data['id'],
                    sender=msg_data['sender'],
                    content=msg_data['content'],
                    timestamp=datetime.fromisoformat(msg_data['timestamp']),
                    context_type=msg_data['context_type']
                )
                conversation_history.append(message)
            
            # Reconstruct conversation state
            self.conversation_state = ConversationState(
                current_mode=ContextType(conv_state_data.get('current_mode', 'general')),
                active_document=conv_state_data.get('active_document'),
                active_game=conv_state_data.get('active_game'),
                conversation_history=conversation_history,
                document_context=conv_state_data.get('document_context'),
                game_context=conv_state_data.get('game_context'),
                last_updated=datetime.fromisoformat(
                    conv_state_data.get('last_updated', datetime.now().isoformat())
                )
            )
            
            # Load context items
            self.context_items = {}
            for item_id, item_data in context_data.get('context_items', {}).items():
                context_item = ContextItem(
                    id=item_data['id'],
                    context_type=ContextType(item_data['context_type']),
                    priority=ContextPriority(item_data['priority']),
                    data=item_data['data'],
                    created_at=datetime.fromisoformat(item_data['created_at']),
                    last_accessed=datetime.fromisoformat(item_data['last_accessed']),
                    access_count=item_data['access_count'],
                    expires_at=datetime.fromisoformat(item_data['expires_at']) 
                              if item_data['expires_at'] else None
                )
                self.context_items[item_id] = context_item
            
            # Clean up expired context
            self._cleanup_expired_context()
            
            self.logger.info("Context loaded successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error loading context: {e}")
            return False
    
    def _save_current_context(self):
        """Save current context state"""
        self.conversation_state.last_updated = datetime.now()
    
    def _switch_to_document_context(self, context_data: Optional[Dict[str, Any]]):
        """Switch to document context mode"""
        if context_data and 'document_id' in context_data:
            self.conversation_state.active_document = context_data['document_id']
            self.conversation_state.document_context = context_data
    
    def _switch_to_game_context(self, context_data: Optional[Dict[str, Any]]):
        """Switch to game context mode"""
        if context_data and 'game_type' in context_data:
            self.conversation_state.active_game = context_data['game_type']
            self.conversation_state.game_context = context_data
    
    def _switch_to_general_context(self):
        """Switch to general context mode"""
        # Keep document and game context available but not active
        pass
    
    def _update_context_from_message(self, message: ChatMessage):
        """Update context based on message content"""
        # Update conversation state based on message context type
        if message.context_type == "document" and self.conversation_state.document_context:
            # Document-related message
            pass
        elif message.context_type == "game" and self.conversation_state.game_context:
            # Game-related message
            pass
    
    def _manage_conversation_memory(self):
        """Manage conversation memory to stay within limits"""
        # Trim conversation history if too long
        if len(self.conversation_state.conversation_history) > self.max_conversation_history:
            # Keep recent messages and important ones
            recent_messages = self.conversation_state.conversation_history[-50:]  # Last 50 messages
            self.conversation_state.conversation_history = recent_messages
            self.logger.info("Conversation history trimmed for memory management")
        
        # Check overall memory usage
        if self._estimate_memory_usage() > self.max_memory_bytes * self.cleanup_threshold:
            self._cleanup_low_priority_context()
    
    def _get_recent_conversation(self, max_messages: int = 20) -> List[Dict[str, Any]]:
        """Get recent conversation messages"""
        recent_messages = self.conversation_state.conversation_history[-max_messages:]
        return [
            {
                'sender': msg.sender,
                'content': msg.content,
                'timestamp': msg.timestamp.isoformat(),
                'context_type': msg.context_type
            }
            for msg in recent_messages
        ]
    
    def _is_document_query(self, query: str) -> bool:
        """Determine if query is document-related"""
        doc_indicators = [
            'document', 'doc', 'file', 'text', 'content', 'paper', 'article',
            'what does', 'according to', 'in the', 'from the', 'based on'
        ]
        query_lower = query.lower()
        return any(indicator in query_lower for indicator in doc_indicators)
    
    def _is_game_query(self, query: str) -> bool:
        """Determine if query is game-related"""
        game_indicators = [
            'game', 'play', 'move', 'turn', 'board', 'win', 'lose',
            'tic-tac-toe', 'connect', 'battleship', 'strategy'
        ]
        query_lower = query.lower()
        return any(indicator in query_lower for indicator in game_indicators)
    
    def _estimate_memory_usage(self) -> int:
        """Estimate current memory usage in bytes"""
        try:
            # Rough estimation based on string lengths and object counts
            memory_usage = 0
            
            # Conversation history
            for msg in self.conversation_state.conversation_history:
                memory_usage += len(msg.content.encode('utf-8'))
                memory_usage += 200  # Overhead for message object
            
            # Context items
            for item in self.context_items.values():
                memory_usage += len(str(item.data).encode('utf-8'))
                memory_usage += 300  # Overhead for context item object
            
            return memory_usage
            
        except Exception:
            return 0
    
    def _cleanup_expired_context(self):
        """Clean up expired context items"""
        current_time = datetime.now()
        expired_items = []
        
        for item_id, item in self.context_items.items():
            # Check explicit expiry
            if item.expires_at and current_time > item.expires_at:
                expired_items.append(item_id)
            # Check age-based expiry
            elif (current_time - item.created_at).total_seconds() > self.context_expiry_hours * 3600:
                if item.priority != ContextPriority.CRITICAL:
                    expired_items.append(item_id)
        
        for item_id in expired_items:
            del self.context_items[item_id]
            self.logger.info(f"Expired context item removed: {item_id}")
    
    def _cleanup_low_priority_context(self):
        """Clean up low priority context items to free memory"""
        # Sort items by priority and access patterns
        items_by_priority = sorted(
            self.context_items.items(),
            key=lambda x: (x[1].priority.value, x[1].access_count, x[1].last_accessed),
            reverse=False
        )
        
        # Remove lowest priority items until memory is acceptable
        items_removed = 0
        for item_id, item in items_by_priority:
            if item.priority == ContextPriority.CRITICAL:
                continue
            
            del self.context_items[item_id]
            items_removed += 1
            
            # Check if we've freed enough memory
            if (self._estimate_memory_usage() < 
                self.max_memory_bytes * (self.cleanup_threshold - 0.1)):
                break
            
            # Don't remove too many items at once
            if items_removed >= 10:
                break
        
        if items_removed > 0:
            self.logger.info(f"Cleaned up {items_removed} low priority context items")