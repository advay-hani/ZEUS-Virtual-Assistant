"""
Main application window for Z.E.U.S. Virtual Assistant
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
from typing import Optional
import time
import logging
from core.context_manager import ContextManager, ContextType
from core.error_handler import ErrorHandler, ErrorCategory, ErrorSeverity
from core.performance_monitor import initialize_performance_monitoring, get_performance_monitor
from core.memory_optimizer import initialize_memory_optimizer, get_memory_optimizer
from core.background_processor import initialize_background_processor, get_background_processor
from .styles import StyleManager, setup_keyboard_navigation, setup_accessibility_features
from .keyboard_shortcuts import KeyboardShortcutManager, setup_chat_shortcuts, setup_document_shortcuts, setup_game_shortcuts
from .responsive_layout import ResponsiveLayoutManager


class ZeusMainWindow:
    """Main application window with navigation and content management"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.current_mode = "welcome"  # Track current active mode
        self.content_frame = None
        self.nav_buttons = {}
        self.status_label = None
        
        # Initialize error handler first
        self.error_handler = ErrorHandler(self.root)
        
        # Initialize performance monitoring systems
        self.performance_monitor = initialize_performance_monitoring()
        self.memory_optimizer = initialize_memory_optimizer()
        self.background_processor = initialize_background_processor()
        
        # Initialize context manager
        self.context_manager = ContextManager()
        
        # Initialize logger
        self.logger = logging.getLogger(__name__)
        
        # Performance monitoring
        self.performance_update_interval = 10000  # 10 seconds
        self.last_performance_check = 0
        
        # Initialize UI enhancement systems
        self.style_manager = StyleManager(self.root)
        self.keyboard_manager = KeyboardShortcutManager(self.root)
        self.layout_manager = ResponsiveLayoutManager(self.root)
        
        # Connect main window to keyboard manager for navigation
        self.root.main_window = self
        
        try:
            self.setup_window()
            self.create_widgets()
            self.setup_navigation()
            self.setup_ui_enhancements()
            self.setup_performance_monitoring()
        except Exception as e:
            self.error_handler.handle_error(
                e, ErrorCategory.SYSTEM, ErrorSeverity.CRITICAL,
                custom_message="Failed to initialize the main application window. Please restart the application."
            )
            raise
    
    def setup_window(self):
        """Configure the main window properties"""
        self.root.title("Z.E.U.S. Virtual Assistant")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        
        # Center the window on screen
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (1000 // 2)
        y = (self.root.winfo_screenheight() // 2) - (700 // 2)
        self.root.geometry(f"1000x700+{x}+{y}")
        
        # Set window icon if available
        try:
            # This would set a custom icon if we had one
            # self.root.iconbitmap('assets/zeus_icon.ico')
            pass
        except:
            pass
        
        # Configure window for better appearance
        self.root.configure(bg=self.style_manager.get_color('background'))
    
    def create_widgets(self):
        """Create the main window layout"""
        # Main container with padding
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create navigation sidebar
        self._create_navigation_sidebar(main_container)
        
        # Create main content area
        self._create_content_area(main_container)
        
        # Create status bar
        self._create_status_bar()
    
    def _create_navigation_sidebar(self, parent):
        """Create the navigation sidebar with buttons"""
        nav_frame = ttk.Frame(parent, width=200)
        nav_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 15))
        nav_frame.pack_propagate(False)
        
        # Application title
        title_frame = ttk.Frame(nav_frame)
        title_frame.pack(fill=tk.X, pady=(0, 30))
        
        nav_title = ttk.Label(
            title_frame, 
            text="Z.E.U.S.", 
            font=("Arial", 18, "bold"),
            foreground="#0078d4"
        )
        nav_title.pack()
        
        subtitle = ttk.Label(
            title_frame,
            text="Virtual Assistant",
            font=("Arial", 10),
            foreground="#666666"
        )
        subtitle.pack()
        
        # Navigation buttons
        nav_buttons_frame = ttk.Frame(nav_frame)
        nav_buttons_frame.pack(fill=tk.X, pady=10)
        
        # Store nav frame for responsive layout
        self.nav_frame = nav_frame
        
        # Chat button
        self.nav_buttons['chat'] = ttk.Button(
            nav_buttons_frame,
            text="💬 Chat",
            style='Nav.TButton',
            command=self.switch_to_chat,
            width=20
        )
        self.nav_buttons['chat'].pack(fill=tk.X, pady=3)
        
        # Documents button
        self.nav_buttons['documents'] = ttk.Button(
            nav_buttons_frame,
            text="📄 Documents",
            style='Nav.TButton',
            command=self.switch_to_documents,
            width=20
        )
        self.nav_buttons['documents'].pack(fill=tk.X, pady=3)
        
        # Games button
        self.nav_buttons['games'] = ttk.Button(
            nav_buttons_frame,
            text="🎮 Games",
            style='Nav.TButton',
            command=self.switch_to_games,
            width=20
        )
        self.nav_buttons['games'].pack(fill=tk.X, pady=3)
        
        # Separator
        separator = ttk.Separator(nav_frame, orient='horizontal')
        separator.pack(fill=tk.X, pady=20)
        
        # Additional info
        info_label = ttk.Label(
            nav_frame,
            text="Offline AI Assistant\nNo internet required",
            font=("Arial", 9),
            foreground="#666666",
            justify=tk.CENTER
        )
        info_label.pack(pady=10)
    
    def _create_content_area(self, parent):
        """Create the main content area"""
        # Content container with border
        content_container = ttk.Frame(parent, relief=tk.RAISED, borderwidth=1)
        content_container.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Content frame that will be replaced based on navigation
        self.content_frame = ttk.Frame(content_container)
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Show welcome content initially
        self._show_welcome_content()
    
    def _create_status_bar(self):
        """Create the status bar at the bottom"""
        status_frame = ttk.Frame(self.root, relief=tk.SUNKEN, borderwidth=1)
        status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.status_label = ttk.Label(
            status_frame, 
            text="Ready - Welcome to Z.E.U.S.",
            font=("Arial", 9)
        )
        self.status_label.pack(side=tk.LEFT, padx=5, pady=2)
        
        # Version info on the right
        version_label = ttk.Label(
            status_frame,
            text="v1.0.0",
            font=("Arial", 9),
            foreground="#666666"
        )
        version_label.pack(side=tk.RIGHT, padx=5, pady=2)
    
    def setup_navigation(self):
        """Setup navigation behavior and keyboard shortcuts"""
        # Basic navigation is now handled by KeyboardShortcutManager
        pass
    
    def setup_ui_enhancements(self):
        """Setup UI enhancements including keyboard navigation and accessibility"""
        # Setup keyboard navigation
        setup_keyboard_navigation(self.root)
        
        # Setup accessibility features
        setup_accessibility_features(self.root)
        
        # Add responsive layout callback
        self.layout_manager.add_resize_callback(self._on_responsive_resize)
        
        # Setup context-specific shortcuts when interfaces are created
        # This will be called when each interface is initialized
    
    def switch_to_chat(self):
        """Switch to chat mode"""
        if self.current_mode == "chat":
            return
        
        # Switch context in context manager
        self.context_manager.switch_context(ContextType.GENERAL)
        
        self.current_mode = "chat"
        self._update_navigation_state()
        self._clear_content()
        self._show_chat_placeholder()
        self.update_status("Chat mode - Ready for conversation")
    
    def switch_to_documents(self):
        """Switch to documents mode"""
        if self.current_mode == "documents":
            return
        
        # Switch context in context manager
        self.context_manager.switch_context(ContextType.DOCUMENT)
        
        self.current_mode = "documents"
        self._update_navigation_state()
        self._clear_content()
        self._show_documents_placeholder()
        self.update_status("Documents mode - Upload documents for analysis")
    
    def switch_to_games(self):
        """Switch to games mode"""
        if self.current_mode == "games":
            return
        
        # Switch context in context manager
        self.context_manager.switch_context(ContextType.GAME)
        
        self.current_mode = "games"
        self._update_navigation_state()
        self._clear_content()
        self._show_games_placeholder()
        self.update_status("Games mode - Choose a game to play")
    
    def _update_navigation_state(self):
        """Update navigation button states to show active mode"""
        # Reset all buttons to normal style
        for button in self.nav_buttons.values():
            button.configure(style='Nav.TButton')
        
        # Highlight active button
        if self.current_mode in self.nav_buttons:
            self.nav_buttons[self.current_mode].configure(style='NavActive.TButton')
    
    def _clear_content(self):
        """Clear the current content area"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    
    def _show_welcome_content(self):
        """Show welcome content"""
        welcome_frame = ttk.Frame(self.content_frame)
        welcome_frame.pack(expand=True)
        
        # Welcome title
        welcome_title = ttk.Label(
            welcome_frame,
            text="Welcome to Z.E.U.S.",
            font=("Arial", 24, "bold"),
            foreground="#0078d4"
        )
        welcome_title.pack(pady=(50, 10))
        
        # Subtitle
        subtitle = ttk.Label(
            welcome_frame,
            text="Zero-cost Enhanced User Support",
            font=("Arial", 14),
            foreground="#666666"
        )
        subtitle.pack(pady=(0, 30))
        
        # Description
        description = ttk.Label(
            welcome_frame,
            text="Your offline AI assistant for chat, document analysis, and interactive games.\n"
                 "Choose a feature from the sidebar to get started.",
            font=("Arial", 12),
            justify=tk.CENTER
        )
        description.pack(pady=20)
        
        # Quick start buttons
        quick_start_frame = ttk.Frame(welcome_frame)
        quick_start_frame.pack(pady=30)
        
        ttk.Button(
            quick_start_frame,
            text="Start Chatting",
            command=self.switch_to_chat,
            style='Nav.TButton'
        ).pack(side=tk.LEFT, padx=10)
        
        ttk.Button(
            quick_start_frame,
            text="Analyze Documents",
            command=self.switch_to_documents,
            style='Nav.TButton'
        ).pack(side=tk.LEFT, padx=10)
        
        ttk.Button(
            quick_start_frame,
            text="Play Games",
            command=self.switch_to_games,
            style='Nav.TButton'
        ).pack(side=tk.LEFT, padx=10)
    
    def _show_chat_placeholder(self):
        """Show chat interface with error handling"""
        try:
            from .chat_interface import ChatInterface
            from core.ai_engine import AIEngine
            
            # Initialize AI engine if not already done
            if not hasattr(self, 'ai_engine'):
                self.ai_engine = AIEngine(
                    context_manager=self.context_manager,
                    error_handler=self.error_handler
                )
                # Try to load models in background with progress indication
                import threading
                def load_models():
                    try:
                        success = self.ai_engine.load_models(show_progress=True)
                        if success:
                            self.update_status("AI models loaded successfully")
                        else:
                            self.update_status("Running in basic mode - AI models not available")
                    except Exception as e:
                        self.error_handler.handle_error(
                            e, ErrorCategory.AI_MODEL, ErrorSeverity.WARNING,
                            custom_message="Failed to load AI models. Running in basic mode.",
                            show_dialog=False
                        )
                        self.update_status("Running in basic mode")
                
                threading.Thread(target=load_models, daemon=True).start()
            
            # Create chat interface with error handler
            self.chat_interface = ChatInterface(
                self.content_frame, 
                self.ai_engine, 
                self.context_manager,
                self.error_handler
            )
            
            # Setup chat-specific keyboard shortcuts
            setup_chat_shortcuts(self.keyboard_manager, self.chat_interface)
            self.keyboard_manager.set_context("chat")
            
            # Set up message callback for status updates
            def on_message_event(event_type, data):
                if event_type == "ai_response":
                    self.update_status("Response generated")
                elif event_type == "error":
                    self.update_status(f"Error: {data}")
            
            self.chat_interface.set_message_callback(on_message_event)
            
        except Exception as e:
            self.error_handler.handle_error(
                e, ErrorCategory.SYSTEM, ErrorSeverity.ERROR,
                custom_message="Failed to initialize chat interface. Please try restarting the application."
            )
            # Show error placeholder
            self._show_error_placeholder("Chat interface unavailable")
    
    def _show_documents_placeholder(self):
        """Show documents interface with error handling"""
        try:
            from .document_viewer import DocumentViewer
            from core.document_processor import DocumentProcessor
            
            # Initialize document processor if not already done
            if not hasattr(self, 'document_processor'):
                self.document_processor = DocumentProcessor(error_handler=self.error_handler)
            
            # Create document viewer
            self.document_viewer = DocumentViewer(self.content_frame, self.document_processor)
            
            # Setup document-specific keyboard shortcuts
            setup_document_shortcuts(self.keyboard_manager, self.document_viewer)
            self.keyboard_manager.set_context("documents")
            
            # Set up document event callback for status updates
            def on_document_event(event_type, data):
                try:
                    if event_type == "document_loaded":
                        self.update_status(f"Document '{data.filename}' loaded and ready for analysis")
                        
                        # Set document context in context manager
                        self.context_manager.set_document_context(data, data.chunks)
                        
                        # If chat interface exists, update it
                        if hasattr(self, 'chat_interface'):
                            self.chat_interface.set_document_context(data.chunks, data.filename)
                            self.chat_interface.set_conversation_mode("document")
                        
                        # If AI engine exists, set document context
                        if hasattr(self, 'ai_engine'):
                            self.ai_engine.set_document_context(data, data.chunks)
                            
                    elif event_type == "document_cleared":
                        self.update_status(f"Document '{data}' cleared")
                        
                        # Clear document context from context manager
                        self.context_manager.clear_context(ContextType.DOCUMENT)
                        
                        # Clear document context from chat if exists
                        if hasattr(self, 'chat_interface'):
                            self.chat_interface.clear_document_context()
                            self.chat_interface.set_conversation_mode("general")
                        
                        # Clear from AI engine
                        if hasattr(self, 'ai_engine'):
                            self.ai_engine.clear_context(ContextType.DOCUMENT)
                            
                    elif event_type == "error":
                        self.update_status(f"Document error: {data}")
                        
                except Exception as e:
                    self.error_handler.handle_error(
                        e, ErrorCategory.DOCUMENT, ErrorSeverity.ERROR,
                        custom_message="Error handling document event.",
                        show_dialog=False
                    )
            
            self.document_viewer.set_document_callback(on_document_event)
            
        except Exception as e:
            self.error_handler.handle_error(
                e, ErrorCategory.SYSTEM, ErrorSeverity.ERROR,
                custom_message="Failed to initialize document interface. Please try restarting the application."
            )
            # Show error placeholder
            self._show_error_placeholder("Document interface unavailable")
    
    def _show_games_placeholder(self):
        """Show games interface with GameManager and error handling"""
        try:
            from games.game_manager import GameManager
            
            # Initialize game manager if not already done
            if not hasattr(self, 'game_manager'):
                self.game_manager = GameManager(self.content_frame)
                # Set up status callback for game events
                self.game_manager.set_status_callback(self.update_status)
                
                # Set up game context callback
                def on_game_event(event_type, data):
                    try:
                        if event_type == "game_started":
                            # Set game context in context manager
                            self.context_manager.set_game_context(data)
                            # Update AI engine if exists
                            if hasattr(self, 'ai_engine'):
                                self.ai_engine.set_game_context(data)
                        elif event_type == "game_ended":
                            # Clear game context
                            self.context_manager.clear_context(ContextType.GAME)
                            if hasattr(self, 'ai_engine'):
                                self.ai_engine.clear_context(ContextType.GAME)
                        elif event_type == "error":
                            self.update_status(f"Game error: {data}")
                            
                    except Exception as e:
                        self.error_handler.handle_error(
                            e, ErrorCategory.GAME, ErrorSeverity.ERROR,
                            custom_message="Error handling game event.",
                            show_dialog=False
                        )
                
                self.game_manager.set_game_callback(on_game_event)
                
                # Setup game-specific keyboard shortcuts
                setup_game_shortcuts(self.keyboard_manager, self.game_manager)
                self.keyboard_manager.set_context("games")
            else:
                # Reset to game selection if manager already exists
                self.game_manager.show_game_selection()
                self.keyboard_manager.set_context("games")
                
        except Exception as e:
            self.error_handler.handle_error(
                e, ErrorCategory.SYSTEM, ErrorSeverity.ERROR,
                custom_message="Failed to initialize games interface. Please try restarting the application."
            )
            # Show error placeholder
            self._show_error_placeholder("Games interface unavailable")
    
    def _show_help(self):
        """Show help information"""
        help_window = tk.Toplevel(self.root)
        help_window.title("Z.E.U.S. Help")
        help_window.geometry("400x300")
        help_window.resizable(False, False)
        
        # Center the help window
        help_window.transient(self.root)
        help_window.grab_set()
        
        help_text = """
