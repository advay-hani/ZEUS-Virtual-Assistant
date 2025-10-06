"""
Centralized error handling and user feedback system for Z.E.U.S. Virtual Assistant

This module provides:
- Centralized error handling with categorization
- User-friendly error messages and recovery suggestions
- Progress indicators for long-running operations
- Error logging and reporting
"""

import logging
import traceback
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Callable, Dict, Any, List
from enum import Enum
from datetime import datetime
from dataclasses import dataclass
import threading
import time


class ErrorSeverity(Enum):
    """Error severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """Error categories for better handling"""
    SYSTEM = "system"
    AI_MODEL = "ai_model"
    DOCUMENT = "document"
    GAME = "game"
    NETWORK = "network"
    FILE_IO = "file_io"
    USER_INPUT = "user_input"
    MEMORY = "memory"
    DEPENDENCY = "dependency"


@dataclass
class ErrorInfo:
    """Error information container"""
    category: ErrorCategory
    severity: ErrorSeverity
    message: str
    technical_details: str
    recovery_suggestions: List[str]
    timestamp: datetime
    context: Optional[Dict[str, Any]] = None


class ProgressIndicator:
    """Progress indicator for long-running operations"""
    
    def __init__(self, parent: tk.Widget, title: str = "Processing..."):
        self.parent = parent
        self.title = title
        self.progress_window = None
        self.progress_bar = None
        self.status_label = None
        self.cancel_callback = None
        self.is_cancelled = False
        
    def show(self, message: str = "Please wait...", indeterminate: bool = True):
        """Show progress indicator"""
        try:
            # Create progress window
            self.progress_window = tk.Toplevel(self.parent)
            self.progress_window.title(self.title)
            self.progress_window.geometry("400x150")
            self.progress_window.resizable(False, False)
            
            # Center the window
            self.progress_window.transient(self.parent.winfo_toplevel())
            self.progress_window.grab_set()
            
            # Center on parent
            parent_x = self.parent.winfo_rootx()
            parent_y = self.parent.winfo_rooty()
            parent_width = self.parent.winfo_width()
            parent_height = self.parent.winfo_height()
            
            x = parent_x + (parent_width // 2) - 200
            y = parent_y + (parent_height // 2) - 75
            self.progress_window.geometry(f"400x150+{x}+{y}")
            
            # Main frame
            main_frame = ttk.Frame(self.progress_window)
            main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
            
            # Status message
            self.status_label = ttk.Label(
                main_frame,
                text=message,
                font=("Arial", 11),
                wraplength=350
            )
            self.status_label.pack(pady=(0, 15))
            
            # Progress bar
            if indeterminate:
                self.progress_bar = ttk.Progressbar(
                    main_frame,
                    mode='indeterminate',
                    length=350
                )
                self.progress_bar.start(10)
            else:
                self.progress_bar = ttk.Progressbar(
                    main_frame,
                    mode='determinate',
                    length=350,
                    maximum=100
                )
            
            self.progress_bar.pack(pady=(0, 15))
            
            # Cancel button (optional)
            button_frame = ttk.Frame(main_frame)
            button_frame.pack()
            
            cancel_button = ttk.Button(
                button_frame,
                text="Cancel",
                command=self._on_cancel
            )
            cancel_button.pack()
            
            # Update display
            self.progress_window.update()
            
        except Exception as e:
            logging.error(f"Error showing progress indicator: {e}")
    
    def update_message(self, message: str):
        """Update progress message"""
        try:
            if self.status_label and self.progress_window:
                self.status_label.configure(text=message)
                self.progress_window.update()
        except Exception:
            pass
    
    def update_progress(self, value: int):
        """Update progress bar value (for determinate mode)"""
        try:
            if self.progress_bar and self.progress_window:
                self.progress_bar['value'] = value
                self.progress_window.update()
        except Exception:
            pass
    
    def set_cancel_callback(self, callback: Callable):
        """Set callback for cancel button"""
        self.cancel_callback = callback
    
    def _on_cancel(self):
        """Handle cancel button click"""
        self.is_cancelled = True
        if self.cancel_callback:
            self.cancel_callback()
        self.hide()
    
    def hide(self):
        """Hide progress indicator"""
        try:
            if self.progress_window:
                self.progress_window.destroy()
                self.progress_window = None
        except Exception:
            pass
    
    def is_visible(self) -> bool:
        """Check if progress indicator is visible"""
        return self.progress_window is not None and self.progress_window.winfo_exists()


class ErrorHandler:
    """Centralized error handling system"""
    
    def __init__(self, parent_widget: Optional[tk.Widget] = None):
        self.parent_widget = parent_widget
        self.logger = logging.getLogger(__name__)
        self.error_history: List[ErrorInfo] = []
        self.max_history = 100
        
        # Error message templates
        self.error_templates = {
            ErrorCategory.AI_MODEL: {
                "title": "AI Model Error",
                "icon": "⚠️",
                "default_recovery": [
                    "Try restarting the application",
                    "Check if AI dependencies are properly installed",
                    "Switch to basic mode if available"
                ]
            },
            ErrorCategory.DOCUMENT: {
                "title": "Document Processing Error",
                "icon": "📄",
                "default_recovery": [
                    "Try uploading a different document",
                    "Check if the file is corrupted",
                    "Ensure the file format is supported (PDF, DOC, DOCX)"
                ]
            },
            ErrorCategory.GAME: {
                "title": "Game Error",
                "icon": "🎮",
                "default_recovery": [
                    "Try restarting the game",
                    "Return to game selection",
                    "Check if game state is corrupted"
                ]
            },
            ErrorCategory.FILE_IO: {
                "title": "File System Error",
                "icon": "💾",
                "default_recovery": [
                    "Check file permissions",
                    "Ensure sufficient disk space",
                    "Try a different file location"
                ]
            },
            ErrorCategory.MEMORY: {
                "title": "Memory Error",
                "icon": "🧠",
                "default_recovery": [
                    "Close other applications to free memory",
                    "Restart the application",
                    "Try processing smaller files"
                ]
            },
            ErrorCategory.DEPENDENCY: {
                "title": "Dependency Error",
                "icon": "📦",
                "default_recovery": [
                    "Install missing dependencies",
                    "Check requirements.txt",
                    "Reinstall the application"
                ]
            },
            ErrorCategory.SYSTEM: {
                "title": "System Error",
                "icon": "⚙️",
                "default_recovery": [
                    "Restart the application",
                    "Check system resources",
                    "Contact support if problem persists"
                ]
            }
        }
    
    def handle_error(self, 
                    error: Exception, 
                    category: ErrorCategory,
                    severity: ErrorSeverity = ErrorSeverity.ERROR,
                    context: Optional[Dict[str, Any]] = None,
                    custom_message: Optional[str] = None,
                    custom_recovery: Optional[List[str]] = None,
                    show_dialog: bool = True) -> ErrorInfo:
        """
        Handle an error with appropriate user feedback
        
        Args:
            error: The exception that occurred
            category: Error category for classification
            severity: Error severity level
            context: Additional context information
            custom_message: Custom user-friendly message
            custom_recovery: Custom recovery suggestions
            show_dialog: Whether to show error dialog to user
            
        Returns:
            ErrorInfo object with error details
        """
        # Create error info
        error_info = ErrorInfo(
            category=category,
            severity=severity,
            message=custom_message or self._generate_user_message(error, category),
            technical_details=str(error),
            recovery_suggestions=custom_recovery or self._get_recovery_suggestions(category, error),
            timestamp=datetime.now(),
            context=context
        )
        
        # Log the error
        self._log_error(error_info, error)
        
        # Add to history
        self._add_to_history(error_info)
        
        # Show user dialog if requested
        if show_dialog and self.parent_widget:
            self._show_error_dialog(error_info)
        
        return error_info
    
    def handle_warning(self,
                      message: str,
                      category: ErrorCategory = ErrorCategory.SYSTEM,
                      context: Optional[Dict[str, Any]] = None,
                      show_dialog: bool = True) -> ErrorInfo:
        """Handle a warning message"""
        error_info = ErrorInfo(
            category=category,
            severity=ErrorSeverity.WARNING,
            message=message,
            technical_details="",
            recovery_suggestions=[],
            timestamp=datetime.now(),
            context=context
        )
        
        self._log_error(error_info)
        self._add_to_history(error_info)
        
        if show_dialog and self.parent_widget:
            self._show_warning_dialog(error_info)
        
        return error_info
    
    def _generate_user_message(self, error: Exception, category: ErrorCategory) -> str:
        """Generate user-friendly error message"""
        error_str = str(error).lower()
        
        # AI Model specific errors
        if category == ErrorCategory.AI_MODEL:
            if "model" in error_str or "transformers" in error_str:
                return "The AI model encountered an issue. The application will continue in basic mode."
            elif "memory" in error_str or "cuda" in error_str:
                return "Insufficient memory for AI processing. Try closing other applications."
            else:
                return "An AI processing error occurred. Switching to basic mode."
        
        # Document specific errors
        elif category == ErrorCategory.DOCUMENT:
            if "pdf" in error_str:
                return "Unable to process the PDF file. The file may be corrupted or password-protected."
            elif "docx" in error_str or "doc" in error_str:
                return "Unable to process the Word document. Please check the file format."
            elif "size" in error_str:
                return "The document is too large to process. Please try a smaller file."
            else:
                return "Document processing failed. Please try a different file."
        
        # File I/O errors
        elif category == ErrorCategory.FILE_IO:
            if "permission" in error_str:
                return "Permission denied. Please check file access permissions."
            elif "not found" in error_str:
                return "File not found. The file may have been moved or deleted."
            elif "space" in error_str:
                return "Insufficient disk space. Please free up some space and try again."
            else:
                return "File operation failed. Please check file permissions and try again."
        
        # Memory errors
        elif category == ErrorCategory.MEMORY:
            return "The application is running low on memory. Please close other applications and try again."
        
        # Dependency errors
        elif category == ErrorCategory.DEPENDENCY:
            return "A required component is missing. Please check the installation."
        
        # Game errors
        elif category == ErrorCategory.GAME:
            return "A game error occurred. The game will be reset."
        
        # Default system error
        else:
            return f"An unexpected error occurred: {str(error)[:100]}..."
    
    def _get_recovery_suggestions(self, category: ErrorCategory, error: Exception) -> List[str]:
        """Get recovery suggestions for error category"""
        suggestions = self.error_templates.get(category, {}).get("default_recovery", [])
        
        # Add specific suggestions based on error content
        error_str = str(error).lower()
        
        if "permission" in error_str:
            suggestions.insert(0, "Run the application as administrator")
        elif "network" in error_str or "connection" in error_str:
            suggestions.insert(0, "Check your internet connection")
        elif "memory" in error_str:
            suggestions.insert(0, "Close other applications to free memory")
        elif "disk" in error_str or "space" in error_str:
            suggestions.insert(0, "Free up disk space")
        
        return suggestions[:5]  # Limit to 5 suggestions
    
    def _log_error(self, error_info: ErrorInfo, exception: Optional[Exception] = None):
        """Log error to logging system"""
        log_message = f"[{error_info.category.value}] {error_info.message}"
        
        if error_info.context:
            log_message += f" | Context: {error_info.context}"
        
        if error_info.severity == ErrorSeverity.CRITICAL:
            self.logger.critical(log_message)
            if exception:
                self.logger.critical(traceback.format_exc())
        elif error_info.severity == ErrorSeverity.ERROR:
            self.logger.error(log_message)
            if exception:
                self.logger.error(traceback.format_exc())
        elif error_info.severity == ErrorSeverity.WARNING:
            self.logger.warning(log_message)
        else:
            self.logger.info(log_message)
    
    def _add_to_history(self, error_info: ErrorInfo):
        """Add error to history"""
        self.error_history.append(error_info)
        
        # Trim history if too long
        if len(self.error_history) > self.max_history:
            self.error_history = self.error_history[-self.max_history:]
    
    def _show_error_dialog(self, error_info: ErrorInfo):
        """Show error dialog to user"""
        try:
            template = self.error_templates.get(error_info.category, self.error_templates[ErrorCategory.SYSTEM])
            
            # Create error dialog
            dialog = tk.Toplevel(self.parent_widget)
            dialog.title(template["title"])
            dialog.geometry("500x400")
            dialog.resizable(False, False)
            
            # Center dialog
            dialog.transient(self.parent_widget.winfo_toplevel())
            dialog.grab_set()
            
            # Main frame
            main_frame = ttk.Frame(dialog)
            main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
            
            # Error icon and title
            header_frame = ttk.Frame(main_frame)
            header_frame.pack(fill=tk.X, pady=(0, 15))
            
            icon_label = ttk.Label(
                header_frame,
                text=template["icon"],
                font=("Arial", 24)
            )
            icon_label.pack(side=tk.LEFT, padx=(0, 10))
            
            title_label = ttk.Label(
                header_frame,
                text=template["title"],
                font=("Arial", 14, "bold"),
                foreground="#d13438"
            )
            title_label.pack(side=tk.LEFT, anchor=tk.W)
            
            # Error message
            message_frame = ttk.LabelFrame(main_frame, text="What happened?", padding=10)
            message_frame.pack(fill=tk.X, pady=(0, 15))
            
            message_label = ttk.Label(
                message_frame,
                text=error_info.message,
                font=("Arial", 10),
                wraplength=450,
                justify=tk.LEFT
            )
            message_label.pack(anchor=tk.W)
            
            # Recovery suggestions
            if error_info.recovery_suggestions:
                recovery_frame = ttk.LabelFrame(main_frame, text="What can you do?", padding=10)
                recovery_frame.pack(fill=tk.X, pady=(0, 15))
                
                for i, suggestion in enumerate(error_info.recovery_suggestions, 1):
                    suggestion_label = ttk.Label(
                        recovery_frame,
                        text=f"{i}. {suggestion}",
                        font=("Arial", 10),
                        wraplength=450,
                        justify=tk.LEFT
                    )
                    suggestion_label.pack(anchor=tk.W, pady=2)
            
            # Technical details (collapsible)
            if error_info.technical_details:
                details_frame = ttk.LabelFrame(main_frame, text="Technical Details", padding=10)
                details_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
                
                details_text = tk.Text(
                    details_frame,
                    height=4,
                    wrap=tk.WORD,
                    font=("Courier", 9),
                    bg="#f8f9fa",
                    fg="#333333"
                )
                details_text.pack(fill=tk.BOTH, expand=True)
                details_text.insert(tk.END, error_info.technical_details)
                details_text.configure(state=tk.DISABLED)
            
            # Buttons
            button_frame = ttk.Frame(main_frame)
            button_frame.pack(side=tk.BOTTOM)
            
            ttk.Button(
                button_frame,
                text="OK",
                command=dialog.destroy
            ).pack(side=tk.RIGHT, padx=5)
            
            ttk.Button(
                button_frame,
                text="Copy Details",
                command=lambda: self._copy_error_details(error_info)
            ).pack(side=tk.RIGHT, padx=5)
            
        except Exception as e:
            # Fallback to simple messagebox if dialog creation fails
            messagebox.showerror("Error", error_info.message)
    
    def _show_warning_dialog(self, error_info: ErrorInfo):
        """Show warning dialog to user"""
        try:
            messagebox.showwarning(
                "Warning",
                error_info.message
            )
        except Exception:
            pass
    
    def _copy_error_details(self, error_info: ErrorInfo):
        """Copy error details to clipboard"""
        try:
            details = f"Error Category: {error_info.category.value}\n"
            details += f"Severity: {error_info.severity.value}\n"
            details += f"Time: {error_info.timestamp}\n"
            details += f"Message: {error_info.message}\n"
            details += f"Technical Details: {error_info.technical_details}\n"
            
            if error_info.context:
                details += f"Context: {error_info.context}\n"
            
            # Copy to clipboard
            self.parent_widget.clipboard_clear()
            self.parent_widget.clipboard_append(details)
            
            messagebox.showinfo("Copied", "Error details copied to clipboard")
        except Exception:
            pass
    
    def get_error_history(self) -> List[ErrorInfo]:
        """Get error history"""
        return self.error_history.copy()
    
    def clear_error_history(self):
        """Clear error history"""
        self.error_history.clear()
    
    def create_progress_indicator(self, title: str = "Processing...") -> ProgressIndicator:
        """Create a progress indicator"""
        return ProgressIndicator(self.parent_widget, title)


# Decorator for automatic error handling
def handle_errors(category: ErrorCategory, 
                 severity: ErrorSeverity = ErrorSeverity.ERROR,
                 show_dialog: bool = True,
                 fallback_return=None):
    """
    Decorator for automatic error handling in methods
    
    Args:
        category: Error category
        severity: Error severity
        show_dialog: Whether to show error dialog
        fallback_return: Value to return on error
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Try to find error handler in instance
                error_handler = None
                if args and hasattr(args[0], 'error_handler'):
                    error_handler = args[0].error_handler
                
                if error_handler:
                    error_handler.handle_error(
                        e, category, severity, 
                        context={"function": func.__name__, "args": str(args[1:])},
                        show_dialog=show_dialog
                    )
                else:
                    # Fallback logging
                    logging.error(f"Error in {func.__name__}: {e}")
                
                return fallback_return
        return wrapper
    return decorator


# Context manager for progress indication
class ProgressContext:
    """Context manager for showing progress during operations"""
    
    def __init__(self, error_handler: ErrorHandler, title: str, message: str = "Processing..."):
        self.error_handler = error_handler
        self.title = title
        self.message = message
        self.progress = None
    
    def __enter__(self):
        self.progress = self.error_handler.create_progress_indicator(self.title)
        self.progress.show(self.message)
        return self.progress
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.progress:
            self.progress.hide()
        
        # Handle any exception that occurred
        if exc_type and self.error_handler:
            self.error_handler.handle_error(
                exc_val,
                ErrorCategory.SYSTEM,
                ErrorSeverity.ERROR,
                context={"operation": self.title}
            )
            return True  # Suppress the exception
        
        return False