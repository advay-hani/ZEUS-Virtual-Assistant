"""
Chat Interface for Z.E.U.S. Virtual Assistant

This module provides the chat UI components including:
- Scrollable message display
- Message input field with send functionality
- Typing indicator
- Message formatting for user/AI distinction
- Comprehensive error handling and user feedback
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from typing import Optional, Callable
import threading
from datetime import datetime
import logging

from core.error_handler import ErrorHandler, ErrorCategory, ErrorSeverity, handle_errors
from .styles import apply_modern_styling, create_styled_button, create_card_frame


class ChatInterface:
    """
    Chat interface component for Z.E.U.S. Virtual Assistant
    
    Provides a complete chat UI with message display, input handling,
    and visual feedback for AI processing.
    """
    
    def __init__(self, parent: ttk.Frame, ai_engine=None, context_manager=None, error_handler=None):
        """
        Initialize the chat interface
        
        Args:
            parent: Parent frame to contain the chat interface
            ai_engine: AI engine instance for message processing
            context_manager: Context manager for cross-feature context
            error_handler: Error handler for user feedback
        """
        self.parent = parent
        self.ai_engine = ai_engine
        self.context_manager = context_manager
        self.error_handler = error_handler
        self.logger = logging.getLogger(__name__)
        
        # UI components
        self.chat_display = None
        self.message_input = None
        self.send_button = None
        self.typing_indicator = None
        self.typing_frame = None
        
        # State management
        self.is_processing = False
        self.message_callback = None
        self.document_context = None
        self.conversation_mode = "general"  # general, document, game
        self.message_count = 0
        self.error_count = 0
        self.last_error_time = None
        
        # Create the interface
        try:
            self.create_widgets()
            self.setup_bindings()
        except Exception as e:
            if self.error_handler:
                self.error_handler.handle_error(
                    e, ErrorCategory.SYSTEM, ErrorSeverity.CRITICAL,
                    custom_message="Failed to initialize chat interface. Please restart the application."
                )
            else:
                messagebox.showerror("Initialization Error", f"Failed to create chat interface: {str(e)}")
            raise
    
    def create_widgets(self):
        """Create all chat interface widgets"""
        # Main chat container
        chat_container = ttk.Frame(self.parent)
        chat_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Chat header
        self._create_chat_header(chat_container)
        
        # Message display area
        self._create_message_display(chat_container)
        
        # Typing indicator area
        self._create_typing_indicator(chat_container)
        
        # Message input area
        self._create_message_input(chat_container)
        
        # Show welcome message
        self._show_welcome_message()
    
    def _create_chat_header(self, parent):
        """Create the chat header with title and status"""
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Chat title
        title_label = ttk.Label(
            header_frame,
            text="💬 Chat with Z.E.U.S.",
            font=("Arial", 16, "bold"),
            foreground="#0078d4"
        )
        title_label.pack(side=tk.LEFT)
        
        # Status indicator
        self.status_label = ttk.Label(
            header_frame,
            text="● Online",
            font=("Arial", 10),
            foreground="#28a745"
        )
        self.status_label.pack(side=tk.RIGHT)
        
        # Separator
        separator = ttk.Separator(parent, orient='horizontal')
        separator.pack(fill=tk.X, pady=(0, 10))
    
    def _create_message_display(self, parent):
        """Create the scrollable message display area"""
        # Message display frame with border
        display_frame = ttk.Frame(parent, relief=tk.SUNKEN, borderwidth=1)
        display_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Scrollable text widget for messages
        self.chat_display = scrolledtext.ScrolledText(
            display_frame,
            wrap=tk.WORD,
            state=tk.DISABLED,
            font=("Arial", 11),
            bg="#ffffff",
            fg="#333333",
            padx=10,
            pady=10,
            height=20
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True)
        
        # Apply modern styling
        apply_modern_styling(self.chat_display)
        
        # Configure text tags for message formatting
        self._configure_message_tags()
    
    def _configure_message_tags(self):
        """Configure text tags for different message types"""
        # User message styling
        self.chat_display.tag_configure(
            "user_message",
            foreground="#0078d4",
            font=("Arial", 11, "bold"),
            spacing1=10,
            spacing3=5
        )
        
        # AI message styling
        self.chat_display.tag_configure(
            "ai_message",
            foreground="#28a745",
            font=("Arial", 11, "bold"),
            spacing1=10,
            spacing3=5
        )
        
        # Message content styling
        self.chat_display.tag_configure(
            "message_content",
            foreground="#333333",
            font=("Arial", 11),
            lmargin1=20,
            lmargin2=20,
            spacing3=10
        )
        
        # Timestamp styling
        self.chat_display.tag_configure(
            "timestamp",
            foreground="#666666",
            font=("Arial", 9),
            lmargin1=20,
            spacing3=5
        )
        
        # System message styling
        self.chat_display.tag_configure(
            "system_message",
            foreground="#6c757d",
            font=("Arial", 10, "italic"),
            justify=tk.CENTER,
            spacing1=5,
            spacing3=5
        )
    
    def _create_typing_indicator(self, parent):
        """Create the typing indicator area"""
        self.typing_frame = ttk.Frame(parent)
        # Don't pack initially - will be shown when needed
        
        self.typing_indicator = ttk.Label(
            self.typing_frame,
            text="Z.E.U.S. is typing...",
            font=("Arial", 10, "italic"),
            foreground="#6c757d"
        )
        self.typing_indicator.pack(side=tk.LEFT, padx=10)
        
        # Animated dots for typing effect
        self.typing_dots = ttk.Label(
            self.typing_frame,
            text="",
            font=("Arial", 10),
            foreground="#6c757d"
        )
        self.typing_dots.pack(side=tk.LEFT)
    
    def _create_message_input(self, parent):
        """Create the message input area"""
        input_frame = ttk.Frame(parent)
        input_frame.pack(fill=tk.X, pady=(5, 0))
        
        # Message input field
        self.message_input = tk.Text(
            input_frame,
            height=3,
            wrap=tk.WORD,
            font=("Arial", 11),
            bg="#ffffff",
            fg="#333333",
            relief=tk.SUNKEN,
            borderwidth=1,
            padx=10,
            pady=8
        )
        self.message_input.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Apply modern styling
        apply_modern_styling(self.message_input)
        
        # Send button with modern styling
        self.send_button = create_styled_button(
            input_frame,
            text="Send",
            command=self._on_send_clicked,
            style="Primary"
        )
        self.send_button.configure(width=10)
        self.send_button.pack(side=tk.RIGHT, pady=2)
        
        # Character counter (optional)
        self.char_counter = ttk.Label(
            parent,
            text="0 characters",
            font=("Arial", 9),
            foreground="#666666"
        )
        self.char_counter.pack(anchor=tk.E, pady=(2, 0))
    
    def setup_bindings(self):
        """Setup keyboard bindings and event handlers"""
        # Send message on Ctrl+Enter
        self.message_input.bind('<Control-Return>', lambda e: self._on_send_clicked())
        
        # Update character counter
        self.message_input.bind('<KeyRelease>', self._update_char_counter)
        
        # Focus management
        self.message_input.bind('<FocusIn>', self._on_input_focus)
        
        # Prevent newline on Enter (optional - can be removed if multiline is preferred)
        # self.message_input.bind('<Return>', lambda e: 'break')
    
    def _show_welcome_message(self):
        """Show initial welcome message"""
        welcome_text = (
            "Hello! I'm Z.E.U.S., your virtual assistant. I'm here to help you with:\n\n"
            "• Answering questions and having conversations\n"
            "• Analyzing documents you upload\n"
            "• Playing interactive games\n\n"
            "How can I assist you today?"
        )
        self.display_message("zeus", welcome_text, show_timestamp=False)
    
    def display_message(self, sender: str, message: str, show_timestamp: bool = True):
        """
        Display a message in the chat interface
        
        Args:
            sender: 'user' or 'zeus'
            message: Message content
            show_timestamp: Whether to show timestamp
        """
        self.chat_display.configure(state=tk.NORMAL)
        
        # Add sender name
        sender_name = "You" if sender == "user" else "Z.E.U.S."
        tag = "user_message" if sender == "user" else "ai_message"
        
        self.chat_display.insert(tk.END, f"{sender_name}:\n", tag)
        
        # Add message content
        self.chat_display.insert(tk.END, f"{message}\n", "message_content")
        
        # Add timestamp if requested
        if show_timestamp:
            timestamp = datetime.now().strftime("%H:%M")
            self.chat_display.insert(tk.END, f"{timestamp}\n", "timestamp")
        
        # Add spacing
        self.chat_display.insert(tk.END, "\n")
        
        self.chat_display.configure(state=tk.DISABLED)
        self.chat_display.see(tk.END)
    
    def display_system_message(self, message: str):
        """
        Display a system message (e.g., status updates)
        
        Args:
            message: System message content
        """
        self.chat_display.configure(state=tk.NORMAL)
        self.chat_display.insert(tk.END, f"--- {message} ---\n\n", "system_message")
        self.chat_display.configure(state=tk.DISABLED)
        self.chat_display.see(tk.END)
    
    def show_typing_indicator(self):
        """Show the typing indicator with animation"""
        if not self.is_processing:
            self.is_processing = True
            self.typing_frame.pack(fill=tk.X, pady=(5, 5))
            self.send_button.configure(state=tk.DISABLED)
            self.message_input.configure(state=tk.DISABLED)
            
            # Start typing animation
            self._animate_typing_dots()
    
    def hide_typing_indicator(self):
        """Hide the typing indicator"""
        self.is_processing = False
        self.typing_frame.pack_forget()
        self.send_button.configure(state=tk.NORMAL)
        self.message_input.configure(state=tk.NORMAL)
        self.message_input.focus_set()
    
    def _animate_typing_dots(self):
        """Animate the typing indicator dots"""
        if not self.is_processing:
            return
        
        # Check if widgets still exist
        try:
            if not self.typing_dots.winfo_exists():
                return
        except tk.TclError:
            return
        
        dots = ["", ".", "..", "..."]
        current_dots = self.typing_dots.cget("text")
        
        try:
            current_index = dots.index(current_dots)
            next_index = (current_index + 1) % len(dots)
        except ValueError:
            next_index = 0
        
        self.typing_dots.configure(text=dots[next_index])
        
        # Schedule next animation frame
        try:
            self.parent.after(500, self._animate_typing_dots)
        except tk.TclError:
            # Widget destroyed, stop animation
            pass
    
    def _on_send_clicked(self):
        """Handle send button click"""
        message = self.message_input.get("1.0", tk.END).strip()
        
        if not message:
            return
        
        # Clear input field
        self.message_input.delete("1.0", tk.END)
        self._update_char_counter()
        
        # Display user message
        self.display_message("user", message)
        
        # Process message
        self._process_message(message)
    
    def _process_message(self, message: str):
        """
        Process user message and generate AI response with comprehensive error handling
        
        Args:
            message: User message to process
        """
        # Validate message
        if not message or not message.strip():
            if self.error_handler:
                self.error_handler.handle_warning(
                    "Please enter a message before sending.",
                    ErrorCategory.USER_INPUT,
                    show_dialog=False
                )
            return
        
        # Check message length
        if len(message) > 5000:
            if self.error_handler:
                self.error_handler.handle_warning(
                    "Your message is very long. I'll process the first 5000 characters.",
                    ErrorCategory.USER_INPUT,
                    show_dialog=False
                )
            message = message[:5000] + "..."
        
        # Track message count for performance monitoring
        self.message_count += 1
        
        # Show typing indicator
        self.show_typing_indicator()
        
        # Process in background thread to keep UI responsive
        def process_in_background():
            response = ""
            processing_start_time = datetime.now()
            
            try:
                # Determine context type based on current mode and message content
                from core.context_manager import ContextType
                context_type = None
                
                if self.context_manager:
                    try:
                        context_summary = self.context_manager.get_context_summary()
                        current_mode = context_summary.get('current_mode', 'general')
                        
                        if current_mode == 'document' or self._is_document_query(message):
                            context_type = ContextType.DOCUMENT
                        elif current_mode == 'game' or self._is_game_query(message):
                            context_type = ContextType.GAME
                        else:
                            context_type = ContextType.GENERAL
                    except Exception as e:
                        self.logger.warning(f"Error getting context: {e}")
                        context_type = ContextType.GENERAL
                
                # Check if we have document context and this might be a document query
                if self.document_context and self._is_document_query(message):
                    # Process as document query
                    if self.ai_engine:
                        try:
                            response = self.ai_engine.analyze_document_query(
                                message, 
                                self.document_context['chunks']
                            )
                        except Exception as e:
                            self.logger.error(f"Document query error: {e}")
                            if self.error_handler:
                                self.error_handler.handle_error(
                                    e, ErrorCategory.DOCUMENT, ErrorSeverity.ERROR,
                                    custom_message="Error analyzing document. Using basic search.",
                                    show_dialog=False
                                )
                            response = self._fallback_document_response(message)
                    else:
                        response = self._fallback_document_response(message)
                else:
                    # Process as general query with context awareness
                    if self.ai_engine:
                        try:
                            # Check AI engine status first
                            status = self.ai_engine.get_model_status()
                            
                            if status.get('fallback_mode', True):
                                # Inform user about fallback mode on first use
                                if not hasattr(self, '_fallback_notified'):
                                    self._fallback_notified = True
                                    fallback_msg = ("Note: I'm currently running in basic mode. "
                                                  "For enhanced AI features, please ensure all dependencies are installed.\n\n")
                                    response = fallback_msg + self.ai_engine.generate_response(message, context_type=context_type)
                                else:
                                    response = self.ai_engine.generate_response(message, context_type=context_type)
                            else:
                                response = self.ai_engine.generate_response(message, context_type=context_type)
                        except Exception as e:
                            self.logger.error(f"AI engine error: {e}")
                            if self.error_handler:
                                self.error_handler.handle_error(
                                    e, ErrorCategory.AI_MODEL, ErrorSeverity.ERROR,
                                    custom_message="AI processing error. Using basic response mode.",
                                    show_dialog=False
                                )
                            response = self._generate_fallback_response(message)
                    else:
                        # Fallback response when no AI engine is available
                        response = self._generate_fallback_response(message)
                
                # Validate response
                if not response or not response.strip():
                    response = "I'm sorry, I couldn't generate a response. Please try rephrasing your message."
                
                # Check processing time
                processing_time = (datetime.now() - processing_start_time).total_seconds()
                if processing_time > 15:  # Log slow responses
                    self.logger.warning(f"Slow response generation: {processing_time:.2f} seconds")
                
                # Update UI in main thread
                self.parent.after(0, lambda: self._handle_ai_response(response))
                
            except MemoryError as e:
                self.error_count += 1
                error_response = ("I'm running low on memory. Please try a shorter message, "
                                "close other applications, or restart the application.")
                if self.error_handler:
                    self.error_handler.handle_error(
                        e, ErrorCategory.MEMORY, ErrorSeverity.ERROR,
                        custom_message=error_response,
                        custom_recovery=[
                            "Try shorter messages",
                            "Close other applications",
                            "Restart the application"
                        ],
                        show_dialog=False
                    )
                self.parent.after(0, lambda: self._handle_ai_response(error_response))
                
            except Exception as e:
                self.error_count += 1
                self.last_error_time = datetime.now()
                
                # Enhanced error handling with specific error types
                if "timeout" in str(e).lower():
                    error_response = ("Response generation timed out. Please try again with a shorter message.")
                elif "model" in str(e).lower():
                    error_response = ("I'm having trouble with my AI models. I'll try to help you in basic mode instead.")
                elif "connection" in str(e).lower():
                    error_response = ("Connection issue detected. Please check your internet connection.")
                else:
                    error_response = f"I encountered an error while processing your message. Please try again."
                
                # Log the error
                self.logger.error(f"Message processing error: {e}")
                
                # Handle error through error handler
                if self.error_handler:
                    self.error_handler.handle_error(
                        e, ErrorCategory.AI_MODEL, ErrorSeverity.ERROR,
                        custom_message="Error processing your message.",
                        context={"message_length": len(message), "message_count": self.message_count},
                        show_dialog=False
                    )
                
                # Try fallback response as backup
                try:
                    if self.document_context and self._is_document_query(message):
                        fallback = self._fallback_document_response(message)
                    else:
                        fallback = self._generate_fallback_response(message)
                    
                    if fallback and fallback.strip():
                        error_response += f"\n\nHere's what I can tell you: {fallback}"
                except Exception as fallback_error:
                    self.logger.error(f"Fallback response error: {fallback_error}")
                
                self.parent.after(0, lambda: self._handle_ai_response(error_response))
        
        # Start background processing with timeout handling
        try:
            thread = threading.Thread(target=process_in_background, daemon=True)
            thread.start()
            
            # Set a timeout to prevent indefinite waiting
            def timeout_handler():
                if self.is_processing:
                    timeout_response = ("I'm taking longer than expected to respond. "
                                      "Please try again or restart the application if this continues.")
                    if self.error_handler:
                        self.error_handler.handle_warning(
                            "Response generation timed out.",
                            ErrorCategory.AI_MODEL,
                            show_dialog=False
                        )
                    self._handle_ai_response(timeout_response)
            
            # 30 second timeout
            self.parent.after(30000, timeout_handler)
            
        except Exception as e:
            self.logger.error(f"Error starting message processing thread: {e}")
            if self.error_handler:
                self.error_handler.handle_error(
                    e, ErrorCategory.SYSTEM, ErrorSeverity.ERROR,
                    custom_message="Failed to process message. Please try again."
                )
            self.hide_typing_indicator()
            self.display_message("zeus", "I'm sorry, I couldn't process your message. Please try again.")
    
    def _handle_ai_response(self, response: str):
        """
        Handle AI response in the main thread
        
        Args:
            response: AI generated response
        """
        # Hide typing indicator
        self.hide_typing_indicator()
        
        # Display AI response
        self.display_message("zeus", response)
        
        # Call message callback if set
        if self.message_callback:
            self.message_callback("ai_response", response)
    
    def _generate_fallback_response(self, message: str) -> str:
        """
        Generate a fallback response when AI engine is not available
        
        Args:
            message: User message
            
        Returns:
            str: Fallback response
        """
        message_lower = message.lower()
        
        if any(word in message_lower for word in ['hello', 'hi', 'hey']):
            return "Hello! I'm Z.E.U.S. How can I help you today?"
        
        elif any(word in message_lower for word in ['help', 'what can you do']):
            return ("I can help you with:\n"
                   "• Chatting and answering questions\n"
                   "• Analyzing uploaded documents\n"
                   "• Playing games like Tic-Tac-Toe, Connect 4, and Battleship\n\n"
                   "What would you like to do?")
        
        elif any(word in message_lower for word in ['document', 'upload', 'file']):
            return ("To analyze documents, please use the Documents section from the sidebar. "
                   "You can upload PDF and DOC files for analysis there.")
        
        elif any(word in message_lower for word in ['game', 'play']):
            return ("To play games, please use the Games section from the sidebar. "
                   "I have Tic-Tac-Toe, Connect 4, and Battleship available!")
        
        else:
            return ("I understand you're asking about something. I'm currently running in basic mode, "
                   "but I'm still here to help! You can ask me about documents, games, or general questions.")
    
    def _update_char_counter(self, event=None):
        """Update the character counter"""
        content = self.message_input.get("1.0", tk.END)
        char_count = len(content) - 1  # Subtract 1 for the automatic newline
        self.char_counter.configure(text=f"{char_count} characters")
    
    def _on_input_focus(self, event=None):
        """Handle input field focus"""
        # Could add placeholder text handling here if needed
        pass
    
    def send_message(self, message: str):
        """
        Programmatically send a message
        
        Args:
            message: Message to send
        """
        self.message_input.delete("1.0", tk.END)
        self.message_input.insert("1.0", message)
        self._on_send_clicked()
    
    def clear_chat(self):
        """Clear all messages from the chat display"""
        self.chat_display.configure(state=tk.NORMAL)
        self.chat_display.delete("1.0", tk.END)
        self.chat_display.configure(state=tk.DISABLED)
        
        # Show welcome message again
        self._show_welcome_message()
    
    def set_message_callback(self, callback: Callable):
        """
        Set a callback function for message events
        
        Args:
            callback: Function to call on message events
        """
        self.message_callback = callback
    
    def set_ai_engine(self, ai_engine):
        """
        Set or update the AI engine
        
        Args:
            ai_engine: AI engine instance
        """
        self.ai_engine = ai_engine
    
    def get_message_count(self) -> int:
        """
        Get the current number of messages in the chat
        
        Returns:
            int: Number of messages
        """
        # This is a simple approximation based on content
        content = self.chat_display.get("1.0", tk.END)
        return content.count("You:") + content.count("Z.E.U.S.:")
    
    def export_chat_history(self) -> str:
        """
        Export chat history as text
        
        Returns:
            str: Chat history
        """
        return self.chat_display.get("1.0", tk.END)
    
    def set_document_context(self, document_chunks: list, document_name: str = None):
        """
        Set document context for document-aware conversations
        
        Args:
            document_chunks: List of document text chunks
            document_name: Name of the document (optional)
        """
        self.document_context = {
            'chunks': document_chunks,
            'name': document_name or 'uploaded document'
        }
        self.conversation_mode = "document"
        
        # Notify user about document context
        context_msg = f"Document '{self.document_context['name']}' is now available for questions."
        self.display_system_message(context_msg)
    
    def clear_document_context(self):
        """Clear document context and return to general conversation mode"""
        if self.document_context:
            doc_name = self.document_context.get('name', 'document')
            self.document_context = None
            self.conversation_mode = "general"
            
            # Notify user
            self.display_system_message(f"Document context for '{doc_name}' cleared.")
    
    def set_conversation_mode(self, mode: str):
        """
        Set conversation mode (general, document, game)
        
        Args:
            mode: Conversation mode
        """
        if mode in ["general", "document", "game"]:
            self.conversation_mode = mode
            
            # Update status indicator
            mode_colors = {
                "general": "#28a745",
                "document": "#0078d4", 
                "game": "#fd7e14"
            }
            mode_text = {
                "general": "● Chat Mode",
                "document": "● Document Mode",
                "game": "● Game Mode"
            }
            
            self.status_label.configure(
                text=mode_text[mode],
                foreground=mode_colors[mode]
            )
    
    def process_document_query(self, query: str):
        """
        Process a query specifically about the loaded document
        
        Args:
            query: User query about the document
        """
        if not self.document_context:
            response = ("No document is currently loaded. "
                       "Please upload a document first to ask questions about it.")
            self.display_message("zeus", response)
            return
        
        # Show typing indicator
        self.show_typing_indicator()
        
        def process_in_background():
            try:
                if self.ai_engine:
                    response = self.ai_engine.analyze_document_query(
                        query, 
                        self.document_context['chunks']
                    )
                else:
                    # Fallback document response
                    response = self._fallback_document_response(query)
                
                self.parent.after(0, lambda: self._handle_ai_response(response))
                
            except Exception as e:
                error_response = f"Error analyzing document: {str(e)}"
                self.parent.after(0, lambda: self._handle_ai_response(error_response))
        
        thread = threading.Thread(target=process_in_background, daemon=True)
        thread.start()
    
    def _is_document_query(self, message: str) -> bool:
        """
        Determine if a message is likely a document-related query
        
        Args:
            message: User message
            
        Returns:
            bool: True if likely a document query
        """
        if not self.document_context:
            return False
        
        # Document query indicators
        doc_indicators = [
            'document', 'doc', 'file', 'text', 'content', 'paper', 'article',
            'what does', 'according to', 'in the', 'from the', 'based on',
            'explain', 'summarize', 'summary', 'tell me about', 'what is',
            'how does', 'why does', 'when does', 'where does', 'who is'
        ]
        
        message_lower = message.lower()
        
        # Check for document indicators
        has_doc_indicator = any(indicator in message_lower for indicator in doc_indicators)
        
        # Check for question words (likely asking about content)
        question_words = ['what', 'how', 'why', 'when', 'where', 'who', 'which']
        has_question = any(word in message_lower for word in question_words)
        
        # If in document mode, assume most queries are document-related
        if self.conversation_mode == "document":
            return has_doc_indicator or has_question or len(message.split()) > 3
        
        return has_doc_indicator
    
    def _fallback_document_response(self, query: str) -> str:
        """
        Generate fallback response for document queries
        
        Args:
            query: User query
            
        Returns:
            str: Fallback response
        """
        if not self.document_context:
            return "No document context available."
        
        chunks = self.document_context['chunks']
        query_words = query.lower().split()
        
        # Simple keyword matching
        relevant_chunks = []
        for chunk in chunks:
            chunk_lower = chunk.lower()
            if any(word in chunk_lower for word in query_words if len(word) > 2):
                relevant_chunks.append(chunk)
        
        if relevant_chunks:
            # Find the most relevant chunk (most keyword matches)
            best_chunk = max(relevant_chunks, key=lambda chunk: 
                           sum(1 for word in query_words if len(word) > 2 and word in chunk.lower()))
            
            return (f"Based on the document '{self.document_context['name']}', here's what I found:\n\n"
                   f"{best_chunk[:400]}{'...' if len(best_chunk) > 400 else ''}\n\n"
                   f"(Note: Running in basic mode - for enhanced analysis, "
                   f"please ensure AI dependencies are installed)")
        else:
            return (f"I couldn't find specific information about your query in the document "
                   f"'{self.document_context['name']}'. Try rephrasing your question or "
                   f"check if the document contains that information.")