Z.E.U.S. Virtual Assistant Help

Keyboard Shortcuts:
• Ctrl+1: Switch to Chat
• Ctrl+2: Switch to Documents  
• Ctrl+3: Switch to Games
• F1: Show this help

Features:
• Chat: Conversational AI assistant
• Documents: Upload and analyze PDF/DOC files
• Games: Play Tic-Tac-Toe, Connect 4, or Battleship

This application runs completely offline.
No internet connection required.
        """
        
        help_label = ttk.Label(
            help_window,
            text=help_text.strip(),
            font=("Arial", 10),
            justify=tk.LEFT
        )
        help_label.pack(padx=20, pady=20)
        
        ttk.Button(
            help_window,
            text="Close",
            command=help_window.destroy
        ).pack(pady=10)
    
    def update_status(self, message: str):
        """Update the status bar message"""
        if self.status_label:
            self.status_label.configure(text=message)
    
    def get_current_mode(self) -> str:
        """Get the current active mode"""
        return self.current_mode
    
    def get_content_frame(self) -> ttk.Frame:
        """Get the main content frame for other components to use"""
        return self.content_frame
    
    def run(self):
        """Start the application main loop"""
        self.root.mainloop()
    
    def destroy(self):
        """Clean up and destroy the window"""
        # Save context before closing
        if hasattr(self, 'context_manager'):
            self.context_manager.save_context()
        
        self.root.destroy()
    
    def _show_error_placeholder(self, error_message: str):
        """Show error placeholder when interface fails to load"""
        error_frame = ttk.Frame(self.content_frame)
        error_frame.pack(expand=True)
        
        # Error icon and message
        error_label = ttk.Label(
            error_frame,
            text="⚠️",
            font=("Arial", 48),
            foreground="#d13438"
        )
        error_label.pack(pady=(50, 20))
        
        message_label = ttk.Label(
            error_frame,
            text=error_message,
            font=("Arial", 14),
            foreground="#d13438",
            justify=tk.CENTER
        )
        message_label.pack(pady=10)
        
        # Retry button
        retry_button = ttk.Button(
            error_frame,
            text="Retry",
            command=lambda: self._retry_current_mode(),
            style='Nav.TButton'
        )
        retry_button.pack(pady=20)
    
    def _retry_current_mode(self):
        """Retry loading the current mode"""
        try:
            if self.current_mode == "chat":
                self.switch_to_chat()
            elif self.current_mode == "documents":
                self.switch_to_documents()
            elif self.current_mode == "games":
                self.switch_to_games()
        except Exception as e:
            self.error_handler.handle_error(
                e, ErrorCategory.SYSTEM, ErrorSeverity.ERROR,
                custom_message="Failed to retry loading interface."
            )
    
    def get_context_manager(self) -> ContextManager:
        """Get the context manager instance"""
        return self.context_manager
    
    def get_error_handler(self) -> ErrorHandler:
        """Get the error handler instance"""
        return self.error_handler
    
    def _on_responsive_resize(self, width: int, height: int, breakpoint):
        """Handle responsive layout changes"""
        try:
            # Update status bar with current window info for debugging
            if hasattr(self, 'status_label') and self.status_label:
                # Only show resize info briefly, then restore normal status
                current_status = self.status_label.cget('text')
                if not current_status.startswith('Resized'):
                    self.root.after(2000, lambda: self.update_status(current_status))
                    self.update_status(f"Resized to {width}x{height} ({breakpoint.value})")
        except Exception as e:
            self.logger.error(f"Error in responsive resize callback: {e}")
    
    def get_style_manager(self) -> StyleManager:
        """Get the style manager instance"""
        return self.style_manager
    
    def get_keyboard_manager(self) -> KeyboardShortcutManager:
        """Get the keyboard shortcut manager instance"""
        return self.keyboard_manager
    
    def get_layout_manager(self) -> ResponsiveLayoutManager:
        """Get the responsive layout manager instance"""
        return self.layout_manager 
   
    def setup_performance_monitoring(self):
        """Setup performance monitoring and optimization"""
        try:
            # Register optimization callbacks
            self.performance_monitor.add_optimization_callback(self._handle_performance_optimization)
            
            # Start periodic performance checks
            self._schedule_performance_check()
            
            self.logger.info("Performance monitoring setup completed")
            
        except Exception as e:
            self.logger.error(f"Error setting up performance monitoring: {e}")
    
    def _handle_performance_optimization(self, optimization_type: str, data: dict = None):
        """
        Handle performance optimization requests
        
        Args:
            optimization_type: Type of optimization
            data: Additional optimization data
        """
        try:
            if optimization_type == "memory_optimization":
                urgent = data.get('urgent', False) if data else False
                self._optimize_application_memory(urgent)
                
                # Update status
                if urgent:
                    self.update_status("Critical memory usage - optimizing performance...")
                else:
                    self.update_status("Optimizing memory usage...")
                    
            elif optimization_type == "performance_optimization":
                self._optimize_application_performance()
                self.update_status("Optimizing application performance...")
                
        except Exception as e:
            self.logger.error(f"Error handling performance optimization: {e}")
    
    def _optimize_application_memory(self, urgent: bool = False):
        """
        Optimize application memory usage
        
        Args:
            urgent: Whether this is urgent optimization
        """
        self.logger.info(f"Optimizing application memory (urgent: {urgent})")
        
        try:
            # Optimize UI components
            ui_components = []
            if hasattr(self, 'chat_interface'):
                ui_components.append(self.chat_interface)
            if hasattr(self, 'document_viewer'):
                ui_components.append(self.document_viewer)
            
            optimized_count = self.memory_optimizer.optimize_ui_memory(ui_components)
            
            # Optimize AI engine if available
            if hasattr(self, 'ai_engine'):
                self.ai_engine.optimize_memory()
            
            # Optimize document processor if available
            if hasattr(self, 'document_processor'):
                self.document_processor.optimize_storage()
            
            # Force garbage collection if urgent
            if urgent:
                self.memory_optimizer.force_garbage_collection()
            
            self.logger.info(f"Application memory optimization completed (optimized {optimized_count} components)")
            
        except Exception as e:
            self.logger.error(f"Error optimizing application memory: {e}")
    
    def _optimize_application_performance(self):
        """Optimize application performance"""
        self.logger.info("Optimizing application performance")
        
        try:
            # Clear any pending background tasks that might be slowing things down
            processor_stats = self.background_processor.get_processor_statistics()
            if processor_stats['queue_size'] > 10:
                self.logger.warning(f"High background task queue: {processor_stats['queue_size']} tasks")
            
            # Optimize context manager
            self.context_manager.save_context()  # Save current state
            
            # Update UI responsiveness
            self.root.update_idletasks()
            
            self.logger.info("Application performance optimization completed")
            
        except Exception as e:
            self.logger.error(f"Error optimizing application performance: {e}")
    
    def _schedule_performance_check(self):
        """Schedule periodic performance checks"""
        try:
            self._check_performance_status()
            
            # Schedule next check
            self.root.after(self.performance_update_interval, self._schedule_performance_check)
            
        except Exception as e:
            self.logger.error(f"Error in performance check: {e}")
            # Still schedule next check
            self.root.after(self.performance_update_interval, self._schedule_performance_check)
    
    def _check_performance_status(self):
        """Check current performance status and update UI"""
        try:
            # Get performance summary
            perf_summary = self.performance_monitor.get_performance_summary()
            
            if perf_summary.get('status') == 'no_data':
                return
            
            # Update status based on performance
            status = perf_summary.get('status', 'unknown')
            memory_percent = perf_summary.get('memory_usage_percent', 0)
            
            if status == 'critical':
                self.update_status(f"⚠️ Critical memory usage: {memory_percent:.1f}%")
            elif status == 'warning':
                self.update_status(f"⚡ High memory usage: {memory_percent:.1f}%")
            elif status == 'slow':
                avg_response = perf_summary.get('avg_response_time_ms', 0)
                self.update_status(f"🐌 Slow responses: {avg_response:.0f}ms avg")
            else:
                # Only update if we haven't updated recently to avoid spam
                current_time = time.time()
                if current_time - self.last_performance_check > 30:  # 30 seconds
                    self.update_status(f"✅ Performance good - Memory: {memory_percent:.1f}%")
                    self.last_performance_check = current_time
            
        except Exception as e:
            self.logger.error(f"Error checking performance status: {e}")
    
    def get_application_statistics(self) -> dict:
        """
        Get comprehensive application statistics
        
        Returns:
            Dictionary with application statistics
        """
        try:
            stats = {
                'performance': self.performance_monitor.get_performance_summary(),
                'memory': self.memory_optimizer.get_memory_statistics(),
                'background_processing': self.background_processor.get_processor_statistics(),
                'context': self.context_manager.get_context_summary()
            }
            
            # Add component-specific stats
            if hasattr(self, 'ai_engine'):
                stats['ai_engine'] = self.ai_engine.get_performance_metrics()
            
            if hasattr(self, 'document_processor'):
                stats['document_processor'] = self.document_processor.get_processing_statistics()
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Error getting application statistics: {e}")
            return {'error': str(e)}
    
    def export_performance_data(self, file_path: str = None) -> bool:
        """
        Export performance data to file
        
        Args:
            file_path: Path to export file (optional)
            
        Returns:
            True if successful
        """
        try:
            if file_path is None:
                from datetime import datetime
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                file_path = f"performance_data_{timestamp}.json"
            
            # Export performance metrics
            success = self.performance_monitor.export_metrics(file_path)
            
            if success:
                self.update_status(f"Performance data exported to {file_path}")
            else:
                self.update_status("Failed to export performance data")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error exporting performance data: {e}")
            self.update_status(f"Error exporting performance data: {e}")
            return False
    
    def show_performance_dialog(self):
        """Show performance statistics dialog"""
        try:
            stats_window = tk.Toplevel(self.root)
            stats_window.title("Performance Statistics")
            stats_window.geometry("600x500")
            stats_window.resizable(True, True)
            
            # Center the window
            stats_window.transient(self.root)
            stats_window.grab_set()
            
            # Create scrollable text widget
            text_frame = ttk.Frame(stats_window)
            text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            stats_text = scrolledtext.ScrolledText(
                text_frame,
                wrap=tk.WORD,
                font=("Courier", 10),
                state=tk.DISABLED
            )
            stats_text.pack(fill=tk.BOTH, expand=True)
            
            # Get and display statistics
            stats = self.get_application_statistics()
            
            stats_text.configure(state=tk.NORMAL)
            stats_text.delete("1.0", tk.END)
            
            # Format statistics
            stats_text.insert(tk.END, "Z.E.U.S. Performance Statistics\n")
            stats_text.insert(tk.END, "=" * 40 + "\n\n")
            
            for category, data in stats.items():
                stats_text.insert(tk.END, f"{category.upper()}:\n")
                if isinstance(data, dict):
                    for key, value in data.items():
                        stats_text.insert(tk.END, f"  {key}: {value}\n")
                else:
                    stats_text.insert(tk.END, f"  {data}\n")
                stats_text.insert(tk.END, "\n")
            
            stats_text.configure(state=tk.DISABLED)
            
            # Buttons
            button_frame = ttk.Frame(stats_window)
            button_frame.pack(fill=tk.X, padx=10, pady=5)
            
            ttk.Button(
                button_frame,
                text="Refresh",
                command=lambda: self._refresh_performance_dialog(stats_text)
            ).pack(side=tk.LEFT, padx=5)
            
            ttk.Button(
                button_frame,
                text="Export",
                command=self.export_performance_data
            ).pack(side=tk.LEFT, padx=5)
            
            ttk.Button(
                button_frame,
                text="Optimize Memory",
                command=lambda: self._optimize_application_memory(urgent=False)
            ).pack(side=tk.LEFT, padx=5)
            
            ttk.Button(
                button_frame,
                text="Close",
                command=stats_window.destroy
            ).pack(side=tk.RIGHT, padx=5)
            
        except Exception as e:
            self.error_handler.handle_error(
                e, ErrorCategory.SYSTEM, ErrorSeverity.ERROR,
                custom_message="Failed to show performance statistics."
            )
    
    def _refresh_performance_dialog(self, text_widget):
        """Refresh performance dialog content"""
        try:
            stats = self.get_application_statistics()
            
            text_widget.configure(state=tk.NORMAL)
            text_widget.delete("1.0", tk.END)
            
            # Format statistics
            text_widget.insert(tk.END, "Z.E.U.S. Performance Statistics (Refreshed)\n")
            text_widget.insert(tk.END, "=" * 40 + "\n\n")
            
            for category, data in stats.items():
                text_widget.insert(tk.END, f"{category.upper()}:\n")
                if isinstance(data, dict):
                    for key, value in data.items():
                        text_widget.insert(tk.END, f"  {key}: {value}\n")
                else:
                    text_widget.insert(tk.END, f"  {data}\n")
                text_widget.insert(tk.END, "\n")
            
            text_widget.configure(state=tk.DISABLED)
            
        except Exception as e:
            self.logger.error(f"Error refreshing performance dialog: {e}")
    
    def destroy(self):
        """Clean up and destroy the window"""
        try:
            # Save context before closing
            if hasattr(self, 'context_manager'):
                self.context_manager.save_context()
            
            # Stop performance monitoring
            if hasattr(self, 'performance_monitor'):
                self.performance_monitor.stop_monitoring()
            
            # Shutdown background processor
            if hasattr(self, 'background_processor'):
                self.background_processor.stop()
            
            self.root.destroy()
            
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
            self.root.destroy()